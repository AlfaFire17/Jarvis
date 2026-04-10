import re
from core.logger import logger

class Intent:
    GREETING = "greeting"
    OPEN_PERPLEXITY = "open_perplexity"
    OPEN_YOUTUBE = "open_youtube"
    OPEN_STEAM = "open_steam"
    PLAY_SPOTIFY = "play_spotify"
    GET_TIME = "get_time"
    GET_DATE = "get_date"
    GET_WEATHER = "get_weather"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"

class IntentRouter:
    def __init__(self):
        # Reglas con posibles grupos de captura para extraer nombres de juegos, canciones o ciudades
        self.rules = {
            Intent.GREETING: [r"hola", r"buenos d[ía]as", r"qu[ée] tal", r"saludos"],
            Intent.OPEN_PERPLEXITY: [r"abre perplexity", r"abre el buscador"],
            Intent.OPEN_YOUTUBE: [r"abre youtube"],
            Intent.GET_TIME: [r"qu[ée]\s+hora\s+es"],
            Intent.GET_DATE: [r"qu[ée]\s+d[ía]a\s+es\s+hoy"],
            Intent.GET_WEATHER: [r"clima\s+(.+)"],
            Intent.PLAY_SPOTIFY: [r"pon\s+(.+)"],
            Intent.OPEN_STEAM: [r"abre steam", r"abre\s+(?!perplexity|youtube)(.+)"],
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

