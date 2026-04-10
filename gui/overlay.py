import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Slot, Property
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QFont

class JARVISOverlay(QWidget):
    def __init__(self, controller):
        super().__init__()
        
        # Conectar las señales del controlador a los métodos (Slots)
        self.controller = controller
        self.controller.set_idle.connect(self.set_state_idle)
        self.controller.set_wake.connect(self.set_state_wake)
        self.controller.set_listening.connect(self.set_state_listening)
        self.controller.set_transcription.connect(self.set_state_transcription)
        self.controller.set_responding.connect(self.set_state_responding)
        
        self.init_ui()

    def init_ui(self):
        # Propiedades de la ventana: Frameless, Always on Top, Tool (no taskbar)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # Transparente, no roba click
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Tamaño y posición
        screen = QApplication.primaryScreen().geometry()
        width = 400
        height = 150
        # Esquina inferior derecha:
        self.setGeometry(screen.width() - width - 50, screen.height() - height - 80, width, height)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        self.setLayout(self.layout)

        # Etiqueta principal (transcripción)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                color: #FF8800;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                background-color: rgba(0, 0, 0, 160);
                padding: 10px;
                border-radius: 10px;
                border: 1px solid rgba(255, 136, 0, 100);
            }
        """)
        self.layout.addWidget(self.label)
        self.label.hide()

        # Variable de estado para controlar el pintado del círculo
        self.is_active = False

        # Animación de opacidad para el fade-in / fade-out
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Iniciar oculto
        self.setWindowOpacity(0.0)

    # El evento paintEvent dibuja el círculo naranja cuando está activo
    def paintEvent(self, event):
        if not self.is_active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Configurar gradiente del círculo
        center = self.rect().center()
        # Dibujamos un poco más arriba de la etiqueta
        center.setY(center.y() - 20)
        radius = 25

        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(255, 200, 50, 255))
        gradient.setColorAt(0.7, QColor(255, 136, 0, 200))
        gradient.setColorAt(1, QColor(255, 136, 0, 0))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        # Dibujamos el halo
        painter.drawEllipse(center, radius + 15, radius + 15)

        # Círculo sólido interior
        painter.setBrush(QColor(255, 136, 0, 255))
        painter.drawEllipse(center, radius, radius)
        
        painter.end()

    @Slot()
    def fade_in(self):
        self.show()
        self.opacity_anim.setStartValue(self.windowOpacity())
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

    @Slot()
    def fade_out(self):
        self.opacity_anim.setStartValue(self.windowOpacity())
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.start()
        # Al finalizar, la ventana sigue existiendo pero con opacidad 0

    @Slot()
    def set_state_idle(self):
        self.is_active = False
        self.label.hide()
        self.update() # Llama al paintEvent para borrar el círculo
        self.fade_out()

    @Slot()
    def set_state_wake(self):
        self.is_active = True
        self.label.setText("JARVIS")
        self.label.setStyleSheet("color: #FF8800; font-size: 18px; font-weight: bold;")
        self.label.show()
        self.update()
        self.fade_in()

    @Slot()
    def set_state_listening(self):
        self.label.setText("Escuchando orden...")
        self.label.setStyleSheet("color: #FFDDAA; font-style: italic; font-size: 16px;")

    @Slot(str)
    def set_state_transcription(self, text):
        self.label.setText(f'"{text}"')
        self.label.setStyleSheet("color: #FFFFFF; font-size: 16px;")

    @Slot(str)
    def set_state_responding(self, text):
        # Truncar visualmente si es muy largo para la UI
        display_text = text if len(text) < 150 else text[:147] + "..."
        self.label.setText(display_text)
        self.label.setStyleSheet("color: #FFCC88; font-size: 16px;")
        
        # Schedule idle state after 5 seconds to show the response before hiding
        QTimer.singleShot(5000, self.set_state_idle)
