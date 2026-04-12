import time
import threading
from core.logger import logger

class ConversationManager:
    """
    Gestiona los estados de la conversación híbrida,
    como el mute global, el estado de auto-hablado,
    y la ventana de tiempo de "escucha atenta".
    """
    def __init__(self, gui_controller):
        self.gui_controller = gui_controller
        self.is_muted = False
        self.is_speaking = False
        self.in_conversation = False
        self.last_activity_time = 0.0
        self.conversation_timeout = 20.0  # 20 segundos de vigencia sin wake word
        
    def reset_activity_timer(self):
        """Reinicia el reloj de la conversación."""
        self.last_activity_time = time.time()
        
    def start_conversation(self):
        """Inicia el modo de conversación híbrida."""
        if self.is_muted:
            return False
            
        self.in_conversation = True
        self.reset_activity_timer()
        self.gui_controller.set_conversation_mode.emit()
        logger.info("Modo conversación híbrida activado.")
        return True
        
    def stop_conversation(self):
        """Forza la salida del modo conversación."""
        if self.in_conversation:
            self.in_conversation = False
            # Volvemos a modo neutral visual (Idle)
            self.gui_controller.set_idle.emit()
            logger.info("Modo conversación híbrida detenido.")
        
    def set_speaking(self, status: bool):
        """Marca a JARVIS como hablando o no."""
        self.is_speaking = status
        
    def toggle_mute(self):
        """Alterna el silencio absoluto vía Hotkey."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_conversation()
            self.gui_controller.set_muted.emit()
            logger.info("Sistema MUTEADO globalmente.")
        else:
            self.gui_controller.set_idle.emit()
            logger.info("Sistema DESMUTEADO globalmente.")
        return self.is_muted

    def is_conversation_active(self):
        """Verifica si seguimos dentro del timeout de la conversación."""
        if not self.in_conversation:
            return False
        
        # Si caducó
        if time.time() - self.last_activity_time > self.conversation_timeout:
            self.stop_conversation()
            return False
            
        return True
