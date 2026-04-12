import requests
import json
from core.config import Config
from core.logger import logger

class OllamaClient:
    """
    Cliente para interactuar con la API local de Ollama.
    Soporta chat multi-turno y gestión de memoria (keep_alive).
    """

    def __init__(self, model_name=None):
        self.url = f"{Config.OLLAMA_URL}/api/chat"
        self.model = model_name or Config.OLLAMA_MODEL_DEFAULT
        self.history = []
        # System prompt para mantener la personalidad de JARVIS
        self.system_prompt = (
            "Eres JARVIS, un asistente personal inteligente creado por Pablo Soriano. "
            "Tu personalidad es sofisticada, elegante y eficiente. "
            "Tus respuestas deben ser breves (máximo 3 frases) y naturales para ser leídas por voz. "
            "Evita el markdown excesivo."
        )

    def _reset_history_if_needed(self):
        """Reinicia el historial si es demasiado largo para evitar latencia."""
        if len(self.history) > 10:
            self.history = self.history[-6:]

    def ask(self, prompt, keep_alive=300):
        """
        Envía una consulta al modelo local.
        :param prompt: Texto del usuario.
        :param keep_alive: Tiempo en segundos que el modelo permanece en VRAM (0 = descarga inmediata).
        """
        self._reset_history_if_needed()
        
        # Preparar mensajes incluyendo el system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive
        }

        try:
            logger.info(f"Consultando Ollama ({self.model}, keep_alive: {keep_alive}s): {prompt}")
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("message", {}).get("content", "").strip()

            if answer:
                # Guardar en histórico (limitado)
                self.history.append({"role": "user", "content": prompt})
                self.history.append({"role": "assistant", "content": answer})
                return answer
            
            return "No he recibido una respuesta válida de mi núcleo local, señor."

        except requests.exceptions.ConnectionError:
            logger.error("No se pudo conectar con Ollama. ¿Está el servicio iniciado?")
            return "ERROR_CONNECTION"
        except Exception as e:
            logger.error(f"Error en consulta Ollama: {e}")
            return f"Lo siento señor, mi núcleo local ha devuelto un error: {str(e)}"

    def unload(self):
        """Descarga el modelo de la memoria VRAM inmediatamente."""
        try:
            unload_url = f"{Config.OLLAMA_URL}/api/generate"
            payload = {"model": self.model, "keep_alive": 0}
            requests.post(unload_url, json=payload, timeout=5)
            logger.info(f"Modelo {self.model} descargado de VRAM.")
            return True
        except Exception as e:
            logger.warning(f"No se pudo descargar el modelo: {e}")
            return False

    def check_status(self):
        """Verifica si Ollama está disponible y qué versión tiene."""
        try:
            res = requests.get(Config.OLLAMA_URL, timeout=2)
            return res.status_code == 200
        except:
            return False
