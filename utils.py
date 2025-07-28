#!/usr/bin/env python3
"""
Funzioni di utilità per Ollama Chat GUI
Collezione di funzioni helper riutilizzabili
"""

import os
import re
import sys
import json
import hashlib
import mimetypes
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon


# ===============================
# FORMATTERS E CONVERSIONI
# ===============================

def format_timestamp(dt: Optional[datetime] = None, format_type: str = "default") -> str:
    """Formatta un timestamp in vari formati"""
    if dt is None:
        dt = datetime.now()
    
    if format_type == "default":
        return dt.strftime("%Y-%m-%d_%H-%M-%S")
    elif format_type == "display":
        return dt.strftime("%d/%m/%Y %H:%M")
    elif format_type == "time_only":
        return dt.strftime("%H:%M:%S")
    elif format_type == "date_only":
        return dt.strftime("%d/%m/%Y")
    elif format_type == "iso":
        return dt.isoformat()
    elif format_type == "filename":
        return dt.strftime("%Y%m%d_%H%M%S")
    else:
        return dt.strftime(format_type)


def format_file_size(size_bytes: int) -> str:
    """Formatta la dimensione di un file in formato leggibile"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    
    if i >= len(size_names):
        i = len(size_names) - 1
    
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """Formatta una durata in secondi in formato leggibile"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """Formatta un numero con separatori di migliaia"""
    if isinstance(number, float):
        return f"{number:,.{precision}f}"
    else:
        return f"{number:,}"


# ===============================
# STRING UTILITIES
# ===============================

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitizza un nome file rimuovendo caratteri non validi"""
    # Rimuovi caratteri non validi
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Rimuovi caratteri di controllo
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Normalizza spazi
    filename = re.sub(r'\s+', ' ', filename.strip())
    
    # Limita lunghezza
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        available_length = max_length - len(ext)
        filename = name[:available_length] + ext
    
    # Assicurati che non sia vuoto
    if not filename.strip():
        filename = f"file_{format_timestamp(format_type='filename')}"
    
    return filename


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Tronca un testo alla lunghezza massima"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_text(text: str) -> str:
    """Normalizza un testo rimuovendo diacritici e caratteri speciali"""
    # Normalizza unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Rimuovi diacritici
    text = ''.join(c for c in text if not unicodedata.combining(c))
    
    # Converti a lowercase
    text = text.lower()
    
    # Rimuovi caratteri speciali
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Normalizza spazi
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """Estrae parole chiave da un testo"""
    # Parole comuni da ignorare (stop words italiane)
    stop_words = {
        'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'di', 'a', 'da', 
        'in', 'con', 'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'se', 'che', 
        'chi', 'cui', 'come', 'quando', 'dove', 'mentre', 'quindi', 'però', 
        'anche', 'ancora', 'più', 'molto', 'tutto', 'ogni', 'alcuni', 'qualche',
        'essere', 'avere', 'fare', 'dire', 'andare', 'vedere', 'sapere', 'dare',
        'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know', 'want',
        'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here',
        'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than',
        'them', 'well', 'were'
    }
    
    # Normalizza testo
    text = normalize_text(text)
    
    # Estrai parole
    words = re.findall(r'\b\w+\b', text)
    
    # Filtra parole
    keywords = []
    word_count = {}
    
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            not word.isdigit()):
            word_count[word] = word_count.get(word, 0) + 1
    
    # Ordina per frequenza
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]


# ===============================
# FILE UTILITIES
# ===============================

def get_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """Calcola l'hash di un file"""
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def is_text_file(file_path: Union[str, Path]) -> bool:
    """Verifica se un file è di testo"""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type and mime_type.startswith('text/'):
        return True
    
    # Controlla estensioni comuni
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
        '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log', '.csv', 
        '.sql', '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore'
    }
    
    return Path(file_path).suffix.lower() in text_extensions


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Ottiene informazioni dettagliate su un file"""
    path = Path(file_path)
    
    if not path.exists():
        return {"error": "File non trovato"}
    
    stat = path.stat()
    mime_type, encoding = mimetypes.guess_type(str(path))
    
    return {
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "accessed": datetime.fromtimestamp(stat.st_atime),
        "mime_type": mime_type or "application/octet-stream",
        "encoding": encoding,
        "is_text": is_text_file(path),
        "is_hidden": path.name.startswith('.'),
        "absolute_path": str(path.absolute()),
        "parent": str(path.parent)
    }


def safe_read_file(file_path: Union[str, Path], max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """Legge un file in modo sicuro con limite di dimensione"""
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    if path.stat().st_size > max_size:
        return None
    
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    
    return None


def ensure_directory(dir_path: Union[str, Path]) -> bool:
    """Assicura che una directory esista"""
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        return False


# ===============================
# VALIDATION UTILITIES
# ===============================

def is_valid_url(url: str) -> bool:
    """Verifica se un URL è valido"""
    url_pattern = re.compile(
        r'^https?://'  # http:// o https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # porta opzionale
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def is_valid_email(email: str) -> bool:
    """Verifica se un'email è valida"""
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(email))


def validate_json(json_string: str) -> Tuple[bool, Optional[str]]:
    """Valida una stringa JSON"""
    try:
        json.loads(json_string)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)


# ===============================
# UI UTILITIES
# ===============================

def show_error_dialog(parent, title: str, message: str, details: str = None):
    """Mostra un dialog di errore"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_info_dialog(parent, title: str, message: str):
    """Mostra un dialog informativo"""
    QMessageBox.information(parent, title, message)


def show_warning_dialog(parent, title: str, message: str) -> bool:
    """Mostra un dialog di avviso con OK/Cancel"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    )
    return reply == QMessageBox.StandardButton.Ok


def show_confirmation_dialog(parent, title: str, message: str) -> bool:
    """Mostra un dialog di conferma con Yes/No"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes


def center_window(window, parent=None):
    """Centra una finestra sullo schermo o sul parent"""
    if parent:
        # Centra sul parent
        parent_geometry = parent.geometry()
        x = parent_geometry.x() + (parent_geometry.width() - window.width()) // 2
        y = parent_geometry.y() + (parent_geometry.height() - window.height()) // 2
        window.move(x, y)
    else:
        # Centra sullo schermo
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - window.width()) // 2
        y = (screen_geometry.height() - window.height()) // 2
        window.move(x, y)


def get_app_icon(size: int = 32) -> QIcon:
    """Restituisce l'icona dell'applicazione"""
    # Crea un'icona semplice se non esiste un file
    pixmap = QPixmap(size, size)
    pixmap.fill()  # Riempie di bianco
    
    # Qui potresti caricare un'icona vera da file
    # pixmap.load("path/to/icon.png")
    
    return QIcon(pixmap)


# ===============================
# SYSTEM UTILITIES
# ===============================

def get_system_info() -> Dict[str, str]:
    """Ottiene informazioni sul sistema"""
    import platform
    
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation()
    }


def is_admin() -> bool:
    """Verifica se l'applicazione è eseguita come amministratore"""
    try:
        if sys.platform == "win32":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except:
        return False


def get_available_memory() -> int:
    """Ottiene la memoria disponibile in MB"""
    try:
        import psutil
        return psutil.virtual_memory().available // (1024 * 1024)
    except ImportError:
        return 0


# ===============================
# PERFORMANCE UTILITIES
# ===============================

class Timer:
    """Utility per misurare il tempo di esecuzione"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Inizia il timer"""
        self.start_time = datetime.now()
    
    def stop(self):
        """Ferma il timer"""
        self.end_time = datetime.now()
    
    def elapsed(self) -> float:
        """Restituisce il tempo trascorso in secondi"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def elapsed_formatted(self) -> str:
        """Restituisce il tempo trascorso formattato"""
        return format_duration(self.elapsed())
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def debounce(wait_time: int):
    """Decorator per debounce di funzioni"""
    def decorator(func):
        timer = None
        
        def debounced(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
            
            if timer:
                timer.stop()
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(call_func)
            timer.start(wait_time)
        
        return debounced
    return decorator


# ===============================
# DATA UTILITIES
# ===============================

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge profondo di due dizionari"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Appiattisce un dizionario annidato"""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Divide una lista in chunk di dimensione specifica"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


# ===============================
# LOGGING UTILITIES
# ===============================

class SimpleLogger:
    """Logger semplice per debug"""
    
    def __init__(self, name: str = "OllamaChat", level: str = "INFO"):
        self.name = name
        self.level = level
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        self.current_level = self.levels.get(level, 1)
    
    def _log(self, level: str, message: str):
        if self.levels.get(level, 1) >= self.current_level:
            timestamp = format_timestamp(format_type="display")
            print(f"[{timestamp}] {level:7} {self.name}: {message}")
    
    def debug(self, message: str):
        self._log("DEBUG", message)
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)


# Istanza logger globale
logger = SimpleLogger()


# ===============================
# TESTS
# ===============================

def run_tests():
    """Esegue test delle funzioni utility"""
    print("🧪 Test funzioni utility")
    
    # Test formatters
    print(f"📅 Timestamp: {format_timestamp()}")
    print(f"💾 File size: {format_file_size(1024*1024*1.5)}")
    print(f"⏱️ Duration: {format_duration(3661)}")
    
    # Test string utilities
    dirty_filename = "File<>|?*.txt"
    clean_filename = sanitize_filename(dirty_filename)
    print(f"🧹 Sanitized: '{dirty_filename}' -> '{clean_filename}'")
    
    # Test text processing
    sample_text = "Questo è un testo di esempio per testare l'estrazione delle parole chiave."
    keywords = extract_keywords(sample_text, max_keywords=5)
    print(f"🔑 Keywords: {keywords}")
    
    # Test validation
    urls = ["http://localhost:11434", "invalid-url", "https://example.com"]
    for url in urls:
        print(f"🌐 URL '{url}' valid: {is_valid_url(url)}")
    
    # Test timer
    with Timer() as timer:
        import time
        time.sleep(0.1)
    print(f"⏱️ Timer test: {timer.elapsed_formatted()}")
    
    print("✅ Test completati!")


if __name__ == "__main__":
    run_tests()