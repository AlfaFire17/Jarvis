import re
from core.logger import logger

class Intent:
    GREETING = "greeting"
    OPEN_PERPLEXITY = "open_perplexity"
    OPEN_YOUTUBE = "open_youtube"
    OPEN_APP = "open_app"  # Replaces OPEN_STEAM for broader compatibility
    CLOSE_APP = "close_app"
    OPEN_FOLDER = "open_folder"
    SEARCH_FILE = "search_file"
    OPEN_FILE = "open_file"
    SYSTEM_ACTION = "system_action"
    PLAY_SPOTIFY = "play_spotify"
    GET_TIME = "get_time"
    GET_DATE = "get_date"
    GET_WEATHER = "get_weather"
    SHUTDOWN = "shutdown"
    CANCEL_SHUTDOWN = "cancel_shutdown"
    GET_RECENT_MEMORY = "get_recent_memory"
    SEARCH_MEMORY = "search_memory"
    CHECK_LAST_COMMAND = "check_last_command"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"

class IntentRouter:
    def __init__(self):
        # Reglas con posibles grupos de captura para extraer nombres de juegos, canciones o ciudades
        self.rules = {
            Intent.GREETING: [r"hola", r"buenos d[ía]as", r"qu[ée] tal", r"saludos", r"buenas noches"],
            Intent.SHUTDOWN: [r"apaga el equipo", r"apaga el sistema", r"apaga el ordenador", r"apágate"],
            Intent.CANCEL_SHUTDOWN: [r"cancela apagado", r"cancela el apagado", r"aborta apagado"],
            Intent.SYSTEM_ACTION: [r"bloquea el ordenador", r"abre (?:el )?administrador de tareas", r"abre (?:la )?configuración"],
            Intent.GET_RECENT_MEMORY: [r"últimas conversaciones", r"qu[ée] hice hoy", r"qu[ée] hicimos hoy"],
            Intent.CHECK_LAST_COMMAND: [r"último comando", r"lo último que me dijiste", r"qu[ée] fue lo último"],
            Intent.SEARCH_MEMORY: [r"qu[ée] me dijiste sobre (.+)", r"qu[ée] hablamos de (.+)"],
            Intent.OPEN_PERPLEXITY: [r"abre perplexity", r"abre el buscador"],
            Intent.OPEN_YOUTUBE: [r"abre youtube"],
            Intent.GET_TIME: [r"qu[ée]\s+hora\s+es"],
            Intent.GET_DATE: [r"qu[ée]\s+d[ía]a\s+es\s+hoy"],
            Intent.GET_WEATHER: [r"clima\s+(.+)"],
            Intent.PLAY_SPOTIFY: [r"pon\s+(.+)"],
            Intent.CLOSE_APP: [r"cierra\s+(.+)"],
            Intent.OPEN_FOLDER: [r"abre\s+(descargas|documentos|escritorio|im[áa]genes|mis im[áa]genes|la carpeta del proyecto|proyecto|actual|jarvis)(?!.*archivo)(?!.*programa)"],
            Intent.OPEN_FILE: [r"abre el archivo\s+(.+)"],
            Intent.SEARCH_FILE: [r"(?:busca(?: el archivo)?|encuentra(?: el archivo)?)\s+(.+)"],
            # Catch-all para apertura de programas y Steam fallback
            Intent.OPEN_APP: [r"abre\s+(?!el archivo\b)(?!el ordenador\b)(?!el administrador\b)(?!la configuración\b)(?!youtube\b)(?!perplexity\b)(?!descargas\b)(?!documentos\b)(?!escritorio\b)(?!im[áa]genes\b)(?!mis im[áa]genes\b)(?!proyecto\b)(?!actual\b)(?!jarvis\b)(.+)"],
        }

    def route(self, text):
        """Clasifica el texto en una intención y extrae el payload si existe."""
        if not text or len(text.strip()) == 0:
            return Intent.UNKNOWN, None

        text = text.lower().strip()
        logger.info(f"Analizando intención para: '{text}'")

        for intent, patterns in self.rules.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    # Si hay un grupo de captura, lo extraemos como payload
                    payload = match.group(1) if match.groups() else None
                    logger.info(f"Intención detectada: {intent} (Payload: {payload})")
                    return intent, payload

        # Si no coincide con nada local, lo tratamos como consulta general
        logger.info(f"Intención por defecto: {Intent.GENERAL_QUERY}")
        return Intent.GENERAL_QUERY, text

