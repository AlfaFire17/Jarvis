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
    CREATE_TIMER = "create_timer"
    CREATE_REMINDER = "create_reminder"
    CREATE_ALARM = "create_alarm"
    CANCEL_EVENT = "cancel_event"
    LIST_EVENTS = "list_events"
    TIME_REMAINING = "time_remaining"
    CONVERSATION_STOP = "conversation_stop"
    SAVE_MEMORY = "save_memory"
    QUERY_MEMORY = "query_memory"
    DELETE_MEMORY = "delete_memory"
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
            # -- Alarmas y temporizadores ANTES de Spotify/memoria para evitar colisiones con "pon" --
            Intent.CREATE_ALARM: [r"pon(?: una)? alarma(?: para)? las (\d{1,2})[.:](\d{2})"],
            Intent.CREATE_TIMER: [r"pon(?: un)? temporizador(?: de)? (\d+) (minuto|minutos|hora|horas)(?:.*)?"],
            Intent.PLAY_SPOTIFY: [r"pon\s+(.+)"],
            # -- Recordatorios temporales ANTES de memoria persistente genérica --
            Intent.CREATE_REMINDER: [r"(?:recuérdame|avísame)(?:\s+que)?\s+(.+)\s+(?:en|para dentro de)\s+(\d+)\s+(minuto|minutos|hora|horas)"],
            # -- Cancelación de eventos ANTES de CONVERSATION_STOP para evitar que "para el temporizador" se confunda --
            Intent.CANCEL_EVENT: [r"(?:cancela|para|borra)\s+(?:el |la )?(temporizador|alarma|recordatorio)(?:\s+de\s+(.+))?"],
            Intent.LIST_EVENTS: [r"qué alarmas tengo", r"lista de recordatorios", r"qué eventos tengo", r"cuántos recordatorios"],
            Intent.TIME_REMAINING: [r"cuánto(?: tiempo)? queda"],
            # -- Conversación: patrones explícitos y específicos --
            Intent.CONVERSATION_STOP: [r"sal del modo conversación", r"^silencio$", r"^ya está$", r"gracias jarvis"],
            # -- Memoria persistente --
            Intent.SAVE_MEMORY: [r"(?:recuerda|guarda|no olvides)(?:\s+que)?\s+(.+)"],
            Intent.QUERY_MEMORY: [r"(?:qué recuerdas de mí|cómo me llamo|qué sabes sobre.*)"],
            Intent.DELETE_MEMORY: [r"(?:olvida|borra)(?:\s+que)?\s+(.+)"],
            # -- Apps y archivos --
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
                    # Si hay grupos de captura, extraerlos como payload
                    if not match.groups():
                        payload = None
                    elif len(match.groups()) == 1:
                        payload = match.group(1)
                    else:
                        payload = match.groups()
                        
                    logger.info(f"Intención detectada: {intent} (Payload: {payload})")
                    return intent, payload

        # Si no coincide con nada local, lo tratamos como consulta general
        logger.info(f"Intención por defecto: {Intent.GENERAL_QUERY}")
        return Intent.GENERAL_QUERY, text

