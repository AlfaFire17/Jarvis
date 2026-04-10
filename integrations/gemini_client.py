import google.generativeai as genai
from core.config import Config
from core.logger import logger
import re

class GeminiClient:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "max_output_tokens": 200,
                        "temperature": 0.7,
                    },
                    system_instruction="Eres JARVIS, un asistente personal inteligente, sofisticado y eficiente. Tus respuestas deben ser breves, directas y elegantes, ideales para ser leídas por voz. No uses markdown excesivo. Máximo 2-3 frases por respuesta."
                )
                logger.info(f"GeminiClient inicializado con modelo {self.model_name}")
            except Exception as e:
                logger.error(f"Error inicializando Gemini SDK: {e}")

    def ask(self, question):
        """Envía una consulta a Google Gemini."""
        if not self.api_key or not self.model:
            logger.error("Error: GEMINI_API_KEY no configurada o modelo no inicializado.")
            return "Señor, no puedo acceder a mis servidores de inteligencia en este momento. Por favor, verifique la clave de API."

        try:
            logger.info(f"Consultando a Gemini: {question}")
            response = self.model.generate_content(question)
            
            if response and response.text:
                answer = response.text
                return self._clean_text(answer)
            else:
                return "No he podido generar una respuesta coherente, señor."
                
        except Exception as e:
            logger.error(f"Error en consulta Gemini: {e}")
            return "Lo siento señor, ha ocurrido un error al procesar su solicitud en mi núcleo de IA."

    def _clean_text(self, text):
        """Limpia el texto para que sea apto para TTS."""
        # Eliminar asteriscos de negrita/cursiva
        text = re.sub(r'[*_#]', '', text)
        # Eliminar bloques de código o etiquetas extrañas si las hay
        text = re.sub(r'`.*?`', '', text, flags=re.DOTALL)
        
        # Limitar longitud para TTS (aprox 150 tokens ~ 600-800 caracteres)
        # Pero el prompt del sistema ya pide brevedad
        if len(text) > 500:
            text = text[:500] + "..."
            
        return text.strip()
