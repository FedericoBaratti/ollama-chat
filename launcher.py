#!/usr/bin/env python3
"""
Launcher PULITO per Ollama Chat GUI
Design minimalista e professionale
"""

import sys
import os

def check_dependencies():
    """Verifica le dipendenze necessarie"""
    missing = []
    
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt6")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    if missing:
        print("❌ Dipendenze mancanti:")
        for dep in missing:
            print(f"  - {dep}")
        print("\n💡 Installa con: pip install " + " ".join(missing))
        return False
    
    return True

def launch_full_version():
    """Avvia la versione completa con grafica pulita"""
    try:
        from styles import StyleManager
        from main import main
        print("🚀 Avvio versione completa con design pulito...")
        return main()
    except ImportError as e:
        print(f"⚠️ Modulo mancante: {e}")
        print("🔄 Avvio versione con grafica pulita semplificata...")
        return launch_clean_version()
    except Exception as e:
        print(f"❌ Errore nell'avvio: {e}")
        return launch_clean_version()

def launch_clean_version():
    """Avvia versione con grafica pulita e minimalista"""
    print("🚀 Avvio Ollama Chat - EDIZIONE PULITA")
    
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSplitter,
        QFrame, QMessageBox, QScrollArea, QStatusBar, QMenuBar, QMenu
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QAction
    import requests
    import json
    import time
    
    # STILI PULITI E MINIMALISTI
    CLEAN_STYLES = """
        /* Stile principale */
        QMainWindow {
            background-color: #ffffff;
            color: #1e293b;
        }
        
        /* Sidebar */
        QFrame#cleanSidebar {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        
        QLabel#cleanTitle {
            color: #1e293b;
            font-size: 20px;
            font-weight: 700;
            margin: 20px 0px;
            padding: 16px;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            text-align: center;
        }
        
        QLabel#cleanSubtitle {
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 20px;
            text-align: center;
        }
        
        QLabel#sectionTitle {
            color: #1e293b;
            font-weight: 600;
            font-size: 12px;
            margin: 20px 0 10px 0;
            padding: 4px 0px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Pulsanti */
        QPushButton#cleanPrimary {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton#cleanPrimary:hover {
            background-color: #1d4ed8;
        }
        
        QPushButton#cleanSecondary {
            background-color: #ffffff;
            color: #1e293b;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton#cleanSecondary:hover {
            background-color: #f8fafc;
            border-color: #2563eb;
        }
        
        QPushButton#cleanSuccess {
            background-color: #059669;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
            min-width: 80px;
            padding: 10px 20px;
        }
        
        QPushButton#cleanSuccess:hover {
            background-color: #047857;
        }
        
        QPushButton#cleanDanger {
            background-color: #dc2626;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
            min-width: 80px;
            padding: 10px 20px;
        }
        
        QPushButton#cleanDanger:hover {
            background-color: #b91c1c;
        }
        
        /* ComboBox */
        QComboBox#cleanCombo {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
            color: #1e293b;
            font-weight: 500;
            min-height: 20px;
        }
        
        QComboBox#cleanCombo:focus {
            border-color: #2563eb;
        }
        
        QComboBox#cleanCombo QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            selection-background-color: #f8fafc;
            color: #1e293b;
            font-weight: 500;
        }
        
        /* Input */
        QLineEdit#cleanInput {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            color: #1e293b;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        QLineEdit#cleanInput:focus {
            border-color: #2563eb;
        }
        
        /* Chat Area */
        QWidget#cleanChatArea {
            background-color: #ffffff;
            border-left: 1px solid #e2e8f0;
        }
        
        QFrame#cleanChatHeader {
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
        }
        
        QLabel#cleanChatTitle {
            color: #1e293b;
            font-size: 16px;
            font-weight: 600;
            margin: 8px 0;
        }
        
        QLabel#cleanStatus {
            color: #64748b;
            background-color: #f8fafc;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 11px;
            font-weight: 500;
        }
        
        QTextEdit#cleanMessages {
            background-color: transparent;
            border: none;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
            font-weight: 400;
        }
        
        QFrame#cleanInputArea {
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
        }
        
        /* StatusBar */
        QStatusBar {
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
            font-weight: 500;
            font-size: 11px;
            padding: 4px 8px;
        }
        
        /* MenuBar */
        QMenuBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            color: #1e293b;
            font-weight: 500;
            font-size: 12px;
            padding: 4px;
        }
        
        QMenuBar::item {
            background: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #f8fafc;
        }
        
        /* ScrollBar */
        QScrollBar:vertical {
            background-color: #f8fafc;
            width: 12px;
            border-radius: 6px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #e2e8f0;
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
    """
    
    class CleanOllamaWorker(QThread):
        """Worker pulito per Ollama"""
        models_received = pyqtSignal(list)
        message_chunk = pyqtSignal(str)
        message_completed = pyqtSignal()
        error_occurred = pyqtSignal(str)
        
        def __init__(self, server_url="http://localhost:11434"):
            super().__init__()
            self.server_url = server_url
            self.task = None
            self.message = None
            self.model = None
            self.stop_requested = False
        
        def get_models(self):
            self.task = "models"
            self.start()
        
        def send_message(self, model, message):
            self.task = "message"
            self.model = model
            self.message = message
            self.stop_requested = False
            self.start()
        
        def stop_generation(self):
            self.stop_requested = True
        
        def run(self):
            try:
                if self.task == "models":
                    self._get_models()
                elif self.task == "message":
                    self._send_message()
            except Exception as e:
                self.error_occurred.emit(str(e))
        
        def _get_models(self):
            response = requests.get(f"{self.server_url}/api/tags", timeout=10)
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            self.models_received.emit(models)
        
        def _send_message(self):
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": self.message}],
                "stream": True
            }
            
            response = requests.post(
                f"{self.server_url}/api/chat",
                json=payload,
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if self.stop_requested:
                    break
                    
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            if content:
                                self.message_chunk.emit(content)
                        
                        if chunk.get('done', False):
                            self.message_completed.emit()
                            break
                    except json.JSONDecodeError:
                        continue
    
    class CleanOllamaChat(QMainWindow):
        """Interfaccia PULITA e MINIMALISTA"""
        
        def __init__(self):
            super().__init__()
            self.worker = CleanOllamaWorker()
            self.current_response = ""
            self.is_generating = False
            self.messages_history = []
            
            self.setup_clean_ui()
            self.setup_connections()
            self.setup_clean_menu()
            
            # Auto-carica modelli
            QTimer.singleShot(1000, self.load_models)
        
        def setup_clean_ui(self):
            """Configura interfaccia pulita"""
            self.setWindowTitle("💬 Ollama Chat - Edizione Pulita")
            self.setGeometry(100, 100, 1200, 800)
            self.setMinimumSize(900, 600)
            
            # Widget centrale
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout principale
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Splitter
            splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # Sidebar pulita
            self.create_clean_sidebar(splitter)
            
            # Area chat pulita
            self.create_clean_chat_area(splitter)
            
            splitter.setSizes([300, 900])
            main_layout.addWidget(splitter)
            
            # Status bar pulita
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("💬 Ollama Chat - Pronto per l'uso")
            
            # Applica stili puliti
            self.setStyleSheet(CLEAN_STYLES)
        
        def create_clean_sidebar(self, parent):
            """Crea sidebar pulita"""
            sidebar = QFrame()
            sidebar.setObjectName("cleanSidebar")
            sidebar.setFixedWidth(300)
            
            layout = QVBoxLayout(sidebar)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # Titolo pulito
            title = QLabel("💬 Ollama Chat")
            title.setObjectName("cleanTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            subtitle = QLabel("Interfaccia Pulita e Professionale")
            subtitle.setObjectName("cleanSubtitle")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)
            
            # Sezione modello
            model_label = QLabel("🤖 Modello AI")
            model_label.setObjectName("sectionTitle")
            layout.addWidget(model_label)
            
            self.model_combo = QComboBox()
            self.model_combo.setObjectName("cleanCombo")
            self.model_combo.currentTextChanged.connect(self.on_model_changed)
            layout.addWidget(self.model_combo)
            
            self.refresh_btn = QPushButton("🔄 Aggiorna Modelli")
            self.refresh_btn.setObjectName("cleanPrimary")
            self.refresh_btn.clicked.connect(self.load_models)
            layout.addWidget(self.refresh_btn)
            
            # Sezione chat
            chat_label = QLabel("💬 Gestione Chat")
            chat_label.setObjectName("sectionTitle")
            layout.addWidget(chat_label)
            
            self.new_chat_btn = QPushButton("✨ Nuova Chat")
            self.new_chat_btn.setObjectName("cleanPrimary")
            self.new_chat_btn.clicked.connect(self.new_chat)
            layout.addWidget(self.new_chat_btn)
            
            self.clear_btn = QPushButton("🗑️ Cancella Chat")
            self.clear_btn.setObjectName("cleanSecondary")
            self.clear_btn.clicked.connect(self.clear_chat)
            layout.addWidget(self.clear_btn)
            
            layout.addStretch()
            
            # Status
            status_frame = QFrame()
            status_layout = QVBoxLayout(status_frame)
            
            server_label = QLabel("🌐 Server")
            server_label.setObjectName("sectionTitle")
            
            self.server_info = QLabel("localhost:11434")
            self.server_info.setObjectName("cleanStatus")
            
            self.connection_status = QLabel("⚪ Connessione...")
            self.connection_status.setObjectName("cleanStatus")
            
            status_layout.addWidget(server_label)
            status_layout.addWidget(self.server_info)
            status_layout.addWidget(self.connection_status)
            
            layout.addWidget(status_frame)
            
            parent.addWidget(sidebar)
        
        def create_clean_chat_area(self, parent):
            """Crea area chat pulita"""
            chat_widget = QWidget()
            chat_widget.setObjectName("cleanChatArea")
            
            layout = QVBoxLayout(chat_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Header pulito
            header = QFrame()
            header.setObjectName("cleanChatHeader")
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            self.chat_title = QLabel("💬 Seleziona un modello per iniziare")
            self.chat_title.setObjectName("cleanChatTitle")
            
            self.status_label = QLabel("")
            self.status_label.setObjectName("cleanStatus")
            
            header_layout.addWidget(self.chat_title)
            header_layout.addStretch()
            header_layout.addWidget(self.status_label)
            
            layout.addWidget(header)
            
            # Area messaggi pulita
            self.messages_area = QTextEdit()
            self.messages_area.setObjectName("cleanMessages")
            self.messages_area.setReadOnly(True)
            layout.addWidget(self.messages_area)
            
            # Area input pulita
            input_frame = QFrame()
            input_frame.setObjectName("cleanInputArea")
            
            input_layout = QHBoxLayout(input_frame)
            input_layout.setContentsMargins(20, 15, 20, 15)
            input_layout.setSpacing(12)
            
            self.message_input = QLineEdit()
            self.message_input.setObjectName("cleanInput")
            self.message_input.setPlaceholderText("Scrivi il tuo messaggio...")
            self.message_input.returnPressed.connect(self.send_message)
            self.message_input.textChanged.connect(self.on_input_changed)
            
            self.send_btn = QPushButton("📤 Invia")
            self.send_btn.setObjectName("cleanSuccess")
            self.send_btn.clicked.connect(self.send_message)
            self.send_btn.setEnabled(False)
            
            self.stop_btn = QPushButton("⏹️ Stop")
            self.stop_btn.setObjectName("cleanDanger")
            self.stop_btn.clicked.connect(self.stop_generation)
            self.stop_btn.setVisible(False)
            
            input_layout.addWidget(self.message_input)
            input_layout.addWidget(self.send_btn)
            input_layout.addWidget(self.stop_btn)
            
            layout.addWidget(input_frame)
            
            parent.addWidget(chat_widget)
        
        def setup_clean_menu(self):
            """Menu pulito"""
            menubar = self.menuBar()
            
            # Menu File
            file_menu = menubar.addMenu("File")
            
            new_action = QAction("✨ Nuova Chat", self)
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self.new_chat)
            file_menu.addAction(new_action)
            
            # Menu Help
            help_menu = menubar.addMenu("Aiuto")
            
            about_action = QAction("ℹ️ Informazioni", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
        
        def setup_connections(self):
            """Connessioni segnali"""
            self.worker.models_received.connect(self.on_models_received)
            self.worker.message_chunk.connect(self.on_message_chunk)
            self.worker.message_completed.connect(self.on_message_completed)
            self.worker.error_occurred.connect(self.on_error)
        
        def load_models(self):
            """Carica modelli"""
            self.status_bar.showMessage("🔄 Caricamento modelli...")
            self.connection_status.setText("🔄 Connessione...")
            self.refresh_btn.setText("⏳ Caricamento...")
            self.refresh_btn.setEnabled(False)
            self.worker.get_models()
        
        def on_models_received(self, models):
            """Modelli ricevuti"""
            self.model_combo.clear()
            if models:
                self.model_combo.addItems(models)
                self.connection_status.setText("✅ Connesso")
                self.status_bar.showMessage(f"✅ {len(models)} modelli caricati")
                self.refresh_btn.setText("✅ Caricato")
            else:
                self.connection_status.setText("❌ Nessun modello")
                self.status_bar.showMessage("❌ Nessun modello trovato")
                self.refresh_btn.setText("❌ Errore")
            
            QTimer.singleShot(2000, lambda: self.refresh_btn.setText("🔄 Aggiorna Modelli"))
            self.refresh_btn.setEnabled(True)
        
        def on_model_changed(self, model_name):
            """Modello cambiato"""
            if model_name:
                self.chat_title.setText(f"💬 Chat con {model_name}")
                self.send_btn.setEnabled(bool(self.message_input.text().strip()))
            else:
                self.chat_title.setText("💬 Seleziona un modello per iniziare")
                self.send_btn.setEnabled(False)
        
        def on_input_changed(self, text):
            """Input cambiato"""
            has_model = bool(self.model_combo.currentText())
            self.send_btn.setEnabled(has_model and not self.is_generating)
        
        def send_message(self):
            """Invia messaggio"""
            message = self.message_input.text().strip()
            model = self.model_combo.currentText()
            
            if not message or not model or self.is_generating:
                return
            
            # Aggiungi messaggio utente
            timestamp = time.strftime("%H:%M")
            self.messages_area.append(f"\n[{timestamp}] 👤 Tu: {message}")
            self.message_input.clear()
            
            # Prepara risposta
            self.current_response = ""
            self.is_generating = True
            
            # UI generazione
            self.send_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            self.message_input.setEnabled(False)
            self.status_label.setText("🤖 Generando...")
            
            # Invia
            self.worker.send_message(model, message)
            self.status_bar.showMessage("🤖 Generando risposta...")
        
        def on_message_chunk(self, chunk):
            """Chunk messaggio"""
            if not self.current_response:
                timestamp = time.strftime("%H:%M")
                self.messages_area.append(f"\n[{timestamp}] 🤖 AI: ")
            
            self.current_response += chunk
            
            # Aggiorna messaggio
            cursor = self.messages_area.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            
            text = self.messages_area.toPlainText()
            lines = text.split('\n')
            
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith("[") and "🤖 AI:" in lines[i]:
                    timestamp = time.strftime("%H:%M")
                    lines[i] = f"[{timestamp}] 🤖 AI: {self.current_response}"
                    break
            
            self.messages_area.setPlainText('\n'.join(lines))
            cursor.movePosition(cursor.MoveOperation.End)
            self.messages_area.setTextCursor(cursor)
        
        def on_message_completed(self):
            """Messaggio completato"""
            self.on_generation_finished()
            self.status_bar.showMessage("✅ Risposta completata")
        
        def on_error(self, error):
            """Errore"""
            QMessageBox.critical(self, "Errore", f"Errore: {error}")
            self.on_generation_finished()
            self.status_bar.showMessage(f"❌ Errore: {error}")
        
        def on_generation_finished(self):
            """Generazione finita"""
            self.is_generating = False
            self.send_btn.setVisible(True)
            self.stop_btn.setVisible(False)
            self.message_input.setEnabled(True)
            self.status_label.setText("")
            self.on_input_changed(self.message_input.text())
        
        def stop_generation(self):
            """Ferma generazione"""
            self.worker.stop_generation()
            self.on_generation_finished()
            self.status_bar.showMessage("⏹️ Generazione fermata")
        
        def new_chat(self):
            """Nuova chat"""
            reply = QMessageBox.question(
                self, "Nuova Chat",
                "Iniziare una nuova chat? I messaggi correnti verranno persi.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.clear_chat()
        
        def clear_chat(self):
            """Cancella chat"""
            self.messages_area.clear()
            self.messages_history = []
            self.status_bar.showMessage("🗑️ Chat cancellata")
        
        def show_about(self):
            """Informazioni"""
            QMessageBox.about(self, "💬 Ollama Chat - Edizione Pulita", 
                "💬 OLLAMA CHAT - EDIZIONE PULITA\n\n"
                "✨ Caratteristiche:\n"
                "• Design pulito e minimalista\n"
                "• Interfaccia professionale\n"
                "• Colori armonici e leggibili\n"
                "• Esperienza utente ottimizzata\n\n"
                "🎨 Design moderno senza eccessi visivi\n"
                "💼 Perfetto per uso professionale"
            )
    
    # Avvia applicazione pulita
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = CleanOllamaChat()
    window.show()
    
    print("💬 OLLAMA CHAT - EDIZIONE PULITA AVVIATA!")
    print("🎨 Design minimalista e professionale")
    print("📝 Interfaccia pulita e leggibile")
    print("✨ Esperienza utente ottimizzata")
    
    return app.exec()

def main():
    """Funzione principale del launcher pulito"""
    print("💬 OLLAMA CHAT GUI - LAUNCHER PULITO")
    print("=" * 50)
    print("🎨 Caricamento design minimalista...")
    print("📝 Preparazione interfaccia pulita...")
    print("✨ Inizializzazione...")
    
    # Verifica dipendenze
    if not check_dependencies():
        return 1
    
    # Avvia versione pulita
    return launch_full_version()

if __name__ == "__main__":
    sys.exit(main())