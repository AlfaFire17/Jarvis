import requests
from core.config import Config
from core.logger import logger

class PerplexityClient:
    def __init__(self):
        self.api_key = Config.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def query(self, prompt):
        """Envía una consulta simple a la API de Perplexity."""
        if not self.api_key:
            logger.error("Error: PERPLEXITY_API_KEY no configurada.")
            return "Lo siento, necesito una API key de Perplexity para responderte."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "pplx-7b-online", # Modelo ejemplo, puede cambiar
            "messages": [
                {"role": "system", "content": "Eres JARVIS, un asistente personal inteligente y sofisticado."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            logger.info(f"Enviando consulta a Perplexity: {prompt}")
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            answer = data['choices'][0]['message']['content']
            return answer
        except Exception as e:
            logger.error(f"Error consultando Perplexity: {e}")
            return "Hubo un error al conectar con mi motor de búsqueda."

    def test_connection(self):
        """Verifica que la API key funcione con una consulta mínima."""
        return self.query("Hola, ¿estás funcionando?")
