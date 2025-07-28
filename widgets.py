#!/usr/bin/env python3
"""
Widget personalizzati per Ollama Chat GUI
Componenti UI riutilizzabili e ottimizzati con stile coerente
"""

import os
import math
from datetime import datetime
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QWidget, QScrollArea, QSizePolicy, QProgressBar,
    QPlainTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QTextCursor, QPixmap, QPainter, QColor


class AnimatedWidget(QWidget):
    """Widget base con supporto per animazioni"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        
    def fade_in(self, duration=300):
        """Animazione di fade in"""
        if self.animation:
            self.animation.stop()
            
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
    
    def fade_out(self, duration=300):
        """Animazione di fade out"""
        if self.animation:
            self.animation.stop()
            
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.start()


class MessageWidget(AnimatedWidget):
    """Widget ottimizzato per visualizzare i messaggi della chat"""
    
    def __init__(self, message: str, is_user: bool = True, 
                 timestamp: str = None, settings: dict = None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.settings = settings or {}
        self.is_streaming = False
        
        self.setup_ui()
        self.fade_in(200)
    
    def setup_ui(self):
        """Configura l'interfaccia del widget messaggio"""
        self.setObjectName("userMessage" if self.is_user else "assistantMessage")
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container del messaggio
        message_container = QFrame()
        message_container.setObjectName("messageContainer")
        container_layout = QVBoxLayout(message_container)
        container_layout.setContentsMargins(15, 12, 15, 12)
        container_layout.setSpacing(8)
        
        # Header con timestamp se abilitato
        if self.settings.get("show_timestamps", True):
            header = self.create_header()
            container_layout.addWidget(header)
        
        # Contenuto del messaggio
        self.content_label = QLabel(self.message)
        self.content_label.setObjectName(
            "userMessageContent" if self.is_user else "messageContent"
        )
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Font basato sulle impostazioni - usa Segoe UI coerentemente
        font_size = self.settings.get("font_size", 13)
        font = QFont("Segoe UI", font_size, QFont.Weight.Normal)
        self.content_label.setFont(font)
        
        container_layout.addWidget(self.content_label)
        
        # Indicatore di stato per messaggi in streaming
        self.status_indicator = QLabel()
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setVisible(False)
        # Usa colori coerenti con il sistema
        self.status_indicator.setStyleSheet("""
            QLabel#statusIndicator {
                color: #059669;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                background-color: rgba(5, 150, 105, 0.1);
                border-radius: 4px;
                border: 1px solid rgba(5, 150, 105, 0.2);
            }
        """)
        container_layout.addWidget(self.status_indicator)
        
        layout.addWidget(message_container)
        
        # Imposta politiche di dimensionamento
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    
    def create_header(self):
        """Crea l'header del messaggio con timestamp"""
        header = QLabel()
        header.setObjectName(
            "userMessageHeader" if self.is_user else "messageHeader"
        )
        
        role_text = "👤 Tu" if self.is_user else "🤖 Assistente"
        header_text = f"{role_text} • {self.timestamp}"
        
        header.setText(header_text)
        # Font coerente con il sistema
        header.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        
        return header
    
    def update_content(self, new_content: str):
        """Aggiorna il contenuto del messaggio (per streaming)"""
        self.message = new_content
        self.content_label.setText(new_content)
        
        # Mostra indicatore di streaming
        if not self.is_streaming and not self.is_user:
            self.is_streaming = True
            self.status_indicator.setText("⌛ Generando...")
            self.status_indicator.setVisible(True)
    
    def finalize_message(self):
        """Finalizza il messaggio (fine streaming)"""
        self.is_streaming = False
        self.status_indicator.setVisible(False)
    
    def get_message_data(self):
        """Restituisce i dati del messaggio per il salvataggio"""
        return {
            "role": "user" if self.is_user else "assistant",
            "content": self.message,
            "timestamp": self.timestamp
        }
    
    def set_error_state(self, error_message: str = None):
        """Imposta lo stato di errore per il messaggio"""
        if not self.is_user:
            error_text = error_message or "❌ Errore nella generazione"
            self.content_label.setText(error_text)
            # Usa colore di errore coerente
            self.content_label.setStyleSheet("color: #dc2626; font-weight: 500;")
            self.finalize_message()


class ProjectCard(AnimatedWidget):
    """Card moderna per rappresentare un progetto"""
    
    clicked = pyqtSignal(object)  # Emesso quando la card viene cliccata
    
    def __init__(self, project_data: dict, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.is_selected = False
        self.setup_ui()
        self.fade_in(150)
    
    def setup_ui(self):
        """Configura l'interfaccia della card"""
        self.setObjectName("projectCard")
        self.setFixedHeight(140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Header con nome e icona
        header_layout = QHBoxLayout()
        
        # Icona del progetto - usa colori coerenti
        icon_label = QLabel("📁")
        icon_label.setObjectName("projectIcon")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Info progetto
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nome progetto - usa font coerente
        name_label = QLabel(self.project_data['name'])
        name_label.setObjectName("projectName")
        name_font = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        
        # Descrizione - usa font coerente
        desc_text = self.project_data.get('description', 'Nessuna descrizione')
        
        desc_label = QLabel(desc_text)
        desc_label.setObjectName("projectDescription")
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        desc_label.setMaximumHeight(35)
        desc_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        
        # Badge stato - usa colori coerenti
        status_badge = QLabel("🟢 Attivo")
        status_badge.setObjectName("projectStatus")
        status_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)
        
        layout.addLayout(header_layout)
        
        # Footer con statistiche
        footer_layout = QHBoxLayout()
        
        # Data creazione
        created_date = self.project_data.get('created_at', 'Sconosciuta')
        if isinstance(created_date, str) and len(created_date) > 10:
            created_date = created_date[:10]
        
        date_label = QLabel(f"📅 {created_date}")
        date_label.setObjectName("projectDate")
        date_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        
        # File count (sarà aggiornato dal genitore)
        self.files_label = QLabel("📄 0 file")
        self.files_label.setObjectName("projectFiles")
        self.files_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        
        footer_layout.addWidget(date_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.files_label)
        
        layout.addLayout(footer_layout)
        
        # Applica stili dal sistema centralizzato
        self.update_style()
        # Force style refresh per assicurarsi che vengano applicati
        self.style().unpolish(self)
        self.style().polish(self)
    
    def update_style(self):
        """Aggiorna lo stile della card basato sullo stato di selezione"""
        if self.is_selected:
            self.setObjectName("projectCardSelected")
        else:
            self.setObjectName("projectCard")
        
        # Forza l'aggiornamento del stylesheet
        parent_widget = self.parent()
        if parent_widget:
            parent_widget.setStyleSheet(parent_widget.styleSheet())
    
    def set_selected(self, selected: bool):
        """Imposta lo stato di selezione della card"""
        self.is_selected = selected
        self.update_style()
    
    def update_files_count(self, count: int):
        """Aggiorna il conteggio dei file"""
        self.files_label.setText(f"📄 {count} file")
    
    def mousePressEvent(self, event):
        """Gestisce il click sulla card"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)


class LoadingIndicator(QWidget):
    """Indicatore di caricamento animato con colori coerenti"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.setFixedSize(40, 40)
        # Usa colore primario coerente
        self.primary_color = QColor(37, 99, 235)  # #2563eb
    
    def start(self):
        """Avvia l'animazione"""
        self.timer.start(50)
        self.show()
    
    def stop(self):
        """Ferma l'animazione"""
        self.timer.stop()
        self.hide()
    
    def rotate(self):
        """Ruota l'indicatore"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """Disegna l'indicatore"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Centro
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 5
        
        # Disegna i punti
        for i in range(8):
            angle = (self.angle + i * 45) * 3.14159 / 180
            x = center.x() + radius * 0.7 * cos(angle)
            y = center.y() + radius * 0.7 * sin(angle)
            
            # Alpha basato sulla posizione
            alpha = int(255 * (i + 1) / 8)
            color = QColor(self.primary_color.red(), self.primary_color.green(), 
                          self.primary_color.blue(), alpha)
            painter.setBrush(color)
            painter.setPen(color)
            
            painter.drawEllipse(int(x-3), int(y-3), 6, 6)


class CustomProgressBar(QProgressBar):
    """Progress bar personalizzata con stili coerenti"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernProgress")
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Font coerente
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))


class CollapsibleSection(QWidget):
    """Sezione collassabile per organizzare l'interfaccia"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = True
        self.animation = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della sezione"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header cliccabile
        self.header = QPushButton(f"▼ {self.title}")
        self.header.setObjectName("sectionHeader")
        # Font coerente
        self.header.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.header.clicked.connect(self.toggle_expanded)
        
        # Contenuto
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 5, 10, 5)
        
        layout.addWidget(self.header)
        layout.addWidget(self.content_widget)
    
    def add_widget(self, widget):
        """Aggiunge un widget al contenuto della sezione"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Aggiunge un layout al contenuto della sezione"""
        self.content_layout.addLayout(layout)
    
    def toggle_expanded(self):
        """Cambia lo stato di espansione"""
        self.set_expanded(not self.is_expanded)
    
    def set_expanded(self, expanded: bool):
        """Imposta lo stato di espansione"""
        self.is_expanded = expanded
        
        # Aggiorna icona
        icon = "▼" if expanded else "▶"
        self.header.setText(f"{icon} {self.title}")
        
        # Anima il contenuto
        if self.animation:
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if expanded:
            # Espandi
            self.content_widget.setMaximumHeight(0)
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_widget.sizeHint().height())
        else:
            # Collassa
            self.animation.setStartValue(self.content_widget.height())
            self.animation.setEndValue(0)
        
        self.animation.start()


class SmartScrollArea(QScrollArea):
    """ScrollArea con comportamenti intelligenti"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("smartScrollArea")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Timer per smooth scrolling
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.smooth_scroll_step)
        self.target_value = 0
        self.current_value = 0
        self.scroll_speed = 0
    
    def smooth_scroll_to_bottom(self):
        """Scorre dolcemente fino in fondo"""
        scrollbar = self.verticalScrollBar()
        self.target_value = scrollbar.maximum()
        self.current_value = scrollbar.value()
        
        if self.target_value != self.current_value:
            self.scroll_speed = max(1, abs(self.target_value - self.current_value) // 10)
            self.scroll_timer.start(16)  # ~60fps
    
    def smooth_scroll_step(self):
        """Step dell'animazione di scroll"""
        scrollbar = self.verticalScrollBar()
        
        if self.current_value < self.target_value:
            self.current_value = min(self.target_value, self.current_value + self.scroll_speed)
        elif self.current_value > self.target_value:
            self.current_value = max(self.target_value, self.current_value - self.scroll_speed)
        
        scrollbar.setValue(int(self.current_value))
        
        if self.current_value == self.target_value:
            self.scroll_timer.stop()
    
    def scroll_to_bottom(self):
        """Scorre immediatamente in fondo"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def cos(angle):
    """Coseno per l'indicatore di caricamento"""
    import math
    return math.cos(angle)

def sin(angle):
    """Seno per l'indicatore di caricamento"""
    import math
    return math.sin(angle)