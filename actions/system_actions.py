import os
import subprocess
from core.config import Config
from core.logger import logger

def open_browser_with_urls():
    """Abre Opera GX con las URLs de Perplexity y YouTube."""
    try:
        if os.path.exists(Config.OPERA_PATH):
            logger.info("Abriendo Opera GX con protocolos iniciales...")
            subprocess.Popen([Config.OPERA_PATH, Config.PERPLEXITY_URL])
            subprocess.Popen([Config.OPERA_PATH, Config.YOUTUBE_URL])
            return True
        else:
            logger.warning(f"Error: Opera GX no encontrado en {Config.OPERA_PATH}")
            # Intento de fallback al navegador predeterminado del sistema si falla
            import webbrowser
            webbrowser.open(Config.PERPLEXITY_URL)
            webbrowser.open(Config.YOUTUBE_URL)
            return True
    except Exception as e:
        logger.error(f"Error abriendo apps: {e}")
        return False

def say_hello():
    """Acción simple de saludo."""
    return Config.GREETING_TEXT
