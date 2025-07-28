#!/usr/bin/env python3
"""
Gestione progetti e knowledge base per Ollama Chat GUI - VERSIONE CORRETTA
Sistema completo di file management e ricerca con debug migliorato
"""

import os
import json
import sqlite3
import hashlib
import mimetypes
import shutil
import zipfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class FileProcessor:
    """Processore per diversi tipi di file"""
    
    @staticmethod
    def extract_text_content(file_path: Path) -> str:
        """Estrae il contenuto testuale da diversi tipi di file"""
        try:
            mime_type = mimetypes.guess_type(str(file_path))[0] or ""
            
            # File di testo e codice
            if (mime_type.startswith("text/") or 
                file_path.suffix.lower() in ['.py', '.js', '.html', '.css', '.json', 
                                              '.md', '.txt', '.xml', '.yaml', '.yml', 
                                              '.ini', '.cfg', '.conf', '.log']):
                return FileProcessor._read_text_file(file_path)
            
            # PDF
            elif file_path.suffix.lower() == '.pdf':
                return FileProcessor._extract_pdf_content(file_path)
            
            # Word documents
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return FileProcessor._extract_word_content(file_path)
            
            # Excel files
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                return FileProcessor._extract_excel_content(file_path)
            
            # Altri formati
            else:
                return f"File binario: {file_path.name} ({mime_type})"
                
        except Exception as e:
            return f"Errore nell'estrazione del contenuto: {str(e)}"
    
    @staticmethod
    def _read_text_file(file_path: Path) -> str:
        """Legge un file di testo"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # Se tutti i codifiche falliscono, leggi come binario
        with open(file_path, 'rb') as f:
            content = f.read()
            return content.decode('utf-8', errors='ignore')
    
    @staticmethod
    def _extract_pdf_content(file_path: Path) -> str:
        """Estrae contenuto da file PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            return f"File PDF: {file_path.name} (PyPDF2 non installato per l'estrazione)"
        except Exception as e:
            return f"Errore nell'estrazione PDF: {str(e)}"
    
    @staticmethod
    def _extract_word_content(file_path: Path) -> str:
        """Estrae contenuto da documenti Word"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except ImportError:
            return f"File Word: {file_path.name} (python-docx non installato)"
        except Exception as e:
            return f"Errore nell'estrazione Word: {str(e)}"
    
    @staticmethod
    def _extract_excel_content(file_path: Path) -> str:
        """Estrae contenuto da file Excel"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path, sheet_name=None)
            text = ""
            for sheet_name, sheet_data in df.items():
                text += f"=== Foglio: {sheet_name} ===\n"
                text += sheet_data.to_string() + "\n\n"
            return text.strip()
        except ImportError:
            return f"File Excel: {file_path.name} (pandas non installato)"
        except Exception as e:
            return f"Errore nell'estrazione Excel: {str(e)}"


class DatabaseManager:
    """Gestore centralizzato del database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza le tabelle del database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella progetti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings TEXT,
                knowledge_summary TEXT
            )
        """)
        
        # Tabella file
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_path TEXT,
                file_hash TEXT UNIQUE,
                mime_type TEXT,
                size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_preview TEXT,
                tags TEXT,
                project_id TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Tabella contenuti file
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_content (
                file_id INTEGER PRIMARY KEY,
                content TEXT,
                processed_content TEXT,
                embedding BLOB,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        """)
        
        # Indici per performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_modified ON projects(last_modified)")
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Esegue una query e restituisce i risultati"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
            else:
                results = cursor.lastrowid
                
            conn.commit()
            return results
        finally:
            conn.close()


class FileManager:
    """Gestore per i file del progetto"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.files_dir = self.project_dir / "files"
        self.cache_dir = self.project_dir / "cache"
        
        # Crea le directory necessarie
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Database per metadati
        db_path = self.project_dir / "files_metadata.db"
        self.db = DatabaseManager(str(db_path))
    
    def add_file(self, file_path: str, project_id: str = "default") -> Dict[str, Any]:
        """Aggiunge un file al progetto"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File non trovato: {file_path}")
            
            # Calcola hash del file
            file_hash = self._calculate_file_hash(file_path)
            
            # Verifica se il file esiste già
            existing = self.db.execute_query(
                "SELECT id FROM files WHERE file_hash = ?", (file_hash,)
            )
            if existing:
                return {"status": "exists", "hash": file_hash, "file_id": existing[0][0]}
            
            # Copia il file nella directory del progetto
            dest_filename = f"{file_hash}_{file_path.name}"
            dest_path = self.files_dir / dest_filename
            shutil.copy2(file_path, dest_path)
            
            # Estrai contenuto
            content = FileProcessor.extract_text_content(file_path)
            processed_content = self._process_content(content)
            
            # Salva metadati
            file_info = {
                "filename": file_path.name,
                "original_path": str(file_path),
                "file_hash": file_hash,
                "mime_type": mimetypes.guess_type(str(file_path))[0] or "application/octet-stream",
                "size": file_path.stat().st_size,
                "content_preview": content[:500] if content else "",
                "project_id": project_id
            }
            
            file_id = self._save_file_metadata(file_info, content, processed_content)
            
            return {
                "status": "added",
                "file_id": file_id,
                "hash": file_hash,
                "filename": file_path.name,
                "size": file_info["size"],
                "type": file_info["mime_type"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcola l'hash SHA256 del file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _process_content(self, content: str) -> str:
        """Processa il contenuto per renderlo più utilizzabile"""
        if not content:
            return ""
        
        # Rimuovi caratteri di controllo
        processed = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
        
        # Normalizza spazi bianchi
        lines = [line.strip() for line in processed.split('\n')]
        processed = '\n'.join(line for line in lines if line)
        
        return processed
    
    def _save_file_metadata(self, file_info: Dict[str, Any], 
                           content: str, processed_content: str) -> int:
        """Salva i metadati del file nel database"""
        # Inserisci metadati file
        file_id = self.db.execute_query("""
            INSERT INTO files (filename, original_path, file_hash, mime_type, 
                              size, content_preview, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            file_info["filename"],
            file_info["original_path"],
            file_info["file_hash"],
            file_info["mime_type"],
            file_info["size"],
            file_info["content_preview"],
            file_info["project_id"]
        ))
        
        # Inserisci contenuto
        self.db.execute_query("""
            INSERT INTO file_content (file_id, content, processed_content)
            VALUES (?, ?, ?)
        """, (file_id, content, processed_content))
        
        return file_id
    
    def get_files(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Recupera la lista dei file del progetto"""
        print(f"DEBUG get_files: project_id = {project_id}")
        print(f"DEBUG get_files: database path = {self.db.db_path}")
        
        # Prima controlla se il database esiste
        if not os.path.exists(self.db.db_path):
            print(f"DEBUG: Database file does not exist at {self.db.db_path}")
            return []
            
        if project_id:
            query = """
                SELECT id, filename, file_hash, mime_type, size, created_at, content_preview
                FROM files WHERE project_id = ?
                ORDER BY created_at DESC
            """
            params = (project_id,)
        else:
            query = """
                SELECT id, filename, file_hash, mime_type, size, created_at, content_preview
                FROM files ORDER BY created_at DESC
            """
            params = None
        
        results = self.db.execute_query(query, params)
        print(f"DEBUG get_files: query = {query}")
        print(f"DEBUG get_files: params = {params}")  
        print(f"DEBUG get_files: raw results = {results}")
        
        files = []
        for row in results:
            files.append({
                "id": row[0],
                "filename": row[1],
                "hash": row[2],
                "type": row[3],
                "size": row[4],
                "created_at": row[5],
                "preview": row[6]
            })
        
        return files
    
    def get_file_content(self, file_id: int) -> Optional[str]:
        """Recupera il contenuto completo di un file"""
        results = self.db.execute_query(
            "SELECT content FROM file_content WHERE file_id = ?", (file_id,)
        )
        return results[0][0] if results else None
    
    def search_in_files(self, query: str, project_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Cerca nei contenuti dei file - VERSIONE CORRETTA"""
        print(f"DEBUG search_in_files: query='{query}', project_id='{project_id}', limit={limit}")
        
        # Debug: verifica contenuti
        content_check = self.db.execute_query("""
            SELECT f.id, f.filename, LENGTH(fc.content) as content_length, 
                   LENGTH(fc.processed_content) as processed_length
            FROM files f 
            LEFT JOIN file_content fc ON f.id = fc.file_id 
            WHERE f.project_id = ?
        """, (project_id,))
        print(f"DEBUG: File content check: {content_check}")
        
        # Se non c'è query, restituisci tutti i file
        if not query or not query.strip():
            print("DEBUG: Empty query, returning all files")
            return []
        
        search_query = f"%{query.lower()}%"
        
        if project_id:
            sql_query = """
                SELECT f.id, f.filename, f.mime_type, fc.processed_content,
                       f.content_preview, f.size
                FROM files f
                LEFT JOIN file_content fc ON f.id = fc.file_id
                WHERE f.project_id = ? AND (
                    LOWER(f.filename) LIKE ? OR 
                    LOWER(COALESCE(fc.processed_content, '')) LIKE ? OR
                    LOWER(COALESCE(fc.content, '')) LIKE ?
                )
                ORDER BY 
                    CASE WHEN LOWER(f.filename) LIKE ? THEN 1 ELSE 2 END,
                    f.created_at DESC
                LIMIT ?
            """
            params = (project_id, search_query, search_query, search_query, search_query, limit)
        else:
            sql_query = """
                SELECT f.id, f.filename, f.mime_type, fc.processed_content,
                       f.content_preview, f.size
                FROM files f
                LEFT JOIN file_content fc ON f.id = fc.file_id
                WHERE LOWER(f.filename) LIKE ? OR 
                      LOWER(COALESCE(fc.processed_content, '')) LIKE ? OR
                      LOWER(COALESCE(fc.content, '')) LIKE ?
                ORDER BY 
                    CASE WHEN LOWER(f.filename) LIKE ? THEN 1 ELSE 2 END,
                    f.created_at DESC
                LIMIT ?
            """
            params = (search_query, search_query, search_query, search_query, limit)
        
        print(f"DEBUG: SQL Query: {sql_query}")
        print(f"DEBUG: Params: {params}")
        
        results = self.db.execute_query(sql_query, params)
        print(f"DEBUG: Search results: {len(results) if results else 0} items")
        
        search_results = []
        for row in results:
            # Trova snippet rilevanti
            content = (row[3] or "").lower()
            query_lower = query.lower()
            
            snippet = ""
            if query_lower in content:
                index = content.find(query_lower)
                start = max(0, index - 100)
                end = min(len(content), index + 200)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
            elif content:  # Se non trova la query, prendi l'inizio del contenuto
                snippet = content[:300] + "..." if len(content) > 300 else content
            
            search_results.append({
                "file_id": row[0],
                "filename": row[1],
                "type": row[2],
                "snippet": snippet,
                "preview": row[4],
                "size": row[5]
            })
        
        print(f"DEBUG: Returning {len(search_results)} search results")
        return search_results
    
    def delete_file(self, file_id: int) -> bool:
        """Elimina un file dal progetto"""
        try:
            # Ottieni info file
            file_info = self.db.execute_query(
                "SELECT file_hash, filename FROM files WHERE id = ?", (file_id,)
            )
            
            if not file_info:
                return False
            
            file_hash, filename = file_info[0]
            
            # Elimina file fisico
            file_path = self.files_dir / f"{file_hash}_{filename}"
            if file_path.exists():
                file_path.unlink()
            
            # Elimina dal database
            self.db.execute_query("DELETE FROM file_content WHERE file_id = ?", (file_id,))
            self.db.execute_query("DELETE FROM files WHERE id = ?", (file_id,))
            
            return True
        except Exception:
            return False


class ProjectManager:
    """Gestore principale dei progetti"""
    
    def __init__(self, projects_dir: str):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Database progetti
        db_path = self.projects_dir / "projects.db"
        self.db = DatabaseManager(str(db_path))
    
    def create_project(self, name: str, description: str = "") -> str:
        """Crea un nuovo progetto"""
        project_id = f"proj_{int(time.time())}_{hash(name) % 10000}"
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Salva nel database
        self.db.execute_query("""
            INSERT INTO projects (id, name, description, settings)
            VALUES (?, ?, ?, ?)
        """, (project_id, name, description, json.dumps({})))
        
        return project_id
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Recupera tutti i progetti"""
        results = self.db.execute_query("""
            SELECT id, name, description, created_at, last_modified
            FROM projects ORDER BY last_modified DESC
        """)
        
        projects = []
        for row in results:
            projects.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "last_modified": row[4]
            })
        
        return projects
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Recupera un progetto specifico"""
        results = self.db.execute_query("""
            SELECT id, name, description, created_at, last_modified, settings, knowledge_summary
            FROM projects WHERE id = ?
        """, (project_id,))
        
        if results:
            row = results[0]
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "last_modified": row[4],
                "settings": json.loads(row[5] or "{}"),
                "knowledge_summary": row[6]
            }
        return None
    
    def update_project(self, project_id: str, **kwargs):
        """Aggiorna un progetto"""
        allowed_fields = ['name', 'description', 'settings', 'knowledge_summary']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'settings' and isinstance(value, dict):
                    value = json.dumps(value)
                updates.append(f"{field} = ?")
                params.append(value)
        
        if updates:
            params.append(project_id)
            query = f"""
                UPDATE projects 
                SET {', '.join(updates)}, last_modified = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            self.db.execute_query(query, tuple(params))
    
    def delete_project(self, project_id: str) -> bool:
        """Elimina un progetto"""
        try:
            # Elimina directory
            project_dir = self.projects_dir / project_id
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            # Elimina dal database
            self.db.execute_query("DELETE FROM projects WHERE id = ?", (project_id,))
            
            return True
        except Exception:
            return False
    
    def export_project(self, project_id: str, export_path: str) -> bool:
        """Esporta un progetto in un file ZIP"""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                return False
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_dir)
                        zipf.write(file_path, arcname)
            
            return True
        except Exception:
            return False
    
    def import_project(self, zip_path: str) -> Optional[str]:
        """Importa un progetto da un file ZIP"""
        try:
            # Genera nuovo ID progetto
            project_id = f"proj_import_{int(time.time())}"
            project_dir = self.projects_dir / project_id
            project_dir.mkdir(exist_ok=True)
            
            # Estrai ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(project_dir)
            
            # Leggi metadati se disponibili
            metadata_file = project_dir / "project_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                # Inserisci nel database
                self.db.execute_query("""
                    INSERT INTO projects (id, name, description, settings)
                    VALUES (?, ?, ?, ?)
                """, (
                    project_id,
                    metadata.get('name', 'Progetto Importato'),
                    metadata.get('description', ''),
                    json.dumps(metadata.get('settings', {}))
                ))
            
            return project_id
        except Exception:
            return None
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Ottiene statistiche di un progetto"""
        file_manager = FileManager(str(self.projects_dir / project_id))
        files = file_manager.get_files(project_id)
        
        total_size = sum(f['size'] for f in files)
        file_types = {}
        
        for file_info in files:
            file_type = file_info['type'].split('/')[0] if '/' in file_info['type'] else 'altro'
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'file_types': file_types,
            'last_activity': max([f['created_at'] for f in files]) if files else None
        }


class KnowledgeBase:
    """Sistema di knowledge base con ricerca avanzata - VERSIONE CORRETTA"""
    
    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager
    
    def search_across_projects(self, query: str, project_ids: List[str] = None, 
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Cerca attraverso tutti i progetti o solo quelli specificati"""
        if not project_ids:
            projects = self.project_manager.get_projects()
            project_ids = [p['id'] for p in projects]
        
        all_results = []
        
        for project_id in project_ids:
            project_dir = self.project_manager.projects_dir / project_id
            if project_dir.exists():
                file_manager = FileManager(str(project_dir))
                results = file_manager.search_in_files(query, project_id, limit // len(project_ids))
                
                # Aggiungi info progetto ai risultati
                project_info = self.project_manager.get_project(project_id)
                for result in results:
                    result['project_name'] = project_info['name'] if project_info else 'Sconosciuto'
                    result['project_id'] = project_id
                
                all_results.extend(results)
        
        # Ordina per rilevanza (i file nel nome hanno priorità)
        all_results.sort(key=lambda x: (
            0 if query.lower() in x['filename'].lower() else 1,
            -len(x['snippet'])
        ))
        
        return all_results[:limit]
    
    def generate_project_summary(self, project_id: str, max_files: int = 10) -> str:
        """Genera un riassunto della knowledge base del progetto"""
        project = self.project_manager.get_project(project_id)
        if not project:
            return "Progetto non trovato"
        
        stats = self.project_manager.get_project_statistics(project_id)
        
        summary = f"📊 Riassunto Knowledge Base - {project['name']}\n\n"
        summary += f"📁 File totali: {stats['total_files']}\n"
        summary += f"💾 Dimensione totale: {self._format_size(stats['total_size'])}\n\n"
        
        if stats['file_types']:
            summary += "📋 Tipi di file:\n"
            for file_type, count in stats['file_types'].items():
                summary += f"  • {file_type}: {count} file\n"
            summary += "\n"
        
        # Elenca alcuni file recenti
        project_dir = self.project_manager.projects_dir / project_id
        if project_dir.exists():
            file_manager = FileManager(str(project_dir))
            recent_files = file_manager.get_files(project_id)[:max_files]
            
            if recent_files:
                summary += f"📄 File recenti (ultimi {min(len(recent_files), max_files)}):\n"
                for file_info in recent_files:
                    summary += f"  • {file_info['filename']} ({self._format_size(file_info['size'])})\n"
                summary += "\n"
        
        summary += f"🕒 Ultimo aggiornamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary
    
    def get_context_for_query(self, query: str, project_id: str, 
                             max_context_length: int = 2000) -> str:
        """Ottiene il contesto dalla knowledge base per una query - VERSIONE CORRETTA"""
        print(f"DEBUG get_context_for_query: query='{query[:50]}...', project_id='{project_id}', max_length={max_context_length}")
        
        project_dir = self.project_manager.projects_dir / project_id
        if not project_dir.exists():
            print(f"DEBUG: Project directory does not exist: {project_dir}")
            return ""
        
        file_manager = FileManager(str(project_dir))
        
        # Cerca in base alla query - usa una ricerca più ampia
        search_terms = query.split()[:3]  # Prendi le prime 3 parole
        search_results = []
        
        # Prova con termini singoli se la query completa non trova nulla
        for term in [query] + search_terms:
            if len(term) > 2:  # Ignora parole troppo corte
                results = file_manager.search_in_files(term.strip(), project_id, 3)
                search_results.extend(results)
                if results:  # Se trova qualcosa, fermati
                    break
        
        # Rimuovi duplicati
        seen_ids = set()
        unique_results = []
        for result in search_results:
            if result['file_id'] not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result['file_id'])
        
        print(f"DEBUG: Found {len(unique_results)} unique search results")
        
        if not unique_results:
            # Se non trova nulla con la ricerca, prendi i primi file disponibili
            print("DEBUG: No search results, getting all files")
            all_files = file_manager.get_files(project_id)
            if all_files:
                # Converti in formato search_results
                for file_info in all_files[:2]:  # Prendi i primi 2 file
                    content = file_manager.get_file_content(file_info['id'])
                    if content and len(content.strip()) > 10:
                        unique_results.append({
                            'file_id': file_info['id'],
                            'filename': file_info['filename'],
                            'type': file_info['type'],
                            'snippet': content[:200] + "..." if len(content) > 200 else content,
                            'preview': file_info.get('preview', ''),
                            'size': file_info['size']
                        })
        
        if not unique_results:
            print("DEBUG: No content found in any files")
            return ""
        
        # Costruisci il contesto
        context = "CONTESTO DALLA KNOWLEDGE BASE:\n\n"
        current_length = len(context)
        
        for result in unique_results[:3]:  # Massimo 3 file
            if current_length >= max_context_length:
                break
            
            print(f"DEBUG: Processing file {result['filename']} (ID: {result['file_id']})")
            file_content = file_manager.get_file_content(result['file_id'])
            
            if file_content and len(file_content.strip()) > 10:
                file_header = f"=== FILE: {result['filename']} ===\n"
                
                # Estrai la parte più rilevante del contenuto
                content_snippet = self._extract_relevant_snippet(
                    file_content, query, min(800, max_context_length - current_length - len(file_header) - 10)
                )
                
                addition = file_header + content_snippet + "\n\n"
                
                if current_length + len(addition) <= max_context_length:
                    context += addition
                    current_length += len(addition)
                    print(f"DEBUG: Added {len(addition)} chars from {result['filename']}")
                else:
                    remaining = max_context_length - current_length
                    if remaining > 100:  # Solo se c'è spazio sufficiente per contenuto utile
                        context += addition[:remaining] + "...\n\n"
                        print(f"DEBUG: Added truncated {remaining} chars from {result['filename']}")
                    break
        
        final_context = context.strip()
        print(f"DEBUG: Final context length: {len(final_context)}")
        print(f"DEBUG: Context preview: {final_context[:200]}...")
        
        return final_context
    
    def _extract_relevant_snippet(self, content: str, query: str, max_length: int) -> str:
        """Estrae uno snippet rilevante dal contenuto"""
        if max_length <= 0:
            return ""
            
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Trova la prima occorrenza della query o delle sue parole
        query_words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
        best_index = -1
        
        # Cerca la query completa prima
        index = content_lower.find(query_lower)
        if index != -1:
            best_index = index
        else:
            # Cerca le singole parole
            for word in query_words:
                index = content_lower.find(word)
                if index != -1:
                    best_index = index
                    break
        
        if best_index == -1:
            # Se non trova nulla, prendi l'inizio
            snippet = content[:max_length]
        else:
            # Centra lo snippet attorno alla posizione trovata
            start = max(0, best_index - max_length // 3)
            end = min(len(content), start + max_length)
            snippet = content[start:end]
            
            # Aggiungi ellipsis se necessario
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
        
        return snippet
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatta la dimensione in formato leggibile"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        elif size_bytes < 1024**4:
            return f"{size_bytes/(1024**3):.1f} GB"
        elif size_bytes < 1024**5:
            return f"{size_bytes/(1024**3):.1f} TB"
        elif size_bytes < 1024**6:
            return f"{size_bytes/(1024**3):.1f} PB"
        elif size_bytes < 1024**7:
            return f"{size_bytes/(1024**3):.1f} EB"
        elif size_bytes < 1024**8:
            return f"{size_bytes/(1024**3):.1f} ZB"
        elif size_bytes < 1024**9:
            return f"{size_bytes/(1024**3):.1f} YB"
        