import time
import mss
import io
import win32gui
from PIL import Image
from core.logger import logger


class VisionService:
    """
    Servicio de visión de pantalla para JARVIS.
    Captura pantalla/ventana activa y extrae contexto visual.
    Usa Gemini Vision (multimodal) para análisis inteligente.
    """

    def __init__(self, gemini_client=None):
        self.gemini = gemini_client
        self.session_context = {
            "last_window_title": None,
            "last_screen_text": None,
            "last_visual_summary": None,
            "last_capture_timestamp": None,
            "last_image": None,  # PIL Image en memoria (no se guarda a disco)
        }

    def get_active_window_title(self):
        """Obtiene el título de la ventana activa de Windows."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title if title else "Escritorio"
        except Exception as e:
            logger.error(f"Error obteniendo ventana activa: {e}")
            return "Desconocida"

    def capture_screen(self):
        """Captura la pantalla completa y devuelve una imagen PIL."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Monitor principal
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                # Actualizar contexto de sesión
                self.session_context["last_image"] = img
                self.session_context["last_window_title"] = self.get_active_window_title()
                self.session_context["last_capture_timestamp"] = time.time()
                logger.info(f"Captura de pantalla realizada ({img.size[0]}x{img.size[1]})")
                return img
        except Exception as e:
            logger.error(f"Error capturando pantalla: {e}")
            return None

    def _image_to_bytes(self, img):
        """Convierte una imagen PIL a bytes JPEG para enviar a Gemini."""
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=75)
        buffer.seek(0)
        return buffer.read()

    def analyze_screen(self, question=None):
        """
        Captura la pantalla y la analiza con Gemini Vision.
        Si se proporciona una pregunta, se contextualiza.
        """
        img = self.capture_screen()
        if img is None:
            return "No he podido capturar la pantalla, señor."

        if not self.gemini or not self.gemini.model:
            return "Mi motor de análisis visual no está disponible en este momento."

        window_title = self.session_context["last_window_title"]

        # Construir prompt contextual
        if question:
            prompt = (
                f"Eres JARVIS, asistente de Pablo Soriano. "
                f"La ventana activa es: '{window_title}'. "
                f"El usuario pregunta sobre lo que ve en pantalla: '{question}'. "
                f"Analiza la imagen y responde de forma breve, directa y útil (máximo 3 frases). "
                f"Si hay un error o stack trace, explícalo claramente."
            )
        else:
            prompt = (
                f"Eres JARVIS, asistente de Pablo Soriano. "
                f"La ventana activa es: '{window_title}'. "
                f"Describe brevemente qué se ve en esta captura de pantalla (máximo 3 frases). "
                f"Si hay texto importante, menciónalo."
            )

        try:
            img_bytes = self._image_to_bytes(img)
            response = self.gemini.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes}
            ])

            if response and response.candidates and response.candidates[0].content.parts:
                result_text = self.gemini._clean_text(response.text)
                self.session_context["last_screen_text"] = result_text
                self.session_context["last_visual_summary"] = result_text
                return result_text
            else:
                return "No he podido interpretar lo que aparece en pantalla."

        except Exception as e:
            logger.error(f"Error en análisis visual Gemini: {e}")
            return "Ha ocurrido un error analizando la pantalla, señor."

    def read_screen_text(self):
        """Captura y extrae el texto visible en pantalla."""
        return self.analyze_screen(question="Lee y transcribe todo el texto visible en esta pantalla.")

    def summarize_screen(self):
        """Captura y resume el contenido visible."""
        return self.analyze_screen(question="Resume el contenido principal visible en esta pantalla en 2-3 frases.")

    def explain_screen_error(self):
        """Captura y explica errores visibles en pantalla."""
        return self.analyze_screen(
            question="Si hay algún error, warning, stack trace o mensaje de fallo visible, "
                     "explícalo claramente y sugiere qué hacer para resolverlo."
        )

    def get_last_context(self):
        """Devuelve el último contexto visual para follow-ups."""
        text = self.session_context.get("last_screen_text")
        window = self.session_context.get("last_window_title")
        if text:
            return text, window
        return None, None

    def followup_analysis(self, question):
        """
        Realiza un follow-up sobre el último contexto visual.
        Si hay imagen reciente, la reutiliza. Si no, captura nueva.
        """
        last_img = self.session_context.get("last_image")
        last_ts = self.session_context.get("last_capture_timestamp", 0)

        # Reutilizar si la captura tiene menos de 60 segundos
        if last_img and (time.time() - last_ts) < 60:
            logger.info("Reutilizando captura reciente para follow-up.")
            window_title = self.session_context.get("last_window_title", "Desconocida")

            prompt = (
                f"Eres JARVIS, asistente de Pablo Soriano. "
                f"La ventana activa era: '{window_title}'. "
                f"El usuario pide sobre lo que se ve en pantalla: '{question}'. "
                f"Responde de forma breve, directa y útil (máximo 3 frases)."
            )

            try:
                img_bytes = self._image_to_bytes(last_img)
                response = self.gemini.model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": img_bytes}
                ])
                if response and response.candidates and response.candidates[0].content.parts:
                    result_text = self.gemini._clean_text(response.text)
                    self.session_context["last_screen_text"] = result_text
                    return result_text
            except Exception as e:
                logger.error(f"Error en follow-up visual: {e}")

        # Si no hay captura reciente, hacer nueva
        return self.analyze_screen(question=question)

    def copy_screen_text_to_clipboard(self):
        """Copia el último texto OCR al portapapeles de Windows."""
        text = self.session_context.get("last_screen_text")
        if not text:
            # Capturar primero
            text = self.read_screen_text()

        if text:
            try:
                import subprocess
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(text.encode('utf-8'))
                return "He copiado el texto visible al portapapeles, señor."
            except Exception as e:
                logger.error(f"Error copiando al portapapeles: {e}")
                return "No he podido copiar el texto al portapapeles."
        return "No hay texto disponible para copiar."
