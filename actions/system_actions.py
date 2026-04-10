import os
import subprocess
import webbrowser
from core.config import Config
from core.logger import logger

def open_url(url, browser_path=None):
    """Abre una URL en el navegador especificado o el predeterminado."""
    try:
        if browser_path and os.path.exists(browser_path):
            logger.info(f"Abriendo {url} con {browser_path}")
            subprocess.Popen([browser_path, url])
            return True
        else:
            logger.info(f"Abriendo {url} con el navegador predeterminado.")
            webbrowser.open(url)
            return True
    except Exception as e:
        logger.error(f"Error abriendo URL {url}: {e}")
        return False

def open_perplexity():
    """Acción: Abre Perplexity AI."""
    return open_url(Config.PERPLEXITY_URL, Config.OPERA_PATH)

def open_youtube():
    """Acción: Abre YouTube."""
    return open_url(Config.YOUTUBE_URL, Config.OPERA_PATH)

def say_hello():
    """Acción: Responde con un saludo."""
    return "Hola señor, ¿en qué puedo ayudarle hoy?"

def no_command_response():
    """Acción: Respuesta cuando no se entiende la orden."""
    return "No he podido entender ninguna orden clara, señor."
