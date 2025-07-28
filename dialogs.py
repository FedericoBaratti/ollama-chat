#!/usr/bin/env python3
"""
Finestre di dialogo per Ollama Chat GUI
Dialog moderni e ottimizzati per la gestione progetti
Utilizzano il sistema di stili centralizzato
"""

import os
import json
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QSpinBox, QCheckBox, QSlider,
    QTabWidget, QWidget, QFormLayout, QGroupBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox,
    QProgressBar, QScrollArea, QGridLayout, QFrame, QSpacerItem,
    QSizePolicy, QDialogButtonBox, QPlainTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QPalette

from project_manager import ProjectManager, FileManager, KnowledgeBase
from widgets import ProjectCard, LoadingIndicator, CustomProgressBar


class ModernDialog(QDialog):
    """Classe base per dialog moderni con stile centralizzato"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 300)
        self.setup_base_ui()
        # Non applica stili qui, lascia che sia fatto dal sistema centralizzato
    
    def setup_base_ui(self):
        """Configura l'interfaccia base con il nuovo stile"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1) # Bordo sottile
        self.main_layout.setSpacing(0)
        
        # Header del dialog
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)
        
        # Contenuto principale
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(25, 20, 25, 25)
        self.content_layout.setSpacing(15)
        
        self.content_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.content_area)
    
    def create_header(self):
        """Crea l'header pulito del dialog"""
        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icona
        self.icon_label = QLabel("⚙️")
        self.icon_label.setObjectName("dialogIcon")
        self.icon_label.setFixedSize(50, 50)
        
        # Titolo
        self.title_label = QLabel(self.windowTitle())
        self.title_label.setObjectName("dialogTitle")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        return header
    
    def add_content_widget(self, widget):
        """Aggiunge un widget al contenuto"""
        self.content_layout.addWidget(widget)
    
    def add_content_layout(self, layout):
        """Aggiunge un layout al contenuto"""
        self.content_layout.addLayout(layout)


class ProjectCreationDialog(ModernDialog):
    """Dialog per creare un nuovo progetto"""
    
    def __init__(self, parent=None):
        super().__init__("✨ Nuovo Progetto", parent)
        self.icon_label.setText("🚀")
        self.setFixedSize(500, 400)
        self.setup_project_ui()
    
    def setup_project_ui(self):
        """Configura l'interfaccia specifica per i progetti"""
        # Form container
        form_group = QGroupBox("Informazioni Progetto")
        form_group.setObjectName("formGroup")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        
        # Nome progetto
        self.name_input = QLineEdit()
        self.name_input.setObjectName("projectNameInput")
        self.name_input.setPlaceholderText("Es: Progetto Marketing 2024")
        self.name_input.textChanged.connect(self.validate_inputs)
        # Font coerente
        self.name_input.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Descrizione
        self.description_input = QTextEdit()
        self.description_input.setObjectName("projectDescInput")
        self.description_input.setPlaceholderText("Descrivi brevemente il progetto...")
        self.description_input.setMaximumHeight(100)
        self.description_input.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        self.description_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Template progetto
        self.template_combo = QComboBox()
        self.template_combo.setObjectName("templateCombo")
        self.template_combo.addItems([
            "Progetto Vuoto",
            "Progetto Documentazione", 
            "Progetto Codice",
            "Progetto Ricerca",
            "Progetto Personale"
        ])
        self.template_combo.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        self.template_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        form_layout.addRow("📛 Nome Progetto:", self.name_input)
        form_layout.addRow("📝 Descrizione:", self.description_input)
        form_layout.addRow("📋 Template:", self.template_combo)
        
        self.add_content_widget(form_group)
        
        # Opzioni avanzate
        advanced_group = QGroupBox("Opzioni Avanzate")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.auto_backup_check = QCheckBox("Backup automatico")
        self.auto_backup_check.setChecked(True)
        self.auto_backup_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        self.enable_search_check = QCheckBox("Abilita ricerca full-text")
        self.enable_search_check.setChecked(True)
        self.enable_search_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        advanced_layout.addWidget(self.auto_backup_check)
        advanced_layout.addWidget(self.enable_search_check)
        
        self.add_content_widget(advanced_group)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ Annulla")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        self.create_btn = QPushButton("✨ Crea Progetto")
        self.create_btn.setObjectName("primaryButton")
        self.create_btn.clicked.connect(self.accept_project)
        self.create_btn.setEnabled(False)
        self.create_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.create_btn)
        
        self.add_content_layout(buttons_layout)
    
    def validate_inputs(self):
        """Valida gli input del form"""
        name = self.name_input.text().strip()
        self.create_btn.setEnabled(bool(name))
    
    def accept_project(self):
        """Conferma la creazione del progetto"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Nome Richiesto", "Inserisci un nome per il progetto!")
            return
        self.accept()
    
    def get_project_data(self):
        """Restituisce i dati del progetto"""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'template': self.template_combo.currentText(),
            'auto_backup': self.auto_backup_check.isChecked(),
            'enable_search': self.enable_search_check.isChecked()
        }


class KnowledgeDialog(ModernDialog):
    """Dialog principale per la gestione della knowledge base"""
    
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__("🧠 Gestione Progetti e Knowledge", parent)
        self.icon_label.setText("🧠")
        self.setGeometry(200, 200, 1200, 800)
        
        self.project_manager = project_manager
        self.knowledge_base = KnowledgeBase(project_manager)
        self.current_project = None
        self.file_manager = None
        
        self.setup_knowledge_ui()
        self.load_projects()

        # Forza l'applicazione degli stili dopo il caricamento
        QTimer.singleShot(100, self._refresh_styles)
    
    def _refresh_styles(self):
        """Riapplica gli stili al dialog"""
        self.setStyleSheet(self.styleSheet())
    
    def setup_knowledge_ui(self):
        """Configura l'interfaccia della knowledge base"""
        # Splitter principale
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Pannello sinistro - Lista progetti
        left_panel = self.create_projects_panel()
        main_splitter.addWidget(left_panel)
        
        # Pannello destro - Dettagli
        right_panel = self.create_details_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([400, 800])
        
        # Layout wrapper per il content
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(main_splitter)
        
        # Pulsanti azioni
        actions_layout = QHBoxLayout()
        
        self.new_project_btn = QPushButton("✨ Nuovo Progetto")
        self.new_project_btn.setObjectName("primaryButton")
        self.new_project_btn.clicked.connect(self.create_new_project)
        self.new_project_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        self.import_files_btn = QPushButton("📁 Importa File")
        self.import_files_btn.setObjectName("secondaryButton")
        self.import_files_btn.clicked.connect(self.import_files)
        self.import_files_btn.setEnabled(False)
        self.import_files_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        self.export_project_btn = QPushButton("📤 Esporta")
        self.export_project_btn.setObjectName("secondaryButton")
        self.export_project_btn.clicked.connect(self.export_project)
        self.export_project_btn.setEnabled(False)
        self.export_project_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        actions_layout.addWidget(self.new_project_btn)
        actions_layout.addWidget(self.import_files_btn)
        actions_layout.addWidget(self.export_project_btn)
        actions_layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        actions_layout.addWidget(button_box)
        
        wrapper_layout.addLayout(actions_layout)
        
        # Sostituisci il contenuto del dialog
        self.content_layout.addLayout(wrapper_layout)
    
    def create_projects_panel(self):
        """Crea il pannello dei progetti"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("🚀 I Miei Progetti")
        header.setObjectName("panelTitle")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Stats
        self.stats_label = QLabel("0 progetti • 0 file totali")
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        layout.addWidget(header)
        layout.addWidget(self.stats_label)
        
        # Scroll area per progetti
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("projectsScrollArea")
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.projects_container = QWidget()
        self.projects_container.setObjectName("projectsContainer")  
        self.projects_container.setStyleSheet("QWidget#projectsContainer { background-color: #f8fafc; }")
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setSpacing(10)
        self.projects_layout.addStretch()
        
        scroll_area.setWidget(self.projects_container)
        layout.addWidget(scroll_area)
        
        # Pulsanti azioni progetti
        project_actions = QHBoxLayout()
        
        self.delete_project_btn = QPushButton("🗑️ Elimina")
        self.delete_project_btn.setObjectName("warningButton")
        self.delete_project_btn.clicked.connect(self.delete_project)
        self.delete_project_btn.setEnabled(False)
        self.delete_project_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        project_actions.addWidget(self.delete_project_btn)
        project_actions.addStretch()
        
        layout.addLayout(project_actions)
        
        return panel
    
    def create_details_panel(self):
        """Crea il pannello dei dettagli"""
        # Tab widget per organizzare le sezioni
        self.details_tabs = QTabWidget()
        self.details_tabs.setObjectName("detailsTabs")
        
        # Tab Info
        info_tab = self.create_info_tab()
        self.details_tabs.addTab(info_tab, "ℹ️ Informazioni")
        
        # Tab File
        files_tab = self.create_files_tab()
        self.details_tabs.addTab(files_tab, "📁 File")
        
        # Tab Knowledge
        knowledge_tab = self.create_knowledge_tab()
        self.details_tabs.addTab(knowledge_tab, "🧠 Knowledge")
        
        return self.details_tabs
    
    def create_info_tab(self):
        """Crea il tab delle informazioni"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info progetto
        info_group = QGroupBox("📋 Informazioni Progetto")
        info_layout = QFormLayout(info_group)
        
        self.project_name_label = QLabel("Nessun progetto selezionato")
        self.project_name_label.setWordWrap(True)
        self.project_desc_label = QLabel("-")
        self.project_desc_label.setWordWrap(True)
        self.project_created_label = QLabel("-")
        self.project_files_count_label = QLabel("0")
        
        # Font coerenti
        for label in [self.project_name_label, self.project_desc_label, 
                     self.project_created_label, self.project_files_count_label]:
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        info_layout.addRow("📛 Nome:", self.project_name_label)
        info_layout.addRow("📝 Descrizione:", self.project_desc_label)
        info_layout.addRow("📅 Creato:", self.project_created_label)
        info_layout.addRow("📁 File:", self.project_files_count_label)
        
        layout.addWidget(info_group)
        
        # Knowledge summary
        summary_group = QGroupBox("🧠 Riassunto Knowledge")
        summary_layout = QVBoxLayout(summary_group)
        
        self.knowledge_summary = QTextEdit()
        self.knowledge_summary.setObjectName("knowledgeSummary")
        self.knowledge_summary.setMaximumHeight(200)
        self.knowledge_summary.setReadOnly(True)
        self.knowledge_summary.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        self.generate_summary_btn = QPushButton("🔄 Genera Riassunto")
        self.generate_summary_btn.setObjectName("primaryButton")
        self.generate_summary_btn.clicked.connect(self.generate_summary)
        self.generate_summary_btn.setEnabled(False)
        self.generate_summary_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        summary_layout.addWidget(self.knowledge_summary)
        summary_layout.addWidget(self.generate_summary_btn)
        
        layout.addWidget(summary_group)
        layout.addStretch()
        
        return tab
    
    def create_files_tab(self):
        """Crea il tab per i file"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header_layout = QHBoxLayout()
        
        files_title = QLabel("📁 File del Progetto")
        files_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        
        self.add_files_btn = QPushButton("➕ Aggiungi File")
        self.add_files_btn.setObjectName("primaryButton")
        self.add_files_btn.clicked.connect(self.add_files_to_project)
        self.add_files_btn.setEnabled(False)
        self.add_files_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        header_layout.addWidget(files_title)
        header_layout.addStretch()
        header_layout.addWidget(self.add_files_btn)
        
        layout.addLayout(header_layout)
        
        # Lista file
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["Nome File", "Tipo", "Dimensione", "Data"])
        self.files_tree.itemDoubleClicked.connect(self.preview_file)
        self.files_tree.itemSelectionChanged.connect(self.on_file_selected)
        # Font coerente
        self.files_tree.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        
        layout.addWidget(self.files_tree)
        
        # Azioni file
        file_actions = QHBoxLayout()
        
        self.preview_file_btn = QPushButton("👁️ Anteprima")
        self.preview_file_btn.setObjectName("secondaryButton")
        self.preview_file_btn.clicked.connect(self.preview_selected_file)
        self.preview_file_btn.setEnabled(False)
        self.preview_file_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        
        self.remove_file_btn = QPushButton("🗑️ Rimuovi")
        self.remove_file_btn.setObjectName("warningButton")
        self.remove_file_btn.clicked.connect(self.remove_file)
        self.remove_file_btn.setEnabled(False)
        self.remove_file_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        
        file_actions.addWidget(self.preview_file_btn)
        file_actions.addWidget(self.remove_file_btn)
        file_actions.addStretch()
        
        layout.addLayout(file_actions)
        
        return tab
    
    def create_knowledge_tab(self):
        """Crea il tab per la knowledge base"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search
        search_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Cerca:")
        search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        self.knowledge_search = QLineEdit()
        self.knowledge_search.setPlaceholderText("Cerca nei contenuti...")
        self.knowledge_search.returnPressed.connect(self.search_knowledge)
        self.knowledge_search.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setObjectName("primaryButton")
        self.search_btn.clicked.connect(self.search_knowledge)
        self.search_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.knowledge_search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Risultati
        self.search_results = QTextEdit()
        self.search_results.setPlaceholderText("I risultati della ricerca appariranno qui...")
        self.search_results.setReadOnly(True)
        self.search_results.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        layout.addWidget(self.search_results)
        
        return tab
    
    # Metodi di utilità rimanenti rimangono invariati ma con font coerenti
    def load_projects(self):
        """Carica la lista dei progetti"""
        # Rimuovi progetti esistenti
        while self.projects_layout.count() > 1:
            child = self.projects_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        projects = self.project_manager.get_projects()
        total_files = 0
        
        for project in projects:
            card = ProjectCard(project, self.projects_container)
            card.clicked.connect(self.on_project_selected)
            
            # Conta file
            stats = self.project_manager.get_project_statistics(project['id'])
            card.update_files_count(stats['total_files'])
            total_files += stats['total_files']
            
            self.projects_layout.insertWidget(self.projects_layout.count() - 1, card)
        
        # Aggiorna stats
        self.stats_label.setText(f"{len(projects)} progetti • {total_files} file totali")
    
    def on_project_selected(self, card: ProjectCard):
        """Gestisce la selezione di un progetto"""
        # Deseleziona altre card
        for i in range(self.projects_layout.count() - 1):
            child = self.projects_layout.itemAt(i)
            if child.widget() and isinstance(child.widget(), ProjectCard):
                child.widget().set_selected(False)
        
        # Seleziona card cliccata
        card.set_selected(True)
        
        # Carica progetto
        project_id = card.project_data['id']
        self.current_project = self.project_manager.get_project(project_id)
        
        if self.current_project:
            project_dir = self.project_manager.projects_dir / project_id
            self.file_manager = FileManager(str(project_dir))
            
            self.update_project_info()
            self.load_project_files()
            
            # Abilita pulsanti
            self.import_files_btn.setEnabled(True)
            self.export_project_btn.setEnabled(True)
            self.delete_project_btn.setEnabled(True)
            self.add_files_btn.setEnabled(True)
            self.generate_summary_btn.setEnabled(True)
    
    def update_project_info(self):
        """Aggiorna le informazioni del progetto"""
        if not self.current_project:
            return
        
        self.project_name_label.setText(self.current_project['name'])
        self.project_desc_label.setText(self.current_project['description'] or "Nessuna descrizione")
        self.project_created_label.setText(self.current_project['created_at'])
        
        if self.file_manager:
            files = self.file_manager.get_files(self.current_project['id'])
            self.project_files_count_label.setText(str(len(files)))
        
        # Knowledge summary
        if self.current_project.get('knowledge_summary'):
            self.knowledge_summary.setPlainText(self.current_project['knowledge_summary'])
    
    def load_project_files(self):
        """Carica i file del progetto"""
        self.files_tree.clear()
        
        if not self.file_manager:
            return
        
        files = self.file_manager.get_files(self.current_project['id'])
        
        for file_info in files:
            item = QTreeWidgetItem()
            
            # Icona basata sul tipo
            if file_info['type'].startswith('text/'):
                icon = "📄"
            elif file_info['type'].startswith('image/'):
                icon = "🖼️"
            elif 'pdf' in file_info['type']:
                icon = "📋"
            else:
                icon = "📎"
            
            item.setText(0, f"{icon} {file_info['filename']}")
            item.setText(1, file_info['type'])
            item.setText(2, self.format_file_size(file_info['size']))
            item.setText(3, file_info['created_at'])
            item.setData(0, Qt.ItemDataRole.UserRole, file_info['id'])
            
            self.files_tree.addTopLevelItem(item)
        
        # Ridimensiona colonne
        for i in range(4):
            self.files_tree.resizeColumnToContents(i)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Formatta la dimensione del file"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    # Altri metodi rimangono invariati...
    def create_new_project(self):
        """Crea un nuovo progetto"""
        dialog = ProjectCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()
            project_id = self.project_manager.create_project(data['name'], data['description'])
            self.load_projects()
    
    def add_files_to_project(self):
        """Aggiunge file al progetto"""
        if not self.current_project:
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleziona File da Aggiungere",
            "", "Tutti i file (*.*)"
        )
        
        if files and self.file_manager:
            progress = CustomProgressBar()
            progress.setRange(0, len(files))
            
            added_count = 0
            for i, file_path in enumerate(files):
                result = self.file_manager.add_file(file_path, self.current_project['id'])
                if result['status'] == 'added':
                    added_count += 1
                progress.setValue(i + 1)
            
            self.load_project_files()
            self.update_project_info()
            
            QMessageBox.information(
                self, "File Aggiunti",
                f"Aggiunti {added_count} file su {len(files)} selezionati."
            )
    
    def on_file_selected(self):
        """Gestisce la selezione di un file"""
        selected = self.files_tree.selectedItems()
        has_selection = len(selected) > 0
        
        self.preview_file_btn.setEnabled(has_selection)
        self.remove_file_btn.setEnabled(has_selection)
    
    def preview_selected_file(self):
        """Mostra anteprima del file selezionato"""
        selected = self.files_tree.selectedItems()
        if selected:
            file_id = selected[0].data(0, Qt.ItemDataRole.UserRole)
            self.show_file_preview(file_id)
    
    def preview_file(self, item, column):
        """Anteprima tramite doppio click"""
        file_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.show_file_preview(file_id)
    
    def show_file_preview(self, file_id: int):
        """Mostra l'anteprima di un file"""
        if not self.file_manager:
            return
        
        content = self.file_manager.get_file_content(file_id)
        if content:
            dialog = FilePreviewDialog(content, self)
            dialog.exec()
    
    def remove_file(self):
        """Rimuove un file dal progetto"""
        selected = self.files_tree.selectedItems()
        if not selected:
            return
        
        filename = selected[0].text(0)
        reply = QMessageBox.question(
            self, "Conferma Rimozione",
            f"Sei sicuro di voler rimuovere '{filename}' dal progetto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_id = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if self.file_manager.delete_file(file_id):
                self.load_project_files()
                self.update_project_info()
    
    def search_knowledge(self):
        """Cerca nella knowledge base"""
        if not self.file_manager or not self.knowledge_search.text().strip():
            return
        
        query = self.knowledge_search.text().strip()
        results = self.file_manager.search_in_files(query, self.current_project['id'])
        
        if results:
            text = f"🔍 Risultati per '{query}':\n\n"
            for result in results:
                text += f"📁 {result['filename']} ({result['type']})\n"
                if result['snippet']:
                    text += f"   💬 {result['snippet']}\n"
                text += "\n"
        else:
            text = f"Nessun risultato trovato per '{query}'"
        
        self.search_results.setPlainText(text)
    
    def generate_summary(self):
        """Genera riassunto knowledge"""
        if not self.current_project:
            return
        
        summary = self.knowledge_base.generate_project_summary(self.current_project['id'])
        self.knowledge_summary.setPlainText(summary)
        
        # Salva nel database
        self.project_manager.update_project(
            self.current_project['id'], 
            knowledge_summary=summary
        )
    
    def delete_project(self):
        """Elimina il progetto selezionato"""
        if not self.current_project:
            return
        
        reply = QMessageBox.question(
            self, "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare '{self.current_project['name']}'?\n\n"
            "Questa operazione eliminerà tutti i file e non può essere annullata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_manager.delete_project(self.current_project['id']):
                self.load_projects()
                self.current_project = None
                QMessageBox.information(self, "Progetto Eliminato", "Progetto eliminato con successo.")
    
    def import_files(self):
        """Importa file nel progetto"""
        self.add_files_to_project()
    
    def export_project(self):
        """Esporta il progetto"""
        if not self.current_project:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Esporta Progetto",
            f"{self.current_project['name']}.zip",
            "File ZIP (*.zip)"
        )
        
        if filename:
            if self.project_manager.export_project(self.current_project['id'], filename):
                QMessageBox.information(self, "Esportazione Completata", 
                                      f"Progetto esportato in: {filename}")
            else:
                QMessageBox.critical(self, "Errore", "Errore durante l'esportazione.")


class FilePreviewDialog(ModernDialog):
    """Dialog per l'anteprima dei file"""
    
    def __init__(self, content: str, parent=None):
        super().__init__("👁️ Anteprima File", parent)
        self.icon_label.setText("👁️")
        self.setGeometry(300, 300, 800, 600)
        self.setup_preview_ui(content)
    
    def setup_preview_ui(self, content: str):
        """Configura l'interfaccia di anteprima"""
        # Contenuto
        self.content_display = QPlainTextEdit()
        self.content_display.setPlainText(content)
        self.content_display.setReadOnly(True)
        self.content_display.setFont(QFont("Consolas", 10, QFont.Weight.Normal))
        
        self.add_content_widget(self.content_display)
        
        # Pulsante chiudi
        close_btn = QPushButton("✅ Chiudi")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        self.add_content_layout(button_layout)


class SettingsDialog(ModernDialog):
    """Dialog per le impostazioni dell'applicazione"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings: Dict[str, Any], parent=None):
        super().__init__("⚙️ Impostazioni", parent)
        self.icon_label.setText("⚙️")
        self.current_settings = current_settings.copy()
        self.setFixedSize(600, 500)
        self.setup_settings_ui()
    
    def setup_settings_ui(self):
        """Configura l'interfaccia delle impostazioni"""
        # Tab widget
        tabs = QTabWidget()
        
        # Tab Server
        server_tab = self.create_server_tab()
        tabs.addTab(server_tab, "🌐 Server")
        
        # Tab Interfaccia
        ui_tab = self.create_ui_tab()
        tabs.addTab(ui_tab, "🎨 Interfaccia")
        
        # Tab Avanzate
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "⚡ Avanzate")
        
        self.add_content_widget(tabs)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Ripristina")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self.reset_settings)
        reset_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        apply_btn = QPushButton("✅ Applica")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        cancel_btn = QPushButton("❌ Annulla")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)
        
        self.add_content_layout(buttons_layout)
    
    def create_server_tab(self):
        """Crea il tab delle impostazioni server"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # URL Server
        self.server_url_input = QLineEdit()
        self.server_url_input.setText(self.current_settings.get("server_url", "http://localhost:11434"))
        self.server_url_input.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        self.server_url_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(self.current_settings.get("request_timeout", 30))
        self.timeout_spin.setSuffix(" secondi")
        self.timeout_spin.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        self.timeout_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Auto refresh
        self.auto_refresh_check = QCheckBox()
        self.auto_refresh_check.setChecked(self.current_settings.get("auto_refresh_models", True))
        self.auto_refresh_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        self.auto_refresh_check.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout.addRow("🌐 URL Server:", self.server_url_input)
        layout.addRow("⏱️ Timeout Richieste:", self.timeout_spin)
        layout.addRow("🔄 Auto-refresh Modelli:", self.auto_refresh_check)
        
        return tab
    
    def create_ui_tab(self):
        """Crea il tab dell'interfaccia"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Dimensione font
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(self.current_settings.get("font_size", 11))
        self.font_size_spin.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        # Timestamp
        self.show_timestamps_check = QCheckBox()
        self.show_timestamps_check.setChecked(self.current_settings.get("show_timestamps", True))
        self.show_timestamps_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        # Animazioni
        self.animations_check = QCheckBox()
        self.animations_check.setChecked(self.current_settings.get("animations", True))
        self.animations_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.current_settings.get("theme", "light").capitalize())
        self.theme_combo.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))

        layout.addRow("🎨 Tema:", self.theme_combo)
        layout.addRow("📝 Dimensione Font:", self.font_size_spin)
        layout.addRow("🕒 Mostra Timestamp:", self.show_timestamps_check)
        layout.addRow("✨ Animazioni:", self.animations_check)
        
        return tab
    
    def create_advanced_tab(self):
        """Crea il tab delle impostazioni avanzate"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Max messaggi
        self.max_messages_spin = QSpinBox()
        self.max_messages_spin.setRange(50, 1000)
        self.max_messages_spin.setValue(self.current_settings.get("max_messages", 200))
        self.max_messages_spin.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        # Knowledge
        self.use_knowledge_check = QCheckBox()
        self.use_knowledge_check.setChecked(self.current_settings.get("use_knowledge", True))
        self.use_knowledge_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        # Context length
        self.context_length_spin = QSpinBox()
        self.context_length_spin.setRange(500, 5000)
        self.context_length_spin.setValue(self.current_settings.get("knowledge_context_length", 2000))
        self.context_length_spin.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        layout.addRow("💬 Max Messaggi:", self.max_messages_spin)
        layout.addRow("🧠 Usa Knowledge Base:", self.use_knowledge_check)
        layout.addRow("📏 Lunghezza Contesto:", self.context_length_spin)
        
        return tab
    
    def apply_settings(self):
        """Applica le impostazioni"""
        new_settings = {
            "server_url": self.server_url_input.text().strip(),
            "request_timeout": self.timeout_spin.value(),
            "auto_refresh_models": self.auto_refresh_check.isChecked(),
            "theme": self.theme_combo.currentText().lower(),
            "font_size": self.font_size_spin.value(),
            "show_timestamps": self.show_timestamps_check.isChecked(),
            "animations": self.animations_check.isChecked(),
            "max_messages": self.max_messages_spin.value(),
            "use_knowledge": self.use_knowledge_check.isChecked(),
            "knowledge_context_length": self.context_length_spin.value()
        }
        
        self.settings_changed.emit(new_settings)
        self.accept()
    
    def reset_settings(self):
        """Ripristina le impostazioni di default"""
        reply = QMessageBox.question(
            self, "Ripristina Impostazioni",
            "Sei sicuro di voler ripristinare tutte le impostazioni ai valori di default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Ripristina valori di default
            self.server_url_input.setText("http://localhost:11434")
            self.timeout_spin.setValue(30)
            self.auto_refresh_check.setChecked(True)
            self.theme_combo.setCurrentText("Light")
            self.font_size_spin.setValue(11)
            self.show_timestamps_check.setChecked(True)
            self.animations_check.setChecked(True)
            self.max_messages_spin.setValue(200)
            self.use_knowledge_check.setChecked(True)
            self.context_length_spin.setValue(2000)