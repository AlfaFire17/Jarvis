import keyboard
from core.logger import logger
import threading

class JARVISHotkeyManager:
    """Registra y gestiona el hotkey global en Windows."""
    def __init__(self, conversation_manager):
        self.conv_manager = conversation_manager
        
    def start(self):
        """Intenta asociar el atajo de teclado F4 de forma global."""
        def mute_callback():
            self.conv_manager.toggle_mute()

        try:
            # F4 actuará a nivel global en Windows
            keyboard.add_hotkey("F4", mute_callback)
            logger.info("Hotkey global F4 registrado exitosamente para Mute.")
        except Exception as e:
            logger.error(f"Error registrando el hotkey F4 (posible falta de permisos Admin): {e}")
            logger.warning("Intentando un atajo alternativo si F4 falla...")
            try:
                keyboard.add_hotkey("ctrl+shift+m", mute_callback)
                logger.info("Hotkey alternativo Ctrl+Shift+M activo para Mute.")
            except Exception as e2:
                logger.error(f"También falló el atajo secundario. Mute de teclado deshabilitado: {e2}")

