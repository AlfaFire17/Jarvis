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
    AGENDA_PATH = os.path.join(project_root, "data", "agenda.json")
    
    # API Keys
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Triggers
    WAKE_PHRASE = "jarvis estas ahi"
    GREETING_TEXT = "Aquí estoy señor, siempre disponible para tí"

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
