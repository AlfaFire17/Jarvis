import os
from dotenv import load_dotenv
import logging

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

class Config:
    # Audio Settings
    FS = 16000
    CHANNELS = 1
    
    # Voice Settings
    VOICE_EDGE = "es-ES-AlvaroNeural"
    VOICE_ID = os.getenv("VOICE_ID", "JBFqnCBv7vXP5ghY067B")
    
    # URLs
    PERPLEXITY_URL = "https://www.perplexity.ai"
    YOUTUBE_URL = "https://www.youtube.com/watch?v=v2AC41dglnM&list=RDv2AC41dglnM&start_radio=1"
    
    # Paths
    OPERA_PATH = os.getenv("OPERA_PATH") or r"C:\Users\pablo\AppData\Local\Programs\Opera GX\opera.exe"
    MODEL_DIR = os.path.join(project_root, "vosk-model-small-es-0.42")
    MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
    STEAM_APPS_PATH = r"C:\Program Files (x86)\Steam\steamapps"
    STEAM_EXE_PATH = r"C:\Program Files (x86)\Steam\steam.exe"

    AGENDA_PATH = os.path.join(project_root, "data", "agenda.json")
    # Mantener nombre de archivo para compatibilidad con datos existentes
    MEMORY_FILE_PATH = os.path.join(project_root, "data", "jarvis_memory.json")

    # Rutas e Integraciones Fase 12 (Informe Diario & OAuth)
    REPORTS_DIR = os.path.join(project_root, "data", "reports")
    PRIVATE_DATA_DIR = os.path.join(project_root, "data", "private")
    GOOGLE_CREDENTIALS_PATH = os.path.join(project_root, "data", "private", "credentials.json")
    GOOGLE_CREDENTIALS_FALLBACK_PATH = os.path.join(project_root, "credentials.json")
    GOOGLE_TOKEN_PATH = os.path.join(project_root, "data", "private", "google_token.json")

    # Configuración por defecto para Informe Diario
    DAILY_BRIEFING_DEFAULT_SETTINGS = {
        "enabled": True,
        "auto_generate_on_first_manual_start_per_day": True,
        "auto_open_report": True,
        "preferred_browser": "default",
        "report_history_days": 30,
        "calendar_days_ahead": 14,
        "email_lookback_days": 3,
        "news_limit_total": 10
    }

    
    # API Keys
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # Ollama & LLM Settings (Fase 11)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL_DEFAULT = os.getenv("OLLAMA_MODEL_DEFAULT", "llama3:8b")
    OLLAMA_MODEL_GAMING = os.getenv("OLLAMA_MODEL_GAMING", "phi3:mini")
    DEFAULT_LLM_BACKEND = "ollama"  # "ollama" o "gemini"
    DEFAULT_PERFORMANCE_PROFILE = "balanced"  # "gaming", "balanced", "fast"
    
    # Triggers
    WAKE_PHRASE = "alfa"

    # Branding (Microfase 11.1)
    DISPLAY_NAME = "A.L.F.A."
    SPOKEN_NAME = "Alfa"
    CREATOR = "Pablo Soriano"
    CREATOR_ASSISTANCE = "Perplexity"
    THEME = "red_alpha"

    # Startup
    AUTO_START_ENABLED = False

    GREETING_TEXT = "Aquí estoy señor, siempre disponible para usted"

    @classmethod
    def validate(cls):
        """Validates critical configuration."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        
        if missing:
            logging.warning(f"Variables de entorno faltantes: {', '.join(missing)}")
            logging.warning("Algunas funciones podrían no estar disponibles.")
        else:
            logging.info("Configuración cargada correctamente.")
        
        if not os.path.exists(cls.OPERA_PATH):
            logging.warning(f"Opera GX no encontrado en: {cls.OPERA_PATH}")
            
        return True
