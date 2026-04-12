import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, Slot
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QFont, QBrush

class JARVISOverlay(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Geometría inicial
        self.setGeometry(100, 100, 400, 400)
        
        # Estados internos Visuales
        self.opacity = 0.0
        self.target_opacity = 0.0
        self.state = "idle"
        self.text_display = ""

        # Conectar señales del nuevo controlador
        self.controller.set_idle.connect(self.on_idle)
        self.controller.set_wake.connect(self.on_wake)
        self.controller.set_listening.connect(self.on_listening)
        self.controller.set_transcription.connect(self.on_transcription)
        self.controller.set_responding.connect(self.on_responding)
        self.controller.set_muted.connect(self.on_muted)
        self.controller.set_conversation_mode.connect(self.on_conversation)
        self.controller.set_analyzing.connect(self.on_analyzing)

        # Timer para animación
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16) # ~60 fps
        
        self.init_ui()

    def init_ui(self):
        # Propiedades de la ventana: Frameless, Always on Top, Tool (no taskbar, transparente)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.moveToBottomRight()

    def moveToBottomRight(self):
        screen = QApplication.primaryScreen()
        size = screen.size()
        margin_x = 50
        margin_y = 100
        x = size.width() - self.width() - margin_x
        y = size.height() - self.height() - margin_y
        self.move(x, y)

    # ---------- Slots de cambio de estado ----------
    @Slot()
    def on_idle(self):
        self.state = "idle"
        self.target_opacity = 0.0

    @Slot()
    def on_wake(self):
        self.state = "wake"
        self.target_opacity = 0.9
        self.text_display = ""
        self.show()
        
    @Slot()
    def on_listening(self):
        self.state = "listening"
        self.target_opacity = 1.0
        self.text_display = "Escuchando..."
        self.show()

    @Slot(str)
    def on_transcription(self, text):
        self.text_display = text
        
    @Slot(str)
    def on_responding(self, text):
        self.state = "responding"
        self.text_display = text if len(text) < 150 else text[:147] + "..."
        self.target_opacity = 1.0
        # Timer para apagar la UI después de un mensaje si no salta el modo conversacion
        QTimer.singleShot(6000, self.auto_fade_out)
        self.show()
        
    @Slot()
    def on_muted(self):
        self.state = "muted"
        self.target_opacity = 0.7
        self.text_display = "[MUTED]"
        self.show()
        
    @Slot()
    def on_conversation(self):
        self.state = "conversing"
        self.target_opacity = 0.8
        self.text_display = "Conversación activa..."
        self.show()

    @Slot(str)
    def on_analyzing(self, text):
        self.state = "analyzing"
        self.target_opacity = 0.9
        self.text_display = text if text else "Analizando pantalla..."
        self.show()

    def auto_fade_out(self):
        if self.state == "responding":
            self.on_idle()

    def animate(self):
        # Suavizar transición de opacidad real (60fps lerp)
        diff = self.target_opacity - self.opacity
        if abs(diff) > 0.01:
            self.opacity += diff * 0.1
            self.update()
        else:
            self.opacity = self.target_opacity
            if self.opacity > 0 or self.state != "idle":
                self.update()

    def paintEvent(self, event):
        if self.opacity <= 0.01:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Configuración de colores
        center_color = QColor(255, 120, 0, int(200 * self.opacity))
        mid_color = QColor(255, 50, 0, int(100 * self.opacity))
        glow_color = QColor(255, 0, 0, 0)
        font_color = QColor(255, 255, 255, int(255 * self.opacity))
        
        if self.state == "muted":
            center_color = QColor(150, 0, 0, int(180 * self.opacity))
            mid_color = QColor(80, 0, 0, int(90 * self.opacity))
            font_color = QColor(200, 200, 200, int(255 * self.opacity))
        elif self.state == "conversing":
            center_color = QColor(0, 200, 255, int(180 * self.opacity))
            mid_color = QColor(0, 100, 200, int(90 * self.opacity))
        elif self.state == "listening":
            center_color = QColor(255, 180, 0, int(240 * self.opacity))
            mid_color = QColor(255, 80, 0, int(150 * self.opacity))
        elif self.state == "analyzing":
            # Verde esmeralda para visión
            center_color = QColor(0, 255, 120, int(200 * self.opacity))
            mid_color = QColor(0, 180, 80, int(100 * self.opacity))

        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2.5

        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, center_color)
        gradient.setColorAt(0.5, mid_color)
        gradient.setColorAt(1.0, glow_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        # Dibujar Texto debajo del HUD
        if self.text_display:
            font = QFont("Arial", 14, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(font_color)
            text_rect = rect.adjusted(0, int(rect.height() * 0.7), 0, 0)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap),
                self.text_display
            )
        painter.end()
