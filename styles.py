#!/usr/bin/env python3
"""
Sistema di stili PULITO per Ollama Chat GUI
Design minimalista con tema bianco professionale e coerenza completa
"""

class StyleManager:
    """Gestore centralizzato degli stili con design pulito e coerente"""
    
    # Palette colori pulita e coerente
    COLORS = {
        'primary': '#2563eb',        # Blu professionale
        'primary_hover': '#1d4ed8',  # Blu hover
        'primary_light': '#dbeafe',  # Blu chiaro per backgrounds
        'secondary': '#64748b',      # Grigio bluastro
        'success': '#059669',        # Verde successo
        'success_light': '#d1fae5',  # Verde chiaro
        'warning': '#d97706',        # Arancione warning
        'warning_light': '#fef3c7',  # Arancione chiaro
        'danger': '#dc2626',         # Rosso danger
        'danger_light': '#fee2e2',   # Rosso chiaro
        'background': '#ffffff',     # Bianco puro
        'surface': '#f8fafc',        # Grigio chiarissimo
        'surface_hover': '#f1f5f9',  # Grigio hover
        'border': '#e2e8f0',        # Grigio bordi
        'border_light': '#f1f5f9',  # Grigio bordi chiaro
        'text_primary': '#1e293b',   # Testo principale
        'text_secondary': '#64748b', # Testo secondario
        'text_muted': '#94a3b8',     # Testo disabilitato
        'shadow': 'rgba(0, 0, 0, 0.1)', # Ombra sottile
        'shadow_light': 'rgba(0, 0, 0, 0.05)', # Ombra più leggera
    }
    
    # Font families coerenti
    FONTS = {
        'primary': 'Segoe UI, system-ui, -apple-system, sans-serif',
        'code': 'Consolas, Monaco, "Courier New", monospace',
        'emoji': 'Segoe UI Emoji, "Apple Color Emoji", "Noto Color Emoji"'
    }
    
    @staticmethod
    def get_main_window_style():
        """Stile principale pulito"""
        return f"""
            QMainWindow {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @staticmethod
    def get_sidebar_style():
        """Sidebar pulita e minimalista"""
        return f"""
            QFrame#modernSidebar {{
                background-color: {StyleManager.COLORS['surface']};
                border-right: 1px solid {StyleManager.COLORS['border']};
                border-radius: 0px;
            }}
            
            QLabel#mainTitle {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: 22px;
                font-weight: 700;
                margin: 20px 0px;
                padding: 20px;
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 8px;
                text-align: center;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#subtitle {{
                color: {StyleManager.COLORS['text_secondary']};
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 20px;
                text-align: center;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#sectionTitle {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 600;
                font-size: 13px;
                margin: 20px 0 10px 0;
                padding: 8px 0px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#currentProject {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 500;
                background-color: {StyleManager.COLORS['background']};
                padding: 12px;
                border-radius: 6px;
                border: 1px solid {StyleManager.COLORS['border']};
                margin: 8px 0;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#connectionTitle {{
                color: {StyleManager.COLORS['text_secondary']};
                font-weight: 600;
                font-size: 11px;
                margin-top: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#connectionStatus {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: 12px;
                padding: 8px 12px;
                background-color: {StyleManager.COLORS['background']};
                border-radius: 4px;
                border: 1px solid {StyleManager.COLORS['border_light']};
                margin: 4px 0;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#panelTitle {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 600;
                font-size: 14px;
                margin: 10px 0;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#statsLabel {{
                color: {StyleManager.COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 500;
                margin-bottom: 15px;
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @staticmethod
    def get_button_styles():
        """Pulsanti puliti e moderni"""
        return f"""
            QPushButton#primaryButton {{
                background-color: {StyleManager.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 12px;
                min-height: 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {StyleManager.COLORS['primary_hover']};
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {StyleManager.COLORS['primary_hover']};
            }}
            
            QPushButton#primaryButton:disabled {{
                background-color: {StyleManager.COLORS['text_muted']};
                color: white;
            }}
            
            QPushButton#secondaryButton {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 12px;
                min-height: 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: {StyleManager.COLORS['surface']};
                border-color: {StyleManager.COLORS['primary']};
            }}
            
            QPushButton#secondaryButton:pressed {{
                background-color: {StyleManager.COLORS['border_light']};
            }}
            
            QPushButton#warningButton {{
                background-color: {StyleManager.COLORS['warning']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 12px;
                min-height: 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#warningButton:hover {{
                background-color: #b45309;
            }}
            
            QPushButton#sendButton {{
                background-color: {StyleManager.COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
                padding: 10px 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#sendButton:hover {{
                background-color: #047857;
            }}
            
            QPushButton#sendButton:disabled {{
                background-color: {StyleManager.COLORS['text_muted']};
            }}
            
            QPushButton#stopButton {{
                background-color: {StyleManager.COLORS['danger']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
                padding: 10px 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#stopButton:hover {{
                background-color: #b91c1c;
            }}
            
            QPushButton#attachButton {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_secondary']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                padding: 10px;
                font-family: {StyleManager.FONTS['emoji']};
            }}
            
            QPushButton#attachButton:hover {{
                background-color: {StyleManager.COLORS['surface']};
                color: {StyleManager.COLORS['primary']};
                border-color: {StyleManager.COLORS['primary']};
            }}
            
            QPushButton#sectionHeader {{
                background-color: {StyleManager.COLORS['surface']};
                color: {StyleManager.COLORS['text_primary']};
                border: 1px solid {StyleManager.COLORS['border_light']};
                border-radius: 8px;
                padding: 10px 15px;
                text-align: left;
                font-weight: 600;
                font-size: 12px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QPushButton#sectionHeader:hover {{
                background-color: {StyleManager.COLORS['surface_hover']};
                border-color: {StyleManager.COLORS['border']};
            }}
        """
    
    @staticmethod
    def get_input_styles():
        """Input puliti e moderni"""
        return f"""
            QComboBox#modernCombo, QComboBox#templateCombo {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 500;
                min-height: 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QComboBox#modernCombo:focus, QComboBox#templateCombo:focus {{
                border-color: {StyleManager.COLORS['primary']};
                outline: none;
            }}
            
            QComboBox#modernCombo::drop-down, QComboBox#templateCombo::drop-down {{
                border: none;
                width: 20px;
                padding-right: 12px;
            }}
            
            QComboBox#modernCombo::down-arrow, QComboBox#templateCombo::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {StyleManager.COLORS['text_secondary']};
                margin-right: 6px;
            }}
            
            QComboBox#modernCombo QAbstractItemView, QComboBox#templateCombo QAbstractItemView {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                selection-background-color: {StyleManager.COLORS['surface']};
                selection-color: {StyleManager.COLORS['text_primary']};
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 500;
                padding: 4px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLineEdit#messageInput, QLineEdit#projectNameInput {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 13px;
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
                font-weight: 400;
            }}
            
            QLineEdit#messageInput:focus, QLineEdit#projectNameInput:focus {{
                border-color: {StyleManager.COLORS['primary']};
                outline: none;
            }}
            
            QLineEdit#messageInput::placeholder, QLineEdit#projectNameInput::placeholder {{
                color: {StyleManager.COLORS['text_muted']};
            }}
            
            QTextEdit#projectDescInput, QTextEdit#knowledgeSummary {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-size: 12px;
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
                font-weight: 400;
            }}
            
            QTextEdit#projectDescInput:focus, QTextEdit#knowledgeSummary:focus {{
                border-color: {StyleManager.COLORS['primary']};
                outline: none;
            }}
            
            QSpinBox {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
                font-weight: 400;
            }}
            
            QSpinBox:focus {{
                border-color: {StyleManager.COLORS['primary']};
                outline: none;
            }}
            
            QCheckBox {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: 11px;
                font-weight: 400;
                font-family: {StyleManager.FONTS['primary']};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {StyleManager.COLORS['border']};
                border-radius: 3px;
                background-color: {StyleManager.COLORS['background']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {StyleManager.COLORS['primary']};
                border-color: {StyleManager.COLORS['primary']};
                image: none;
            }}
            
            QCheckBox::indicator:checked:after {{
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
        """
    
    @staticmethod
    def get_chat_area_styles():
        """Area chat pulita"""
        return f"""
            QWidget#chatArea {{
                background-color: {StyleManager.COLORS['background']};
                border-left: 1px solid {StyleManager.COLORS['border']};
            }}
            
            QFrame#chatHeader {{
                background-color: {StyleManager.COLORS['background']};
                border-bottom: 1px solid {StyleManager.COLORS['border']};
            }}
            
            QLabel#chatTitle {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
                margin: 8px 0;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#typingIndicator {{
                color: {StyleManager.COLORS['success']};
                font-size: 12px;
                font-weight: 500;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#contextLabel {{
                color: {StyleManager.COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 500;
                background-color: {StyleManager.COLORS['surface']};
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid {StyleManager.COLORS['border_light']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QScrollArea#messagesScrollArea, QScrollArea#smartScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QWidget#messagesContainer {{
                background-color: transparent;
            }}
            
            QFrame#inputArea {{
                background-color: {StyleManager.COLORS['surface']};
                border-top: 1px solid {StyleManager.COLORS['border']};
            }}
        """
    
    @staticmethod
    def get_message_styles():
        """Messaggi puliti e leggibili"""
        return f"""
            QFrame#userMessage {{
                background-color: {StyleManager.COLORS['primary']};
                border: none;
                border-radius: 12px 12px 4px 12px;
                margin: 8px 60px 8px 8px;
                padding: 12px 16px;
            }}
            
            QFrame#assistantMessage {{
                background-color: {StyleManager.COLORS['surface']};
                border: 1px solid {StyleManager.COLORS['border_light']};
                border-radius: 12px 12px 12px 4px;
                margin: 8px 8px 8px 60px;
                padding: 12px 16px;
            }}
            
            QLabel#messageContent {{
                color: {StyleManager.COLORS['text_primary']}; /* Corretto: usa il colore del testo primario del tema */
                font-size: 13px;
                line-height: 1.5;
                background: transparent;
                border: none;
                font-weight: 400;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#userMessageContent {{
                color: {StyleManager.COLORS['text_primary']}; /* Usa il colore del testo primario del tema */
                font-size: 13px;
                line-height: 1.5;
                background: transparent;
                border: none;
                font-weight: 400;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#messageHeader {{
                color: {StyleManager.COLORS['text_muted']};
                font-size: 10px;
                font-weight: 600;
                margin-bottom: 6px;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#userMessageHeader {{
                color: rgba(255, 255, 255, 0.8);
                font-size: 10px;
                font-weight: 600;
                margin-bottom: 6px;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#statusIndicator {{
                color: {StyleManager.COLORS['success']};
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                background-color: {StyleManager.COLORS['success_light']};
                border-radius: 4px;
                border: 1px solid rgba(5, 150, 105, 0.2);
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @staticmethod
    def get_dialog_styles():
        """Dialog con design pulito, moderno e coesivo"""
        return f"""
            QDialog {{
                background-color: {StyleManager.COLORS['surface']};
                color: {StyleManager.COLORS['text_primary']};
                border-radius: 12px;
                border: 1px solid {StyleManager.COLORS['border']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            /* Header del Dialog */
            QFrame#dialogHeader {{
                background-color: transparent;
                border-bottom: 1px solid {StyleManager.COLORS['border']};
                border-radius: 0;
                padding: 10px 20px;
            }}
            
            QLabel#dialogIcon {{
                background-color: {StyleManager.COLORS['primary_light']};
                border-radius: 25px; /* Cerchio perfetto */
                font-size: 22px;
                color: {StyleManager.COLORS['primary']};
                font-family: {StyleManager.FONTS['emoji']};
                qproperty-alignment: 'AlignCenter';
            }}
            
            QLabel#dialogTitle {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 600;
                font-size: 18px;
                margin-left: 10px;
            }}
            
            /* Area Contenuto */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}

            QWidget#content_widget {{
                background-color: transparent;
            }}
            
            /* Stile per GroupBox pulito */
            QGroupBox, QGroupBox#formGroup {{
                font-weight: 600;
                color: {StyleManager.COLORS['text_primary']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 8px;
                margin-top: 20px;
                padding: 20px 15px 15px 15px;
                background-color: {StyleManager.COLORS['background']};
            }}
            
            QGroupBox::title, QGroupBox#formGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: -12px;
                padding: 4px 8px;
                background-color: {StyleManager.COLORS['surface']};
                color: {StyleManager.COLORS['text_secondary']};
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            /* Layout e Input */
            QFormLayout QLabel {{
                color: {StyleManager.COLORS['text_secondary']};
                font-weight: 500;
                font-size: 12px;
                padding-top: 5px;
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 400;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {StyleManager.COLORS['primary']};
                outline: none;
            }}

            /* Pulsanti nel Dialog */
            QDialogButtonBox {{
                dialog-button-box-spacing: 15px; /* Non funziona in Qt, si usa layout */
            }}

            QDialog .QPushButton {{
                 min-height: 30px; /* Altezza minima per i pulsanti nei dialog */
            }}

            /* Stile per TabWidget */
            QTabWidget::pane {{
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 8px;
                background-color: {StyleManager.COLORS['background']};
                margin-top: 5px;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {StyleManager.COLORS['text_secondary']};
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid transparent;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['primary']};
                border-color: {StyleManager.COLORS['border']};
                border-bottom-color: {StyleManager.COLORS['background']}; /* Nasconde il bordo inferiore */
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {StyleManager.COLORS['surface_hover']};
                color: {StyleManager.COLORS['text_primary']};
            }}
        """
    
    @staticmethod
    def get_tree_widget_styles():
        """Tree widget pulito"""
        return f"""
            QTreeWidget {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                font-size: 12px;
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 400;
                alternate-background-color: {StyleManager.COLORS['surface']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {StyleManager.COLORS['border_light']};
                border-radius: 0px;
                margin: 0px;
            }}
            
            QTreeWidget::item:selected {{
                background-color: {StyleManager.COLORS['primary']};
                color: white;
            }}
            
            QTreeWidget::item:hover {{
                background-color: {StyleManager.COLORS['surface']};
            }}
            
            QHeaderView::section {{
                background-color: {StyleManager.COLORS['surface']};
                border: none;
                border-bottom: 1px solid {StyleManager.COLORS['border']};
                border-right: 1px solid {StyleManager.COLORS['border_light']};
                padding: 8px 12px;
                font-weight: 600;
                color: {StyleManager.COLORS['text_primary']};
                font-size: 11px;
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @staticmethod
    def get_scrollbar_styles():
        """Scrollbar pulite"""
        return f"""
            QScrollBar:vertical {{
                background-color: {StyleManager.COLORS['surface']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
                border: none;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {StyleManager.COLORS['border']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {StyleManager.COLORS['text_muted']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            QScrollBar:horizontal {{
                background-color: {StyleManager.COLORS['surface']};
                height: 12px;
                border-radius: 6px;
                margin: 0;
                border: none;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {StyleManager.COLORS['border']};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {StyleManager.COLORS['text_muted']};
            }}
        """
    
    @staticmethod
    def get_status_bar_style():
        """Status bar pulita"""
        return f"""
            QStatusBar {{
                background-color: {StyleManager.COLORS['surface']};
                border-top: 1px solid {StyleManager.COLORS['border']};
                color: {StyleManager.COLORS['text_secondary']};
                font-weight: 500;
                font-size: 11px;
                padding: 4px 8px;
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @staticmethod
    def get_menu_bar_style():
        """Menu bar pulita"""
        return f"""
            QMenuBar {{
                background-color: {StyleManager.COLORS['background']};
                border-bottom: 1px solid {StyleManager.COLORS['border']};
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 500;
                font-size: 12px;
                padding: 4px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QMenuBar::item {{
                background: transparent;
                padding: 6px 12px;
                margin: 0px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {StyleManager.COLORS['surface']};
                color: {StyleManager.COLORS['text_primary']};
            }}
            
            QMenu {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                padding: 4px;
                color: {StyleManager.COLORS['text_primary']};
                font-size: 12px;
                font-weight: 400;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QMenu::item {{
                background: transparent;
                padding: 6px 16px;
                border-radius: 4px;
                margin: 1px;
            }}
            
            QMenu::item:selected {{
                background-color: {StyleManager.COLORS['primary']};
                color: white;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {StyleManager.COLORS['border']};
                margin: 4px 8px;
            }}
        """
    
    @staticmethod
    def get_progress_styles():
        """Progress bar pulita"""
        return f"""
            QProgressBar, QProgressBar#modernProgress {{
                background-color: {StyleManager.COLORS['surface']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 6px;
                text-align: center;
                font-size: 11px;
                font-weight: 500;
                color: {StyleManager.COLORS['text_primary']};
                height: 20px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QProgressBar::chunk, QProgressBar#modernProgress::chunk {{
                background-color: {StyleManager.COLORS['primary']};
                border-radius: 5px;
                margin: 1px;
            }}
        """
    
    @staticmethod
    def get_project_card_styles():
        """Project card pulite"""
        return f"""
            QFrame#projectCard {{
                background-color: {StyleManager.COLORS['background']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: 8px;
                margin: 8px;
                padding: 4px;
            }}
            
            QFrame#projectCard:hover {{
                border-color: {StyleManager.COLORS['primary']};
                background-color: {StyleManager.COLORS['surface']};
            }}
            
            QFrame#projectCardSelected {{
                background-color: {StyleManager.COLORS['primary_light']};
                border: 2px solid {StyleManager.COLORS['primary']};
                border-radius: 8px;
                margin: 8px;
                padding: 4px;
            }}
            
            QLabel#projectName {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 600;
                font-size: 14px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#projectDescription {{
                color: {StyleManager.COLORS['text_secondary']};
                font-size: 12px;
                font-weight: 400;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#projectDate, QLabel#projectFiles {{
                color: {StyleManager.COLORS['text_muted']};
                font-size: 11px;
                font-weight: 500;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#projectStatus {{
                background-color: {StyleManager.COLORS['success']};
                color: white;
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: 600;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel#projectIcon {{
                background-color: {StyleManager.COLORS['primary']};
                border-radius: 20px;
                color: white;
                font-size: 18px;
                padding: 8px;
                font-family: {StyleManager.FONTS['emoji']};
            }}

            /* Projects Panel Specific */
            QScrollArea#projectsScrollArea {{
                background-color: {StyleManager.COLORS['surface']};
                border: none;
            }}
            
            QWidget#projectsContainer {{
                background-color: {StyleManager.COLORS['surface']};
            }}
        """
    
    @staticmethod
    def get_form_styles():
        """Stili per form e labels"""
        return f"""
            QFormLayout QLabel {{
                color: {StyleManager.COLORS['text_primary']};
                font-weight: 500;
                font-size: 12px;
                font-family: {StyleManager.FONTS['primary']};
            }}
            
            QLabel {{
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
        """
    
    @classmethod
    def get_complete_stylesheet(cls):
        """Restituisce il foglio di stile completo PULITO e COERENTE"""
        return "".join([
            cls.get_main_window_style(),
            cls.get_sidebar_style(),
            cls.get_button_styles(),
            cls.get_input_styles(),
            cls.get_chat_area_styles(),
            cls.get_message_styles(),
            cls.get_dialog_styles(),
            cls.get_tree_widget_styles(),
            cls.get_scrollbar_styles(),
            cls.get_status_bar_style(),
            cls.get_menu_bar_style(),
            cls.get_progress_styles(),
            cls.get_project_card_styles(),
            cls.get_form_styles()
        ])


class DarkTheme(StyleManager):
    """Dark theme color palette."""
    COLORS = {
        'primary': '#3498db',
        'primary_hover': '#2980b9',
        'primary_light': '#2c3e50',
        'secondary': '#95a5a6',
        'success': '#2ecc71',
        'success_light': '#27ae60',
        'warning': '#f39c12',
        'warning_light': '#e67e22',
        'danger': '#e74c3c',
        'danger_light': '#c0392b',
        'background': '#1e293b',
        'surface': '#2c3e50',
        'surface_hover': '#34495e',
        'border': '#4a6572',
        'border_light': '#5e7a8c',
        'text_primary': '#ecf0f1',
        'text_secondary': '#bdc3c7',
        'text_muted': '#7f8c8d',
        'shadow': 'rgba(0, 0, 0, 0.4)',
        'shadow_light': 'rgba(0, 0, 0, 0.2)',
    }

class ThemeManager:
    """Gestore semplificato dei temi con coerenza completa"""
    
    def __init__(self, theme_name='light'):
        self.themes = {
            'light': StyleManager,
            'dark': DarkTheme,
        }
        self.set_theme(theme_name)
    
    def get_themed_stylesheet(self):
        """Genera il foglio di stile pulito e professionale"""
        return self.current_theme.get_complete_stylesheet()
    
    def set_theme(self, theme_name):
        """Imposta un tema"""
        self.current_theme = self.themes.get(theme_name, StyleManager)
        self.current_theme_name = theme_name
        return True
    
    def get_available_themes(self):
        """Restituisce i temi disponibili"""
        return [('light', 'Bianco Professionale'), ('dark', 'Scuro Moderno')]
    
    def get_color_palette(self):
        """Restituisce la palette di colori corrente"""
        return self.current_theme.COLORS.copy()
    
    def get_font_families(self):
        """Restituisce le famiglie di font utilizzate"""
        return self.current_theme.FONTS.copy()