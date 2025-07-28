#!/usr/bin/env python3
"""
Ollama Chat GUI - Applicazione Principale
Sistema completo di chat con knowledge base e gestione progetti
Versione refactorizzata con stile centralizzato e coerente
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QSplitter, QMessageBox, QStatusBar, QMenuBar, QFileDialog,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QStandardPaths, pyqtSlot
from PyQt6.QtGui import QAction, QFont

# Import dei moduli personalizzati
from styles import StyleManager, ThemeManager
from widgets import MessageWidget, SmartScrollArea, LoadingIndicator, CollapsibleSection
from project_manager import ProjectManager, FileManager, KnowledgeBase
from ollama_worker import OllamaWorker, ConnectionMonitor
from dialogs import KnowledgeDialog, SettingsDialog, ProjectCreationDialog
from config import AppConfig, load_user_settings, save_user_settings
from utils import format_timestamp, sanitize_filename, show_error_dialog


class ChatArea(QWidget):
    """Area principale della chat ottimizzata con stile coerente"""
    
    def __init__(self, settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = settings
        self.messages = []
        self.current_response_widget = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia dell'area chat"""
        self.setObjectName("chatArea")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header della chat
        self.chat_header = self.create_chat_header()
        layout.addWidget(self.chat_header)
        
        # Area messaggi con scroll intelligente
        self.scroll_area = SmartScrollArea()
        self.scroll_area.setObjectName("messagesScrollArea")
        
        # Container per i messaggi
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area, 1)
        
        # Area input
        self.input_area = self.create_input_area()
        layout.addWidget(self.input_area)
    
    def create_chat_header(self):
        """Crea l'header della chat"""
        header = QWidget()
        header.setObjectName("chatHeader")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 10, 25, 10)
        
        # Titolo chat - usa font coerente
        self.chat_title = QLabel("💬 Seleziona un modello per iniziare")
        self.chat_title.setObjectName("chatTitle")
        self.chat_title.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        self.chat_title.setWordWrap(True)
        self.chat_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Indicatore di digitazione
        self.typing_indicator = QLabel()
        self.typing_indicator.setObjectName("typingIndicator")
        self.typing_indicator.setVisible(False)
        self.typing_indicator.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.typing_indicator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(self.chat_title)
        layout.addStretch()
        layout.addWidget(self.typing_indicator)
        
        return header
    
    def create_input_area(self):
        """Crea l'area di input"""
        area = QWidget()
        area.setObjectName("inputArea")
        area.setFixedHeight(120)
        
        layout = QVBoxLayout(area)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(10)
        
        # Context info
        self.context_label = QLabel("📚 Context: Nessun progetto attivo")
        self.context_label.setObjectName("contextLabel")
        self.context_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.context_label.setWordWrap(True)
        self.context_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Input row
        input_row = QHBoxLayout()
        
        # Campo di input
        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Scrivi il tuo messaggio qui... ✨")
        self.message_input.setMinimumHeight(45)
        self.message_input.setFont(QFont("Segoe UI", 13, QFont.Weight.Normal))
        
        # Pulsante allega
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("attachButton")
        self.attach_btn.setFixedSize(45, 45)
        self.attach_btn.setToolTip("Allega file al progetto")
        
        # Pulsante invia
        self.send_btn = QPushButton("🚀 Invia")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setMinimumSize(100, 45)
        self.send_btn.setEnabled(False)
        self.send_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.send_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Pulsante stop
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setMinimumSize(100, 45)
        self.stop_btn.setVisible(False)
        self.stop_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.attach_btn)
        input_row.addWidget(self.send_btn)
        input_row.addWidget(self.stop_btn)
        
        layout.addWidget(self.context_label)
        layout.addLayout(input_row)
        
        return area
    
    def add_message(self, content: str, is_user: bool = True) -> MessageWidget:
        """Aggiunge un messaggio alla chat"""
        message_widget = MessageWidget(
            content, is_user, 
            settings=self.settings
        )
        
        self.messages.append(message_widget)
        
        # Inserisci prima dello stretch
        insert_index = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(insert_index, message_widget)
        
        # Scroll automatico
        if self.settings.get("smart_scroll", True):
            QTimer.singleShot(100, self.scroll_area.smooth_scroll_to_bottom)
        
        return message_widget
    
    def update_current_response(self, content: str):
        """Aggiorna la risposta corrente (streaming)"""
        if self.current_response_widget:
            self.current_response_widget.update_content(content)
    
    def finalize_current_response(self):
        """Finalizza la risposta corrente"""
        if self.current_response_widget:
            self.current_response_widget.finalize_message()
            self.current_response_widget = None
    
    def clear_messages(self):
        """Pulisce tutti i messaggi"""
        while self.messages:
            widget = self.messages.pop()
            widget.deleteLater()
        
        # Rimuovi dal layout
        while self.messages_layout.count() > 1:
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_chat_title(self, title: str):
        """Imposta il titolo della chat"""
        self.chat_title.setText(title)
    
    def set_context_info(self, info: str):
        """Imposta le informazioni del contesto"""
        self.context_label.setText(info)
    
    def show_typing_indicator(self, message: str = "🤖 Generando risposta..."):
        """Mostra l'indicatore di digitazione"""
        self.typing_indicator.setText(message)
        self.typing_indicator.setVisible(True)
    
    def hide_typing_indicator(self):
        """Nasconde l'indicatore di digitazione"""
        self.typing_indicator.setVisible(False)


class Sidebar(QWidget):
    """Sidebar moderna e funzionale con stile coerente"""
    
    def __init__(self, settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della sidebar"""
        self.setObjectName("modernSidebar")
        self.setFixedWidth(320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header dell'app
        header = self.create_header()
        layout.addWidget(header)
        
        # Sezioni collassabili
        self.project_section = CollapsibleSection("📋 Progetto")
        self.setup_project_section()
        layout.addWidget(self.project_section)

        self.model_section = CollapsibleSection("🧠 Modello AI")
        self.setup_model_section()
        layout.addWidget(self.model_section)

        self.chat_section = CollapsibleSection("💬 Gestione Chat")
        self.setup_chat_section()
        layout.addWidget(self.chat_section)

        self.actions_section = CollapsibleSection("⚡ Azioni")
        self.setup_actions_section()
        layout.addWidget(self.actions_section)
        
        layout.addStretch(1)
        
        # Info connessione
        connection_info = self.create_connection_info()
        layout.addWidget(connection_info)
    
    def create_header(self):
        """Crea l'header dell'applicazione"""
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("🚀 Ollama Chat")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Con Knowledge Base")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return header
    
    def create_project_section(self):
        """Crea la sezione progetto"""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        title = QLabel("📋 Progetto Attivo")
        title.setObjectName("sectionTitle")
        
        self.current_project_label = QLabel("Nessun progetto")
        self.current_project_label.setObjectName("currentProject")
        self.current_project_label.setWordWrap(True)
        self.current_project_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.manage_projects_btn = QPushButton("🧠 Gestisci Progetti")
        self.manage_projects_btn.setObjectName("primaryButton")
        self.manage_projects_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.manage_projects_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout.addWidget(title)
        layout.addWidget(self.current_project_label)
        layout.addWidget(self.manage_projects_btn)
        
        return section
    
    def create_model_section(self):
        """Crea la sezione modello"""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        title = QLabel("🧠 Modello AI")
        title.setObjectName("sectionTitle")
        
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modernCombo")
        self.model_combo.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        self.refresh_models_btn = QPushButton("🔄 Aggiorna")
        self.refresh_models_btn.setObjectName("secondaryButton")
        self.refresh_models_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        layout.addWidget(title)
        layout.addWidget(self.model_combo)
        layout.addWidget(self.refresh_models_btn)
        
        return section
    
    def create_chat_section(self):
        """Crea la sezione chat"""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        title = QLabel("💬 Gestione Chat")
        title.setObjectName("sectionTitle")
        
        self.new_chat_btn = QPushButton("✨ Nuova Chat")
        self.new_chat_btn.setObjectName("primaryButton")
        self.new_chat_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        buttons_row = QHBoxLayout()
        
        self.save_chat_btn = QPushButton("💾 Salva")
        self.save_chat_btn.setObjectName("secondaryButton")
        self.save_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        self.load_chat_btn = QPushButton("📂 Carica")
        self.load_chat_btn.setObjectName("secondaryButton")
        self.load_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        buttons_row.addWidget(self.save_chat_btn)
        buttons_row.addWidget(self.load_chat_btn)
        
        layout.addWidget(title)
        layout.addWidget(self.new_chat_btn)
        layout.addLayout(buttons_row)
        
        return section
    
    def create_actions_section(self):
        """Crea la sezione azioni"""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        title = QLabel("⚡ Azioni")
        title.setObjectName("sectionTitle")
        
        self.clear_chat_btn = QPushButton("🗑️ Cancella Chat")
        self.clear_chat_btn.setObjectName("warningButton")
        self.clear_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        self.export_chat_btn = QPushButton("📤 Esporta Chat")
        self.export_chat_btn.setObjectName("secondaryButton")
        self.export_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        layout.addWidget(title)
        layout.addWidget(self.clear_chat_btn)
        layout.addWidget(self.export_chat_btn)
        
        return section
    
    def create_connection_info(self):
        """Crea le info di connessione"""
        info = QWidget()
        layout = QVBoxLayout(info)
        
        # Knowledge status
        knowledge_group = QWidget()
        knowledge_layout = QVBoxLayout(knowledge_group)
        knowledge_layout.setContentsMargins(10, 10, 10, 10)
        
        knowledge_title = QLabel("🧠 Knowledge")
        knowledge_title.setObjectName("connectionTitle")
        
        self.knowledge_status = QLabel("Nessun progetto attivo")
        self.knowledge_status.setObjectName("connectionStatus")
        self.knowledge_status.setWordWrap(True)
        
        knowledge_layout.addWidget(knowledge_title)
        knowledge_layout.addWidget(self.knowledge_status)
        
        # Server status
        server_group = QWidget()
        server_layout = QVBoxLayout(server_group)
        server_layout.setContentsMargins(10, 10, 10, 10)
        
        server_title = QLabel("🌐 Server")
        server_title.setObjectName("connectionTitle")
        
        self.server_status = QLabel("localhost:11434")
        self.server_status.setObjectName("connectionStatus")
        self.server_status.setWordWrap(True)
        
        server_layout.addWidget(server_title)
        server_layout.addWidget(self.server_status)
        
        # Connection status
        connection_group = QWidget()
        connection_layout = QVBoxLayout(connection_group)
        connection_layout.setContentsMargins(10, 10, 10, 10)
        
        connection_title = QLabel("🔗 Stato")
        connection_title.setObjectName("connectionTitle")
        
        self.connection_status = QLabel("⚪ Disconnesso")
        self.connection_status.setObjectName("connectionStatus")
        
        connection_layout.addWidget(connection_title)
        connection_layout.addWidget(self.connection_status)
        
        layout.addWidget(knowledge_group)
        layout.addWidget(server_group)
        layout.addWidget(connection_group)
        
        return info

    def setup_project_section(self):
        self.current_project_label = QLabel("Nessun progetto")
        self.current_project_label.setObjectName("currentProject")
        self.current_project_label.setWordWrap(True)
        self.current_project_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.manage_projects_btn = QPushButton("🧠 Gestisci Progetti")
        self.manage_projects_btn.setObjectName("primaryButton")
        self.manage_projects_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.manage_projects_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.project_section.add_widget(self.current_project_label)
        self.project_section.add_widget(self.manage_projects_btn)

    def setup_model_section(self):
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modernCombo")
        self.model_combo.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        self.refresh_models_btn = QPushButton("🔄 Aggiorna")
        self.refresh_models_btn.setObjectName("secondaryButton")
        self.refresh_models_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))

        self.model_section.add_widget(self.model_combo)
        self.model_section.add_widget(self.refresh_models_btn)

    def setup_chat_section(self):
        self.new_chat_btn = QPushButton("✨ Nuova Chat")
        self.new_chat_btn.setObjectName("primaryButton")
        self.new_chat_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        buttons_row = QHBoxLayout()
        
        self.save_chat_btn = QPushButton("💾 Salva")
        self.save_chat_btn.setObjectName("secondaryButton")
        self.save_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        self.load_chat_btn = QPushButton("📂 Carica")
        self.load_chat_btn.setObjectName("secondaryButton")
        self.load_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        buttons_row.addWidget(self.save_chat_btn)
        buttons_row.addWidget(self.load_chat_btn)

        self.chat_section.add_widget(self.new_chat_btn)
        self.chat_section.add_layout(buttons_row)

    def setup_actions_section(self):
        self.clear_chat_btn = QPushButton("🗑️ Cancella Chat")
        self.clear_chat_btn.setObjectName("warningButton")
        self.clear_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        self.export_chat_btn = QPushButton("📤 Esporta Chat")
        self.export_chat_btn.setObjectName("secondaryButton")
        self.export_chat_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))

        self.actions_section.add_widget(self.clear_chat_btn)
        self.actions_section.add_widget(self.export_chat_btn)
    
    def update_project_info(self, project_name: str, files_count: int = 0):
        """Aggiorna le informazioni del progetto"""
        if project_name:
            self.current_project_label.setText(f"📁 {project_name}")
            self.knowledge_status.setText(f"✅ {files_count} file caricati")
        else:
            self.current_project_label.setText("Nessun progetto")
            self.knowledge_status.setText("Nessun progetto attivo")
    
    def update_connection_status(self, connected: bool):
        """Aggiorna lo stato della connessione"""
        if connected:
            self.connection_status.setText("✅ Connesso")
        else:
            self.connection_status.setText("❌ Disconnesso")
    
    def update_server_info(self, server_url: str):
        """Aggiorna le informazioni del server"""
        display_url = server_url.replace("http://", "").replace("https://", "")
        if len(display_url) > 25:
            display_url = display_url[:22] + "..."
        self.server_status.setText(display_url)
        self.server_status.setToolTip(server_url)


class OllamaChatMainWindow(QMainWindow):
    """Finestra principale dell'applicazione con stile coerente"""
    
    def __init__(self):
        super().__init__()
        
        # Carica configurazione
        self.config = AppConfig()
        self.settings = load_user_settings()
        
        # Inizializza componenti principali
        self.project_manager = None
        self.knowledge_base = None
        self.current_project = None
        self.file_manager = None
        
        # Worker Ollama
        self.ollama_worker = None
        self.connection_monitor = None
        
        # UI Components
        self.sidebar = None
        self.chat_area = None
        
        # Stato applicazione
        self.current_model = None
        self.is_generating = False
        self.current_response = ""
        
        self.theme_manager = ThemeManager(self.settings.get("theme", "light"))
        self.settings_dialog = None

        self.init_application()
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()

    def open_settings_dialog(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.settings, self)
        self.settings_dialog.settings_changed.connect(self.on_settings_changed)
        self.settings_dialog.exec()

    def apply_theme(self):
        """Applica il tema all'applicazione"""
        self.theme_manager.set_theme(self.settings.get("theme", "light"))
        stylesheet = self.theme_manager.get_themed_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Aggiorna info server nella sidebar
        server_url = self.settings.get("server_url", "http://localhost:11434")
        self.sidebar.update_server_info(server_url)
        
        # Avvia componenti
        self.start_workers()
        
        # Auto-load modelli se abilitato
        if self.settings.get("auto_refresh_models", True):
            QTimer.singleShot(1000, self.load_models)
    
    def init_application(self):
        """Inizializza i componenti dell'applicazione"""
        # Setup finestra con font coerente
        self.setWindowTitle("🚀 Ollama Chat - Knowledge Edition")
        self.setGeometry(100, 100, 
                        self.settings.get("window_width", 1400),
                        self.settings.get("window_height", 900))
        self.setMinimumSize(1200, 700)
        
        # Inizializza project manager
        projects_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
            "OllamaProjects"
        )
        self.project_manager = ProjectManager(projects_dir)
        self.knowledge_base = KnowledgeBase(self.project_manager)
        
        # Inizializza worker Ollama
        self.ollama_worker = OllamaWorker(self.settings)
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter principale
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        
        # Sidebar
        self.sidebar = Sidebar(self.settings)
        self.sidebar.setMinimumWidth(300)
        self.sidebar.setMaximumWidth(500)
        splitter.addWidget(self.sidebar)
        
        # Chat area
        self.chat_area = ChatArea(self.settings)
        splitter.addWidget(self.chat_area)
        
        # Imposta proporzioni iniziali
        splitter.setSizes([350, self.width() - 350])
        splitter.setStretchFactor(1, 1) # Permette alla chat area di espandersi
        
        main_layout.addWidget(splitter)
        
        # Status bar con font coerente
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("modernStatusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🎉 Ollama Chat con Knowledge Base caricato!")
        
        # Menu bar
        self.setup_menu_bar()
    
    def setup_menu_bar(self):
        """Configura la barra dei menu"""
        menubar = self.menuBar()
        menubar.setObjectName("modernMenuBar")
        
        # Menu File
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("✨ Nuova Chat", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("💾 Salva Chat", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_chat)
        file_menu.addAction(save_action)
        
        load_action = QAction("📂 Carica Chat", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_chat)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Esci", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Progetti
        projects_menu = menubar.addMenu("Progetti")
        
        manage_action = QAction("🧠 Gestisci Progetti", self)
        manage_action.setShortcut("Ctrl+P")
        manage_action.triggered.connect(self.show_knowledge_dialog)
        projects_menu.addAction(manage_action)
        
        new_project_action = QAction("✨ Nuovo Progetto", self)
        new_project_action.setShortcut("Ctrl+Shift+N")
        new_project_action.triggered.connect(self.quick_new_project)
        projects_menu.addAction(new_project_action)
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu("Impostazioni")
        
        preferences_action = QAction("⚙️ Preferenze", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        # Menu Aiuto
        help_menu = menubar.addMenu("Aiuto")
        
        about_action = QAction("ℹ️ Informazioni", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """Configura le connessioni dei segnali"""
        # Sidebar connections
        self.sidebar.manage_projects_btn.clicked.connect(self.show_knowledge_dialog)
        self.sidebar.refresh_models_btn.clicked.connect(self.load_models)
        self.sidebar.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.sidebar.new_chat_btn.clicked.connect(self.new_chat)
        self.sidebar.save_chat_btn.clicked.connect(self.save_chat)
        self.sidebar.load_chat_btn.clicked.connect(self.load_chat)
        self.sidebar.clear_chat_btn.clicked.connect(self.clear_chat)
        self.sidebar.export_chat_btn.clicked.connect(self.export_chat)
        
        # Chat area connections
        self.chat_area.message_input.returnPressed.connect(self.send_message)
        self.chat_area.message_input.textChanged.connect(self.on_input_changed)
        self.chat_area.send_btn.clicked.connect(self.send_message)
        self.chat_area.stop_btn.clicked.connect(self.stop_generation)
        self.chat_area.attach_btn.clicked.connect(self.attach_files)
        
        # Worker connections
        if self.ollama_worker:
            self.ollama_worker.models_received.connect(self.on_models_received)
            self.ollama_worker.message_chunk_received.connect(self.on_message_chunk)
            self.ollama_worker.message_completed.connect(self.on_message_completed)
            self.ollama_worker.error_occurred.connect(self.on_error_occurred)
            self.ollama_worker.connection_status_changed.connect(self.on_connection_changed)
            self.ollama_worker.generation_stopped.connect(self.on_generation_stopped)
    
    def start_workers(self):
        """Avvia i thread worker"""
        if self.ollama_worker:
            # Avvia connection monitor
            self.connection_monitor = ConnectionMonitor(
                self.ollama_worker.request_manager
            )
            self.connection_monitor.connection_changed.connect(self.on_connection_changed)
            self.connection_monitor.start()
    
    def apply_theme(self):
        """Applica il tema all'applicazione"""
        theme_manager = ThemeManager(self.settings.get("theme", "clean_professional"))
        stylesheet = theme_manager.get_themed_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Aggiorna info server nella sidebar
        server_url = self.settings.get("server_url", "http://localhost:11434")
        self.sidebar.update_server_info(server_url)
    
    # Slot per gestione eventi (invariati, solo aggiornati i font)
    @pyqtSlot(list)
    def on_models_received(self, models):
        """Gestisce la ricezione dei modelli"""
        self.sidebar.model_combo.clear()
        if models:
            self.sidebar.model_combo.addItems(models)
            self.sidebar.update_connection_status(True)
            self.status_bar.showMessage(f"✅ {len(models)} modelli caricati")
        else:
            self.sidebar.update_connection_status(False)
            self.status_bar.showMessage("❌ Nessun modello trovato")
    
    @pyqtSlot(str)
    def on_message_chunk(self, chunk):
        """Gestisce la ricezione di un chunk di messaggio"""
        self.current_response += chunk
        self.chat_area.update_current_response(self.current_response)
    
    @pyqtSlot(str)
    def on_message_completed(self, full_response):
        """Gestisce il completamento di un messaggio"""
        self.chat_area.finalize_current_response()
        self.on_generation_finished()
        self.status_bar.showMessage("✅ Risposta completata")
    
    @pyqtSlot(str)
    def on_error_occurred(self, error_message):
        """Gestisce gli errori"""
        show_error_dialog(self, "Errore Ollama", error_message)
        self.on_generation_finished()
        self.status_bar.showMessage(f"❌ Errore: {error_message}")
    
    @pyqtSlot(bool)
    def on_connection_changed(self, connected):
        """Gestisce il cambio di stato della connessione"""
        self.sidebar.update_connection_status(connected)
        if connected:
            self.status_bar.showMessage("✅ Connesso al server Ollama")
        else:
            self.status_bar.showMessage("❌ Connessione al server Ollama persa")
    
    @pyqtSlot()
    def on_generation_stopped(self):
        """Gestisce l'interruzione della generazione"""
        self.chat_area.finalize_current_response()
        self.on_generation_finished()
        self.status_bar.showMessage("⏹️ Generazione interrotta")
    
    def on_model_changed(self, model_name):
        """Gestisce il cambio di modello"""
        self.current_model = model_name
        if model_name:
            self.chat_area.set_chat_title(f"💬 Chat con {model_name}")
            self.ollama_worker.set_model(model_name)
            self.status_bar.showMessage(f"🤖 Modello selezionato: {model_name}")
        else:
            self.chat_area.set_chat_title("💬 Seleziona un modello per iniziare")
        
        self.update_input_state()
    
    def on_input_changed(self, text):
        """Gestisce il cambio del testo di input"""
        self.update_input_state()
    
    def update_input_state(self):
        """Aggiorna lo stato dell'input"""
        has_model = bool(self.current_model)
        can_send = has_model and not self.is_generating
        
        self.chat_area.send_btn.setEnabled(can_send)
    
    # Tutti gli altri metodi rimangono invariati ma con stili coerenti
    def load_models(self):
        """Carica i modelli disponibili"""
        if self.ollama_worker and not self.ollama_worker.is_busy:
            self.ollama_worker.load_models()
            self.status_bar.showMessage("🔄 Caricamento modelli...")
    
    def send_message(self):
        """Invia un messaggio"""
        if self.is_generating:
            return
        
        message_text = self.chat_area.message_input.text().strip()
        if not message_text or not self.current_model:
            return
        
        # Aggiungi messaggio utente
        self.chat_area.add_message(message_text, is_user=True)
        self.chat_area.message_input.clear()
        
        # Prepara per la risposta
        self.is_generating = True
        self.current_response = ""
        
        # Crea widget per la risposta
        self.chat_area.current_response_widget = self.chat_area.add_message("", is_user=False)
        
        # Ottieni contesto dalla knowledge base
        context = ""
        if self.current_project and self.settings.get("use_knowledge", True):
            print(f"DEBUG: current_project = {self.current_project['name'] if self.current_project else None}")
            print(f"DEBUG: use_knowledge = {self.settings.get('use_knowledge', True)}")
            print(f"DEBUG: knowledge_context_length = {self.settings.get('knowledge_context_length', 2000)}")

            context = self.knowledge_base.get_context_for_query(
                message_text, 
                self.current_project['id'],
                self.settings.get("knowledge_context_length", 2000)
            )
            print(f"DEBUG: Generated context length: {len(context)}")
            if context:
                print(f"DEBUG: Context preview: {context[:200]}...")
        else:
            print(f"DEBUG: No context generation - current_project={self.current_project is not None}, use_knowledge={self.settings.get('use_knowledge', True)}")
            self.chat_area.show_typing_indicator("🧠 Generando con knowledge base...")
            self.chat_area.show_typing_indicator()
        
        # Aggiorna UI
        self.chat_area.send_btn.setVisible(False)
        self.chat_area.stop_btn.setVisible(True)
        self.chat_area.message_input.setEnabled(False)
        
        # Invia al worker
        self.ollama_worker.send_message(message_text, context)
        
        self.status_bar.showMessage("🤖 Generando risposta...")
    
    def stop_generation(self):
        """Ferma la generazione"""
        if self.ollama_worker:
            self.ollama_worker.stop_generation()
    
    def on_generation_finished(self):
        """Chiamato quando la generazione è finita"""
        self.is_generating = False
        
        # Ripristina UI
        self.chat_area.send_btn.setVisible(True)
        self.chat_area.stop_btn.setVisible(False)
        self.chat_area.message_input.setEnabled(True)
        self.chat_area.hide_typing_indicator()
        
        self.update_input_state()
    
    # Altri metodi dell'applicazione rimangono invariati...
    def new_chat(self):
        """Inizia una nuova chat"""
        reply = QMessageBox.question(
            self, "Nuova Chat",
            "Sei sicuro di voler iniziare una nuova chat? I messaggi correnti verranno persi.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_chat()
            self.status_bar.showMessage("✨ Nuova chat iniziata")
    
    def clear_chat(self):
        """Pulisce la chat"""
        self.chat_area.clear_messages()
        if self.ollama_worker:
            self.ollama_worker.clear_conversation()
        self.status_bar.showMessage("🗑️ Chat pulita")
    
    def save_chat(self):
        """Salva la chat"""
        if not self.chat_area.messages:
            QMessageBox.information(self, "Salva Chat", "Non ci sono messaggi da salvare.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salva Chat",
            f"chat_{format_timestamp()}.json",
            "JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if filename:
            try:
                messages_data = []
                for widget in self.chat_area.messages:
                    messages_data.append(widget.get_message_data())
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": format_timestamp(),
                        "model": self.current_model,
                        "project": self.current_project['name'] if self.current_project else None,
                        "messages": messages_data
                    }, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"💾 Chat salvata in {Path(filename).name}")
                
            except Exception as e:
                show_error_dialog(self, "Errore Salvataggio", f"Impossibile salvare la chat: {str(e)}")
    
    def load_chat(self):
        """Carica una chat"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Carica Chat", "",
            "JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Pulisci chat corrente
            self.clear_chat()
            
            # Carica messaggi
            messages = data.get("messages", [])
            for msg_data in messages:
                is_user = msg_data["role"] == "user"
                self.chat_area.add_message(msg_data["content"], is_user)
            
            # Imposta modello se disponibile
            if "model" in data and data["model"] in [
                self.sidebar.model_combo.itemText(i) 
                for i in range(self.sidebar.model_combo.count())
            ]:
                self.sidebar.model_combo.setCurrentText(data["model"])
            
            self.status_bar.showMessage(f"📂 Chat caricata da {Path(filename).name}")
            
        except Exception as e:
            show_error_dialog(self, "Errore Caricamento", f"Impossibile caricare la chat: {str(e)}")
    
    def export_chat(self):
        """Esporta la chat in vari formati"""
        if not self.chat_area.messages:
            QMessageBox.information(self, "Esporta Chat", "Non ci sono messaggi da esportare.")
            return
        
        # TODO: Implementa dialog di esportazione
        QMessageBox.information(self, "Esporta Chat", "Funzione di esportazione in sviluppo.")
    
    def show_knowledge_dialog(self):
        """Mostra il dialog della knowledge base"""
        dialog = KnowledgeDialog(self.project_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aggiorna progetto corrente se cambiato
            if dialog.current_project:
                self.set_current_project(dialog.current_project['id'])
    
    def quick_new_project(self):
        """Crea rapidamente un nuovo progetto"""
        dialog = ProjectCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()
            project_id = self.project_manager.create_project(data['name'], data['description'])
            self.set_current_project(project_id)
    
    def set_current_project(self, project_id: str):
        """Imposta il progetto corrente"""
        self.current_project = self.project_manager.get_project(project_id)
        
        if self.current_project:
            # Inizializza file manager
            project_dir = self.project_manager.projects_dir / project_id
            self.file_manager = FileManager(str(project_dir))
            
            # Aggiorna UI
            files_count = len(self.file_manager.get_files(project_id))
            self.sidebar.update_project_info(self.current_project['name'], files_count)
            
            # Aggiorna context info
            self.chat_area.set_context_info(
                f"📚 Context: {self.current_project['name']} ({files_count} file)"
            )
            
            self.status_bar.showMessage(f"📁 Progetto attivo: {self.current_project['name']}")
    
    def attach_files(self):
        """Allega file al progetto corrente"""
        if not self.current_project:
            reply = QMessageBox.question(
                self, "Nessun Progetto",
                "Non hai un progetto attivo. Vuoi crearne uno nuovo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.quick_new_project()
            return
        
        # Apri dialog per selezionare file
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleziona File da Allegare",
            "", "Tutti i file (*.*)"
        )
        
        if files and self.file_manager:
            added_count = 0
            for file_path in files:
                result = self.file_manager.add_file(file_path, self.current_project['id'])
                if result['status'] == 'added':
                    added_count += 1
            
            if added_count > 0:
                # Aggiorna info progetto
                files_count = len(self.file_manager.get_files(self.current_project['id']))
                self.sidebar.update_project_info(self.current_project['name'], files_count)
                self.chat_area.set_context_info(
                    f"📚 Context: {self.current_project['name']} ({files_count} file)"
                )
                
                self.status_bar.showMessage(f"📎 Aggiunti {added_count} file al progetto")
    
    def show_settings(self):
        """Mostra il dialog delle impostazioni"""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
    
    @pyqtSlot(dict)
    def on_settings_changed(self, new_settings):
        """Gestisce il cambio delle impostazioni"""
        self.settings.update(new_settings)
        save_user_settings(self.settings)
        
        # Aggiorna worker
        if self.ollama_worker:
            self.ollama_worker.update_settings(self.settings)
        
        # Riapplica tema
        self.apply_theme()
        
        self.status_bar.showMessage("⚙️ Impostazioni aggiornate")
    
    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        about_text = f"""
        <h2>🚀 Ollama Chat - Knowledge Edition</h2>
        <p><b>Versione:</b> 1.0</p>
        <p><b>Descrizione:</b> Sistema completo di chat con AI e knowledge base</p>
        
        <h3>✨ Caratteristiche:</h3>
        <ul>
        <li>🧠 Knowledge Base con gestione progetti</li>
        <li>📁 Gestione file avanzata</li>
        <li>🔍 Ricerca intelligente nei contenuti</li>
        <li>💬 Chat con streaming in tempo reale</li>
        <li>🎨 Interfaccia moderna e coerente</li>
        <li>⚙️ Configurazione completa</li>
        </ul>
        
        <h3>🌐 Server Corrente:</h3>
        <p>{self.settings.get('server_url', 'Non configurato')}</p>
        
        <h3>📁 Progetto Attivo:</h3>
        <p>{self.current_project['name'] if self.current_project else 'Nessuno'}</p>
        
        <p><i>Sviluppato con PyQt6 e design pulito e professionale! ✨</i></p>
        """
        
        QMessageBox.about(self, "Informazioni", about_text)
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        # Salva impostazioni finestra
        self.settings["window_width"] = self.width()
        self.settings["window_height"] = self.height()
        save_user_settings(self.settings)
        
        # Ferma i worker
        if self.connection_monitor:
            self.connection_monitor.requestInterruption()
            self.connection_monitor.wait(3000)
        
        if self.ollama_worker:
            self.ollama_worker.requestInterruption()
            self.ollama_worker.wait(3000)
        
        event.accept()


def main():
    """Funzione principale dell'applicazione"""
    # Verifica dipendenze
    try:
        from PyQt6.QtWidgets import QApplication
        import requests
    except ImportError as e:
        print(f"❌ Dipendenza mancante: {e}")
        print("💡 Installa con: pip install PyQt6 requests")
        return 1
    
    # Crea applicazione
    app = QApplication(sys.argv)
    app.setApplicationName("Ollama Chat")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("OllamaChat")
    app.setOrganizationDomain("ollama-chat.local")
    
    # Imposta stile e font predefinito
    app.setStyle('Fusion')
    
    # Font dell'applicazione
    default_font = QFont("Segoe UI", 11, QFont.Weight.Normal)
    app.setFont(default_font)
    
    # Crea e mostra finestra principale
    try:
        window = OllamaChatMainWindow()
        window.show()
        
        print("🚀 OLLAMA CHAT - KNOWLEDGE EDITION CON STILE COERENTE!")
        print("🧠 Sistema completo di gestione progetti e knowledge!")
        print("📁 Crea progetti, allega file, usa drag & drop!")
        print("🔍 Ricerca intelligente nei contenuti!")
        print("⌨️ Scorciatoie: Ctrl+P per progetti, Ctrl+N per nuova chat")
        print("🎨 DESIGN PULITO E PROFESSIONALE!")
        
        return app.exec()
        
    except Exception as e:
        show_error_dialog(None, "Errore Avvio", f"Impossibile avviare l'applicazione: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())