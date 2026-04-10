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
            
            # Limpieza básica de la respuesta para TTS
            cleaned_answer = self._clean_text(answer)
            return cleaned_answer
        except Exception as e:
            logger.error(f"Error consultando Perplexity: {e}")
            return "Hubo un error al conectar con mi motor de búsqueda."

    def _clean_text(self, text):
        """Limpia el texto de markdown y lo recorta para TTS."""
        import re
        # Eliminar negritas, cursivas, etc.
        text = re.sub(r'[*_#]', '', text)
        # Eliminar citas tipo [1], [2], [1, 2]
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        # Eliminar enlaces markdown [texto](url)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Limitar longitud para no cansar al usuario (aprox 300 caracteres)
        if len(text) > 300:
            text = text[:300] + "... Para más detalles, por favor consulte la pantalla."
            
        return text.strip()

    def test_connection(self):
        """Verifica que la API key funcione con una consulta mínima."""
        return self.query("Hola, ¿estás funcionando?")
