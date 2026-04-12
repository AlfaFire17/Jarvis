from core.config import Config
from core.logger import logger

class PerformanceProfile:
    GAMING = "gaming"     # Descarga inmediata, máximo ahorro de GPU
    BALANCED = "balanced" # Mantener 3-5 minutos, equilibrio
    FAST = "fast"         # Siempre cargado, respuesta instantánea

class PerformanceManager:
    """
    Gestiona los perfiles de rendimiento de JARVIS.
    Controla cuánto tiempo permanece el modelo LLM en VRAM.
    """

    def __init__(self, current_profile=None):
        self.profile = current_profile or Config.DEFAULT_PERFORMANCE_PROFILE
        self._apply_profile_settings()

    def _apply_profile_settings(self):
        """Asigna los valores técnicos según el perfil activo."""
        if self.profile == PerformanceProfile.GAMING:
            self.model_name = Config.OLLAMA_MODEL_GAMING
            self.keep_alive = 0  # Descargar inmediatamente
            self.auto_unload = True
        elif self.profile == PerformanceProfile.BALANCED:
            self.model_name = Config.OLLAMA_MODEL_DEFAULT
            self.keep_alive = 300  # 5 minutos
            self.auto_unload = False
        elif self.profile == PerformanceProfile.FAST:
            self.model_name = Config.OLLAMA_MODEL_DEFAULT
            self.keep_alive = -1   #永 Indefinido
            self.auto_unload = False
        
        logger.info(f"Perfil de rendimiento aplicado: {self.profile.upper()} "
                    f"(Modelo: {self.model_name}, KeepAlive: {self.keep_alive}s)")

    def set_profile(self, profile_name):
        """Cambia el perfil de rendimiento."""
        if profile_name in [PerformanceProfile.GAMING, PerformanceProfile.BALANCED, PerformanceProfile.FAST]:
            self.profile = profile_name
            self._apply_profile_settings()
            return True
        return False

    def get_status(self):
        """Retorna el estado actual para la GUI o el IntentRouter."""
        return {
            "profile": self.profile,
            "model": self.model_name,
            "keep_alive": self.keep_alive,
            "is_gaming": self.profile == PerformanceProfile.GAMING
        }
