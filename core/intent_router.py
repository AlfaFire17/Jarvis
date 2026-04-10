import re
from core.logger import logger

class Intent:
    GREETING = "greeting"
    OPEN_PERPLEXITY = "open_perplexity"
    OPEN_YOUTUBE = "open_youtube"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"

class IntentRouter:
    def __init__(self):
        # Reglas simples basadas en palabras clave
        self.rules = {
            Intent.GREETING: [r"hola", r"buenos d[ií]as", r"qu[ée] tal", r"saludos"],
            Intent.OPEN_PERPLEXITY: [r"abre perplexity", r"abre el buscador", r"pon perplexity"],
            Intent.OPEN_YOUTUBE: [r"abre youtube", r"pon m[uú]sica", r"abre el v[ií]deo", r"pon youtube"],
        }

    def route(self, text):
        """Clasifica el texto en una intención."""
        if not text or len(text.strip()) == 0:
            return Intent.UNKNOWN, ""

        text = text.lower().strip()
        logger.info(f"Analizando intención para: '{text}'")

        for intent, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    logger.info(f"Intención detectada: {intent}")
                    return intent, text

        # Si no coincide con nada local, lo tratamos como consulta general
        logger.info(f"Intención por defecto: {Intent.GENERAL_QUERY}")
        return Intent.GENERAL_QUERY, text
