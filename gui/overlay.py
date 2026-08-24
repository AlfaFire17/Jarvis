import os
import math
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, Slot, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QFont, QBrush, QPen, QPainterPath

class ALFAOverlay(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Geometría inicial
        self.setGeometry(100, 100, 420, 420)
        
        # Estados internos visuales
        self.opacity = 0.0
        self.target_opacity = 0.0
        self.state = "idle"
        self.text_display = ""
        self.status_display = ""
        self.perf_display = ""
        self.pulse_phase = 0.0

        # Conectar señales del controlador
        self.controller.set_idle.connect(self.on_idle)
        self.controller.set_wake.connect(self.on_wake)
        self.controller.set_listening.connect(self.on_listening)
        self.controller.set_transcription.connect(self.on_transcription)
        self.controller.set_responding.connect(self.on_responding)
        self.controller.set_muted.connect(self.on_muted)
        self.controller.set_conversation_mode.connect(self.on_conversation)
        self.controller.set_analyzing.connect(self.on_analyzing)
        self.controller.set_status_text.connect(self.on_status_text)
        self.controller.set_perf_status.connect(self.on_perf_status)

        # Timer para animación a ~60 fps
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16)
        
        self.init_ui()

    def init_ui(self):
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

    @Slot(str)
    def on_status_text(self, text):
        self.status_display = text
        self.update()

    @Slot(str)
    def on_perf_status(self, text):
        self.perf_display = text
        self.update()

    def auto_fade_out(self):
        if self.state == "responding":
            self.on_idle()

    def animate(self):
        # Transición suave de opacidad
        diff = self.target_opacity - self.opacity
        if abs(diff) > 0.01:
            self.opacity += diff * 0.1
            self.update()
        else:
            self.opacity = self.target_opacity
            if self.opacity > 0 or self.state != "idle":
                self.update()
        
        # Animación de pulso
        self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)

    def paintEvent(self, event):
        if self.opacity <= 0.01:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pulse = (math.sin(self.pulse_phase) + 1.0) / 2.0  # [0.0, 1.0]

        # Definición de paleta de colores rojos A.L.F.A. según estado
        bg_alpha = int(220 * self.opacity)

        # Colores por estado (Rojo primario)
        if self.state == "muted":
            alpha_color = QColor(160, 60, 60, int(220 * self.opacity))
            glow_center = QColor(120, 30, 30, int(120 * self.opacity))
            ring_color = QColor(100, 40, 40, int(150 * self.opacity))
        elif self.state == "listening":
            # Rojo vivo pulsatil
            g_val = int(30 + 40 * pulse)
            alpha_color = QColor(255, g_val, 50, int(255 * self.opacity))
            glow_center = QColor(255, 0, 40, int((150 + 60 * pulse) * self.opacity))
            ring_color = QColor(255, 30, 60, int((180 + 70 * pulse) * self.opacity))
        elif self.state == "conversing":
            # Rojo carmesí profundo con toques magenta
            alpha_color = QColor(255, 40, 100, int(240 * self.opacity))
            glow_center = QColor(220, 10, 80, int(140 * self.opacity))
            ring_color = QColor(255, 20, 90, int(160 * self.opacity))
        elif self.state == "responding":
            alpha_color = QColor(255, 50, 50, int(255 * self.opacity))
            glow_center = QColor(255, 20, 30, int(160 * self.opacity))
            ring_color = QColor(255, 60, 60, int(200 * self.opacity))
        elif self.state == "analyzing":
            # Verde esmeralda para análisis visual
            alpha_color = QColor(0, 255, 140, int(255 * self.opacity))
            glow_center = QColor(0, 200, 100, int(140 * self.opacity))
            ring_color = QColor(0, 255, 120, int(180 * self.opacity))
        else: # idle / wake
            alpha_color = QColor(220, 20, 40, int(220 * self.opacity))
            glow_center = QColor(180, 10, 30, int(100 * self.opacity))
            ring_color = QColor(200, 20, 40, int(120 * self.opacity))

        rect = self.rect()
        center = QPointF(rect.width() / 2.0, rect.height() / 2.0 - 20)

        # 1. Dibujar halo / glow radial
        glow_radius = 120 + (10 * pulse if self.state == "listening" else 0)
        gradient = QRadialGradient(center, glow_radius)
        gradient.setColorAt(0.0, glow_center)
        gradient.setColorAt(0.6, QColor(glow_center.red(), glow_center.green(), glow_center.blue(), int(40 * self.opacity)))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)

        # 2. Dibujar anillo tecnológico externo
        ring_pen = QPen(ring_color, 2, Qt.PenStyle.DashLine if self.state == "listening" else Qt.PenStyle.SolidLine)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, 75, 75)

        # 3. Renderizar el símbolo α central (Letra Griega Alfa)
        font_alpha = QFont("Segoe UI", 72, QFont.Weight.Bold)
        painter.setFont(font_alpha)
        painter.setPen(alpha_color)
        
        alpha_text = "α"
        fm_alpha = painter.fontMetrics()
        alpha_rect = fm_alpha.boundingRect(alpha_text)
        alpha_x = center.x() - alpha_rect.width() / 2.0 - alpha_rect.left()
        alpha_y = center.y() + alpha_rect.height() / 4.0

        painter.drawText(int(alpha_x), int(alpha_y), alpha_text)

        # 4. Dibujar marca "A.L.F.A." justo debajo del símbolo α
        font_brand = QFont("Segoe UI", 13, QFont.Weight.DemiBold)
        font_brand.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        painter.setFont(font_brand)
        painter.setPen(QColor(255, 255, 255, int(220 * self.opacity)))
        
        brand_text = "A.L.F.A."
        fm_brand = painter.fontMetrics()
        brand_rect = fm_brand.boundingRect(brand_text)
        brand_x = center.x() - brand_rect.width() / 2.0
        brand_y = center.y() + 65

        painter.drawText(int(brand_x), int(brand_y), brand_text)

        # 5. Dibujar Texto de Transcripción / Respuesta debajo del HUD
        if self.text_display:
            font_text = QFont("Segoe UI", 12, QFont.Weight.Normal)
            painter.setFont(font_text)
            painter.setPen(QColor(240, 240, 245, int(255 * self.opacity)))
            text_box = rect.adjusted(20, int(rect.height() * 0.72), -20, -30)
            painter.drawText(
                text_box,
                int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap),
                self.text_display
            )
            
        # 6. Status e IA (Fase 11) - Esquina inferior derecha
        if self.status_display or self.perf_display:
            font_small = QFont("Segoe UI", 9, QFont.Weight.Normal)
            painter.setFont(font_small)
            painter.setPen(QColor(200, 200, 210, int(160 * self.opacity)))
            info_text = f"{self.status_display} | {self.perf_display}"
            painter.drawText(
                rect.adjusted(0, 0, -15, -10),
                int(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight),
                info_text
            )

        painter.end()
