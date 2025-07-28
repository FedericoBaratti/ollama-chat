#!/usr/bin/env python3
"""
Configurazione dell'applicazione Ollama Chat GUI
Gestione centralizzata delle impostazioni e configurazioni
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QStandardPaths


class AppConfig:
    """Configurazione dell'applicazione"""
    
    # Informazioni applicazione
    APP_NAME = "Ollama Chat"
    APP_VERSION = "1.0"
    APP_AUTHOR = "Baratti Federico"
    APP_DESCRIPTION = "GUI avanzata per Ollama con Knowledge Base"
    
    # Directory e percorsi
    @staticmethod
    def get_app_data_dir() -> Path:
        """Restituisce la directory dei dati dell'applicazione"""
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )) / "OllamaChat"
    
    @staticmethod
    def get_config_dir() -> Path:
        """Restituisce la directory di configurazione"""
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.ConfigLocation
        )) / "OllamaChat"
    
    @staticmethod
    def get_documents_dir() -> Path:
        """Restituisce la directory dei documenti"""
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )) / "OllamaChat"
    
    @staticmethod
    def get_cache_dir() -> Path:
        """Restituisce la directory della cache"""
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.CacheLocation
        )) / "OllamaChat"
    
    # Impostazioni di default
    DEFAULT_SETTINGS = {
        # Server Ollama
        "server_url": "http://localhost:11434",
        "connection_timeout": 15,  # AUMENTATO da 10 a 15 secondi
        "read_timeout": 120,       # NUOVO: timeout separato per lettura stream (2 minuti)
        "request_timeout": 30,     # Mantenuto per compatibilità
        "auto_refresh_models": True,
        "check_connection_interval": 30,
        "max_retries": 3,          # NUOVO: numero massimo di tentativi
        
        # Interfaccia utente
        "theme": "modern",
        "font_family": "Segoe UI",
        "font_size": 11,
        "show_timestamps": True,
        "animations": True,
        "smart_scroll": True,
        "window_width": 1400,
        "window_height": 900,
        "maximize_startup": False,
        "sidebar_width": 320,
        
        # Chat e messaggi
        "max_messages": 200,
        "stream_buffer_size": 50,
        "typing_indicator_delay": 500,
        "message_animation_duration": 200,
        "auto_scroll_threshold": 100,
        
        # Knowledge Base
        "use_knowledge": True,
        "knowledge_context_length": 2000,
        "max_search_results": 10,
        "search_snippet_length": 200,
        "auto_generate_summaries": True,
        "enable_file_preview": True,
        
        # File management
        "supported_file_types": [
            "txt", "md", "py", "js", "html", "css", "json", "xml", "yaml", "yml",
            "pdf", "docx", "doc", "xlsx", "xls", "csv"
        ],
        "max_file_size_mb": 50,
        "extract_file_content": True,
        "auto_backup_projects": True,
        
        # Export e salvataggio
        "default_export_format": "json",
        "export_directory": "",
        "include_timestamps": True,
        "include_model_info": True,
        "include_project_info": True,
        "autosave_enabled": False,
        "autosave_interval_minutes": 5,
        
        # Prestazioni
        "enable_logging": False,
        "log_level": "INFO",
        "detailed_errors": False,
        "memory_limit_mb": 512,
        "cleanup_interval_hours": 24,
        
        # Sicurezza
        "validate_file_types": True,
        "scan_for_malware": False,
        "restrict_file_access": True,
        "enable_sandboxing": False,
        
        # Avanzate
        "experimental_features": False,
        "debug_mode": False,
        "verbose_logging": False,
        "performance_monitoring": False
    }
    
    # Valori di validazione
    VALIDATION_RULES = {
        "server_url": {
            "type": str,
            "pattern": r"^https?://.*",
            "required": True
        },
        "connection_timeout": {
            "type": int,
            "min": 1,
            "max": 60
        },
        "request_timeout": {
            "type": int,
            "min": 5,
            "max": 300
        },
        "font_size": {
            "type": int,
            "min": 8,
            "max": 24
        },
        "max_messages": {
            "type": int,
            "min": 10,
            "max": 1000
        },
        "knowledge_context_length": {
            "type": int,
            "min": 100,
            "max": 10000
        },
        "window_width": {
            "type": int,
            "min": 800,
            "max": 4000
        },
        "window_height": {
            "type": int,
            "min": 600,
            "max": 3000
        }
    }
    
    @classmethod
    def validate_setting(cls, key: str, value: Any) -> bool:
        """Valida un'impostazione"""
        if key not in cls.VALIDATION_RULES:
            return True  # Se non ci sono regole, accetta
        
        rules = cls.VALIDATION_RULES[key]
        
        # Controlla tipo
        if "type" in rules and not isinstance(value, rules["type"]):
            return False
        
        # Controlla pattern (per stringhe)
        if "pattern" in rules and isinstance(value, str):
            import re
            if not re.match(rules["pattern"], value):
                return False
        
        # Controlla range (per numeri)
        if isinstance(value, (int, float)):
            if "min" in rules and value < rules["min"]:
                return False
            if "max" in rules and value > rules["max"]:
                return False
        
        return True
    
    @classmethod
    def get_setting_description(cls, key: str) -> str:
        """Restituisce la descrizione di un'impostazione"""
        descriptions = {
            "server_url": "URL del server Ollama",
            "connection_timeout": "Timeout per la connessione (secondi)",
            "request_timeout": "Timeout per le richieste (secondi)",
            "auto_refresh_models": "Aggiorna automaticamente i modelli all'avvio",
            "theme": "Tema dell'interfaccia",
            "font_size": "Dimensione del font",
            "show_timestamps": "Mostra timestamp nei messaggi",
            "animations": "Abilita animazioni",
            "max_messages": "Numero massimo di messaggi in conversazione",
            "use_knowledge": "Utilizza la knowledge base nelle risposte",
            "knowledge_context_length": "Lunghezza massima del contesto (caratteri)",
            "window_width": "Larghezza finestra",
            "window_height": "Altezza finestra"
        }
        return descriptions.get(key, f"Impostazione: {key}")


def get_settings_file_path() -> Path:
    """Restituisce il percorso del file delle impostazioni"""
    config_dir = AppConfig.get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def load_user_settings() -> Dict[str, Any]:
    """Carica le impostazioni utente"""
    settings_file = get_settings_file_path()
    
    # Inizia con le impostazioni di default
    settings = AppConfig.DEFAULT_SETTINGS.copy()
    
    # Carica impostazioni salvate se esistono
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                
                # Valida e merge le impostazioni
                for key, value in user_settings.items():
                    if key in AppConfig.DEFAULT_SETTINGS:
                        if AppConfig.validate_setting(key, value):
                            settings[key] = value
                        else:
                            print(f"⚠️ Impostazione non valida ignorata: {key}={value}")
        
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"⚠️ Errore nel caricamento delle impostazioni: {e}")
            print("📝 Utilizzo impostazioni di default")
    
    return settings


def save_user_settings(settings: Dict[str, Any]) -> bool:
    """Salva le impostazioni utente"""
    settings_file = get_settings_file_path()
    
    try:
        # Crea directory se non esiste
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Filtra solo impostazioni valide
        valid_settings = {}
        for key, value in settings.items():
            if key in AppConfig.DEFAULT_SETTINGS:
                if AppConfig.validate_setting(key, value):
                    valid_settings[key] = value
                else:
                    print(f"⚠️ Impostazione non valida non salvata: {key}={value}")
        
        # Salva su file
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(valid_settings, f, indent=2, ensure_ascii=False)
        
        return True
        
    except (PermissionError, OSError) as e:
        print(f"❌ Errore nel salvataggio delle impostazioni: {e}")
        return False


def reset_user_settings() -> bool:
    """Ripristina le impostazioni di default"""
    try:
        settings_file = get_settings_file_path()
        if settings_file.exists():
            settings_file.unlink()
        return True
    except Exception as e:
        print(f"❌ Errore nel ripristino delle impostazioni: {e}")
        return False


def get_projects_directory() -> Path:
    """Restituisce la directory dei progetti"""
    projects_dir = AppConfig.get_documents_dir() / "Projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir


def get_cache_directory() -> Path:
    """Restituisce la directory della cache"""
    cache_dir = AppConfig.get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_logs_directory() -> Path:
    """Restituisce la directory dei log"""
    logs_dir = AppConfig.get_app_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_exports_directory() -> Path:
    """Restituisce la directory delle esportazioni"""
    exports_dir = AppConfig.get_documents_dir() / "Exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


def create_default_directories():
    """Crea le directory di default dell'applicazione"""
    directories = [
        AppConfig.get_app_data_dir(),
        AppConfig.get_config_dir(),
        AppConfig.get_documents_dir(),
        AppConfig.get_cache_dir(),
        get_projects_directory(),
        get_logs_directory(),
        get_exports_directory()
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"⚠️ Impossibile creare directory: {directory}")


class SettingsManager:
    """Gestore avanzato delle impostazioni con cache e validazione"""
    
    def __init__(self):
        self._settings = load_user_settings()
        self._observers = []
        self._cache = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Ottiene un'impostazione"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Imposta un'impostazione"""
        if AppConfig.validate_setting(key, value):
            old_value = self._settings.get(key)
            self._settings[key] = value
            
            # Notifica observers
            self._notify_observers(key, old_value, value)
            
            # Salva automaticamente
            return save_user_settings(self._settings)
        
        return False
    
    def update(self, settings_dict: Dict[str, Any]) -> bool:
        """Aggiorna multiple impostazioni"""
        valid_updates = {}
        
        for key, value in settings_dict.items():
            if AppConfig.validate_setting(key, value):
                valid_updates[key] = value
        
        if valid_updates:
            old_settings = self._settings.copy()
            self._settings.update(valid_updates)
            
            # Notifica observers per ogni cambio
            for key, value in valid_updates.items():
                old_value = old_settings.get(key)
                self._notify_observers(key, old_value, value)
            
            return save_user_settings(self._settings)
        
        return False
    
    def reset(self) -> bool:
        """Ripristina alle impostazioni di default"""
        self._settings = AppConfig.DEFAULT_SETTINGS.copy()
        
        # Notifica reset completo
        for observer in self._observers:
            if hasattr(observer, 'on_settings_reset'):
                observer.on_settings_reset()
        
        return save_user_settings(self._settings)
    
    def add_observer(self, observer):
        """Aggiunge un observer per i cambiamenti"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Rimuove un observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, key: str, old_value: Any, new_value: Any):
        """Notifica gli observers dei cambiamenti"""
        for observer in self._observers:
            if hasattr(observer, 'on_setting_changed'):
                try:
                    observer.on_setting_changed(key, old_value, new_value)
                except Exception as e:
                    print(f"⚠️ Errore nell'observer: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Restituisce tutte le impostazioni"""
        return self._settings.copy()
    
    def export_settings(self, file_path: str) -> bool:
        """Esporta le impostazioni in un file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Errore nell'esportazione: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Importa le impostazioni da un file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            return self.update(imported_settings)
            
        except Exception as e:
            print(f"❌ Errore nell'importazione: {e}")
            return False


# Istanza globale del gestore impostazioni
settings_manager = SettingsManager()


def get_app_info() -> Dict[str, str]:
    """Restituisce le informazioni dell'applicazione"""
    return {
        "name": AppConfig.APP_NAME,
        "version": AppConfig.APP_VERSION,
        "author": AppConfig.APP_AUTHOR,
        "description": AppConfig.APP_DESCRIPTION,
        "config_dir": str(AppConfig.get_config_dir()),
        "data_dir": str(AppConfig.get_app_data_dir()),
        "projects_dir": str(get_projects_directory()),
        "cache_dir": str(get_cache_directory())
    }


def check_first_run() -> bool:
    """Verifica se è la prima esecuzione dell'app"""
    settings_file = get_settings_file_path()
    return not settings_file.exists()


def setup_first_run():
    """Configura l'applicazione per la prima esecuzione"""
    print("🎉 Prima esecuzione di Ollama Chat!")
    print("📁 Creazione directory...")
    
    # Crea directory
    create_default_directories()
    
    # Salva impostazioni di default
    save_user_settings(AppConfig.DEFAULT_SETTINGS)
    
    print("✅ Configurazione completata!")
    print(f"📂 Directory progetti: {get_projects_directory()}")
    print(f"⚙️ File impostazioni: {get_settings_file_path()}")


if __name__ == "__main__":
    # Test del modulo
    print("🧪 Test modulo configurazione")
    
    # Test caricamento impostazioni
    settings = load_user_settings()
    print(f"📝 Impostazioni caricate: {len(settings)} elementi")
    
    # Test validazione
    valid = AppConfig.validate_setting("font_size", 12)
    print(f"✅ Validazione font_size=12: {valid}")
    
    invalid = AppConfig.validate_setting("font_size", 50)
    print(f"❌ Validazione font_size=50: {invalid}")
    
    # Test manager
    manager = SettingsManager()
    print(f"🔧 Manager inizializzato con {len(manager.get_all())} impostazioni")
    
    # Test info app
    info = get_app_info()
    print(f"ℹ️ Info app: {info['name']} v{info['version']}")
    
    print("✅ Test completati!")