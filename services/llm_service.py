from integrations.ollama_client import OllamaClient
from integrations.gemini_client import GeminiClient
from core.config import Config
from core.logger import logger

class LLMService:
    """
    Servicio unificado de IA. Gestiona el uso de Ollama como principal
    y Gemini como fallback en la nube.
    """

    def __init__(self, performance_manager):
        self.perf = performance_manager
        self.ollama = OllamaClient(model_name=self.perf.model_name)
        self.gemini = GeminiClient()
        self.backend = Config.DEFAULT_LLM_BACKEND  # "ollama" o "gemini"
        self.fallback_enabled = True

    def _sync_model_with_perf(self):
        """Asegura que el cliente de Ollama use el modelo del perfil actual."""
        if self.ollama.model != self.perf.model_name:
            self.ollama.model = self.perf.model_name
            logger.info(f"Sincronizando LLMService con modelo de perfil: {self.ollama.model}")

    def ask(self, prompt, vision_context=None):
        """
        Envía una consulta al cerebro de JARVIS.
        :param prompt: Pregunta del usuario.
        :param vision_context: Texto extraído de la pantalla si existe.
        """
        self._sync_model_with_perf()

        # Si hay contexto visual, unirlo al prompt
        final_prompt = prompt
        if vision_context:
            final_prompt = (
                f"[CONTEXTO VISUAL DE PANTALLA]: {vision_context}\n"
                f"Usuario: {prompt}"
            )

        # 1. Intentar con el backend preferido
        if self.backend == "ollama":
            response = self.ollama.ask(final_prompt, keep_alive=self.perf.keep_alive)
            
            if response == "ERROR_CONNECTION":
                logger.warning("Ollama no responde. Intentando fallback...")
                if self.fallback_enabled:
                    return self.gemini.ask(final_prompt)
                else:
                    return "Señor, no puedo conectar con mi núcleo local y el acceso a la nube está restringido."
            
            return response
        
        # 2. Si el backend es gemini directo
        return self.gemini.ask(final_prompt)

    def set_backend(self, backend_name):
        """Cambia el backend manualmente (ollama/gemini)."""
        if backend_name in ["ollama", "gemini"]:
            self.backend = backend_name
            logger.info(f"Backend de IA cambiado a: {backend_name}")
            return True
        return False

    def get_status(self):
        """Retorna información para la GUI."""
        return {
            "backend": self.backend,
            "fallback": self.fallback_enabled,
            "model": self.ollama.model if self.backend == "ollama" else "Gemini Cloud"
        }
