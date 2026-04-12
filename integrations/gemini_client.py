import google.generativeai as genai
from core.config import Config
from core.logger import logger
import re

class GeminiClient:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "max_output_tokens": 250,
                        "temperature": 0.5,
                    },
                    system_instruction=(
                        "Eres JARVIS, un asistente personal inteligente creado por Pablo Soriano, con asistencia de Perplexity. "
                        "Tu inspiración estética es el JARVIS de Iron Man, pero tu creador real es Pablo Soriano. "
                        "NUNCA digas que fuiste creado por Tony Stark, OpenAI, Google ni ningún otro. "
                        "Si te preguntan quién te creó, responde siempre: 'Fui creado por Pablo Soriano, con asistencia de Perplexity.' "
                        "Tus respuestas deben ser breves, directas y elegantes, ideales para ser leídas en voz alta. "
                        "No uses frases de relleno como 'un momento', 'déjame pensar', 'consultando', 'revisando'. "
                        "Ve directo al grano. Evita listas largas y markdown. Limítate a 2 o 3 frases informativas máximo."
                    )
                )
                logger.info(f"GeminiClient inicializado: {self.model_name} (Temp: 0.5)")
            except Exception as e:
                logger.error(f"Error inicializando Gemini SDK: {e}")

    def ask(self, question):
        """Envía una consulta a Google Gemini de forma robusta."""
        if not self.api_key or not self.model:
            logger.error("Error: GEMINI_API_KEY no configurada o modelo no inicializado.")
            return "Señor, mis protocolos de IA están desactivados. Verifique su clave de acceso."

        try:
            logger.info(f"Consultando a Gemini ({self.model_name}): {question}")
            response = self.model.generate_content(question)
            
            # Validación robusta de la respuesta
            if not response:
                return "No he recibido respuesta de los servidores, señor."
            
            # El SDK puede devolver errores en candidatos o bloqueos por seguridad
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                # Verificar si el candidato tiene texto (evitar errores de seguridad/bloqueo)
                if candidate.content.parts:
                    answer = response.text
                    return self._clean_text(answer)
                else:
                    logger.warning(f"Respuesta bloqueada o vacía: {candidate.finish_reason}")
                    return "Lo siento señor, no puedo responder a esa solicitud por restricciones de seguridad."
            
            return "No he podido procesar una respuesta válida en este momento."
                
        except Exception as e:
            logger.error(f"Error crítico en consulta Gemini: {e}")
            return "Ha ocurrido un error en mi núcleo de procesamiento, señor. Por favor, reintente en unos instantes."

    def _clean_text(self, text):
        """Limpia el texto para que sea natural y fluido para TTS."""
        if not text:
            return ""

        # 1. Eliminar markdown residual (negritas, cursivas, títulos, bloques de código)
        text = re.sub(r'[*_#~`>]', '', text)
        
        # 2. Eliminar marcadores de listas (guiones, asteriscos, numeración al inicio de línea)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+[\.\)]\s+', '', text, flags=re.MULTILINE)
        
        # 3. Compactar espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 4. Recorte inteligente por frases (máximo 3 frases para no cansar)
        # Usamos regex para detectar puntos, exclamaciones o interrogaciones seguidos de espacio
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 3:
            text = " ".join(sentences[:3])
        else:
            text = " ".join(sentences)

        return text.strip()
