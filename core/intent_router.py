import re
import unicodedata
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
    IDENTITY = "identity"
    SCREEN_ANALYZE = "screen_analyze"
    SCREEN_READ = "screen_read"
    SCREEN_ERROR = "screen_error"
    ACTIVE_WINDOW = "active_window"
    COPY_SCREEN = "copy_screen"
    VISUAL_FOLLOWUP = "visual_followup"
    UNKNOWN = "unknown"

class IntentRouter:
    def __init__(self):
        # Reglas ordenadas por PRIORIDAD (Phase 10 Patch)
        self.rules = {
            # 1. Control de conversación y silencio (Prioridad inmediata)
            Intent.CONVERSATION_STOP: [r"sal del modo conversacion", r"^silencio$", r"^ya esta$", r"gracias jarvis"],
            
            # 2. Alarmas, Temporizadores y Recordatorios (Prioridad alta)
            Intent.CANCEL_EVENT: [r"(?:cancela|para|borra)\s+(?:el |la )?(temporizador|alarma|recordatorio)(?:\s+de\s+(.+))?"],
            Intent.CREATE_ALARM: [r"pon(?: una)? alarma(?: para)? las (\d{1,2})[.:](\d{2})"],
            Intent.CREATE_TIMER: [r"pon(?: un)? temporizador(?: de)? (\d+) (minuto|minutos|hora|horas)(?:.*)?"],
            Intent.CREATE_REMINDER: [r"(?:recuerdame|avisame)(?:\s+que)?\s+(.+)\s+(?:en|para dentro de)\s+(\d+)\s+(minuto|minutos|hora|horas)"],
            Intent.LIST_EVENTS: [r"que alarmas tengo", r"lista de recordatorios", r"que eventos tengo", r"cuantos recordatorios"],
            Intent.TIME_REMAINING: [r"cuanto(?: tiempo)? queda"],
            
            # 3. Memoria Persistente (Identificación de hechos)
            Intent.SAVE_MEMORY: [r"(?:recuerda|guarda|no olvides)(?:\s+que)?\s+(.+)"],
            Intent.QUERY_MEMORY: [r"(?:que recuerdas de mi|como me llamo|que sabes sobre.*)"],
            Intent.DELETE_MEMORY: [r"(?:olvida|borra)(?:\s+que)?\s+(.+)"],
            
            # 4. VISION Y OCR (Prioridad Crítica Phase 10)
            Intent.SCREEN_ERROR: [r"ayudame con (?:este|el|un) error", r"que (?:significa|es) (?:este|ese|el|un) (?:error|fallo|mensaje)", r"explicame (?:este|ese|el) (?:error|stack|fallo)"],
            Intent.ACTIVE_WINDOW: [r"que ventana tengo (?:abierta|activa)", r"ventana actual", r"en que (?:app|programa|ventana) estoy"],
            Intent.COPY_SCREEN: [r"copia (?:el )?texto (?:visible|de (?:la |esta |mi |tu )?pantalla)", r"guarda (?:el )?texto de (?:esta|la|mi|tu) pantalla"],
            Intent.SCREEN_READ: [r"lee (?:la |esta |mi |tu )?(?:pantalla|ventana)", r"que (?:pone|dice) (?:en |aqui|la |mi |tu )(?:pantalla)?", r"leeme (?:esto|la pantalla|la ventana)"],
            Intent.SCREEN_ANALYZE: [r"analiza (?:la |esta |mi |tu )?pantalla", r"que (?:hay|ves) (?:en |a traves de )?(?:la |esta |mi |tu )?pantalla", r"que ves", r"resume (?:la |esta |mi |tu )?pantalla", r"resume (?:esto|este texto)"],
            Intent.VISUAL_FOLLOWUP: [r"explicamelo", r"traducelo", r"resumelo", r"que (?:tengo|debo) (?:que )?hacer"],
            
            # 5. Comandos Locales y Consultas Básicas
            Intent.GREETING: [r"hola", r"buenos dias", r"que tal", r"saludos", r"buenas noches"],
            Intent.IDENTITY: [r"quien te (?:creo|hizo|programo|diseno)", r"quien es tu creador", r"quien te ha creado"],
            Intent.GET_TIME: [r"que\s+hora\s+es"],
            Intent.GET_DATE: [r"que\s+dia\s+es\s+hoy"],
            Intent.GET_WEATHER: [r"clima\s+(.+)"],
            Intent.PLAY_SPOTIFY: [r"pon\s+(.+)"],
            Intent.OPEN_APP: [r"abre\s+(?!el archivo\b)(?!el ordenador\b)(?!el administrador\b)(?!la configuracion\b)(?!youtube\b)(?!perplexity\b)(?!descargas\b)(?!documentos\b)(?!escritorio\b)(?!imagenes\b)(?!mis imagenes\b)(?!proyecto\b)(?!actual\b)(?!jarvis\b)(.+)"],
            Intent.CLOSE_APP: [r"cierra\s+(.+)"],
            Intent.SYSTEM_ACTION: [r"bloquea el ordenador", r"abre (?:el )?administrador de tareas", r"abre (?:la )?configuracion"],
            Intent.OPEN_FOLDER: [r"abre\s+(descargas|documentos|escritorio|imagenes|mis imagenes|la carpeta del proyecto|proyecto|actual|jarvis)(?!.*archivo)(?!.*programa)"],
            Intent.OPEN_FILE: [r"abre el archivo\s+(.+)"],
            Intent.SEARCH_FILE: [r"(?:busca(?: el archivo)?|encuentra(?: el archivo)?)\s+(.+)"],
            Intent.SHUTDOWN: [r"apaga el equipo", r"apaga el sistema", r"apaga el ordenador", r"apagate"],
            Intent.CANCEL_SHUTDOWN: [r"cancela apagado", r"cancela el apagado", r"aborta apagado"],
            Intent.GET_RECENT_MEMORY: [r"ultimas conversaciones", r"que hice hoy", r"que hicimos hoy"],
            Intent.CHECK_LAST_COMMAND: [r"ultimo comando", r"lo ultimo que me dijiste", r"que fue lo ultimo"],
            Intent.SEARCH_MEMORY: [r"que me dijiste sobre (.+)", r"que hablamos de (.+)"],
            Intent.OPEN_PERPLEXITY: [r"abre perplexity", r"abre el buscador"],
            Intent.OPEN_YOUTUBE: [r"abre youtube"],
        }

    def _normalize_text(self, text):
        """Estandariza el texto: minúsculas, sin acentos y sin espacios extra."""
        if not text:
            return ""
        # 1. Minúsculas
        text = text.lower().strip()
        # 2. Eliminar acentos
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
        return text

    def route(self, text):
        """Clasifica el texto en una intención y extrae el payload si existe."""
        if not text or len(text.strip()) == 0:
            return Intent.UNKNOWN, None

        raw_text = text
        text = self._normalize_text(text)
        logger.info(f"Ruteando comando (Normalizado: '{text}')")

        for intent, patterns in self.rules.items():
            for pattern in patterns:
                # Los patrones ya NO deben tener acentos para que coincidan con el texto normalizado
                match = re.search(pattern, text)
                if match:
                    if not match.groups():
                        payload = None
                    elif len(match.groups()) == 1:
                        payload = match.group(1)
                    else:
                        payload = match.groups()
                        
                    logger.info(f"INTENCION DETECTADA: {intent} (Payload: {payload})")
                    return intent, payload

        # Si no coincide con nada local, lo tratamos como consulta general
        logger.info(f"INTENCION POR DEFECTO: {Intent.GENERAL_QUERY}")
        return Intent.GENERAL_QUERY, raw_text

