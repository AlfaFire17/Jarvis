import os
import json
import queue
import sounddevice as sd
import numpy as np
import urllib.request
import zipfile
from vosk import Model, KaldiRecognizer
from core.config import Config
from core.logger import logger

class VoiceListener:
    def __init__(self):
        self.q = queue.Queue()
        self.model = None
        self.recognizer = None
        self.is_processing = False

    def download_model(self):
        """Descarga y extrae el modelo de Vosk si no existe."""
        if not os.path.exists(Config.MODEL_DIR):
            logger.info("Modelo de voz no encontrado. Descargando (~40MB)...")
            zip_path = os.path.join(os.path.dirname(Config.MODEL_DIR), "model.zip")
            try:
                urllib.request.urlretrieve(Config.MODEL_URL, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(Config.MODEL_DIR))
                os.remove(zip_path)
                logger.info("Modelo descargado y extraído correctamente.")
            except Exception as e:
                logger.error(f"Error descargando el modelo: {e}")
                return False
        return True

    def initialize(self):
        """Inicializa el modelo y el reconocedor."""
        if not self.download_model():
            return False
        
        try:
            self.model = Model(Config.MODEL_DIR)
            # Reconocedor para wake word (más restrictivo)
            self.wake_rec = KaldiRecognizer(
                self.model, 
                Config.FS, 
                f'["{Config.WAKE_PHRASE}", "[unk]"]'
            )

            # Reconocedor para comandos (abierto)
            self.command_rec = KaldiRecognizer(self.model, Config.FS)
            return True
        except Exception as e:
            logger.error(f"Error inicializando Vosk: {e}")
            return False

    def callback(self, indata, frames, time, status):
        """Callback para procesar audio del stream."""
        if status:
            logger.warning(f"Status de audio: {status}")
        # Convertir float32 a int16 y a bytes
        audio_data = (indata * 32767).astype(np.int16).tobytes()
        self.q.put(audio_data)

    def capture_command(self, timeout=5.0):
        """Escucha una orden abierta durante un tiempo limitado."""
        logger.info(f"Escuchando orden... (timeout: {timeout}s)")
        import time
        start_time = time.time()
        
        # Limpiar cola de audio previo a la activación
        while not self.q.empty():
            self.q.get()

        while time.time() - start_time < timeout:
            if not self.q.empty():
                data = self.q.get()
                if self.command_rec.AcceptWaveform(data):
                    result = json.loads(self.command_rec.Result())
                    text = result.get("text", "")
                    if text:
                        logger.info(f"Orden transcrita: '{text}'")
                        return text
            else:
                time.sleep(0.01)
        
        # Si termina el tiempo, intentamos obtener lo último que se escuchó
        final_result = json.loads(self.command_rec.FinalResult())
        text = final_result.get("text", "")
        if text:
            logger.info(f"Orden transcrita (final): '{text}'")
            return text
            
        logger.warning("Timeout agotado sin detectar orden.")
        return ""

    def listen(self, trigger_callback, conv_manager=None):
        """Bucle principal híbrido de escucha de wake word o conversación abierta."""
        logger.info(f"Escuchando wake word: \"{Config.WAKE_PHRASE}\"")
        import time
        
        try:
            with sd.InputStream(samplerate=Config.FS, device=None, dtype='float32',
                                  channels=Config.CHANNELS, callback=self.callback):
                while True:
                    data = self.q.get()
                    
                    if conv_manager:
                        if conv_manager.is_speaking or conv_manager.is_muted:
                            while not self.q.empty():
                                self.q.get()
                            time.sleep(0.01)
                            continue

                        # Si estamos en modo conversación, escuchamos y disparamos comandos directamente
                        if conv_manager.is_conversation_active() and not self.is_processing:
                            if self.command_rec.AcceptWaveform(data):
                                result = json.loads(self.command_rec.Result())
                                text = result.get("text", "")
                                if text:
                                    self.is_processing = True
                                    logger.info(f"Follow-up detectado: '{text}'")
                                    conv_manager.reset_activity_timer()
                                    trigger_callback(pre_captured_text=text)
                                    self.is_processing = False
                            continue
                            
                    # Flujo estándar: Esperando Wake Word
                    if self.wake_rec.AcceptWaveform(data):
                        result = json.loads(self.wake_rec.Result())
                        text = result.get("text", "")
                        
                        if Config.WAKE_PHRASE in text and not self.is_processing:
                            self.is_processing = True
                            logger.info("Wake word detectado!")
                            if conv_manager:
                                conv_manager.start_conversation()
                            trigger_callback()
                            self.is_processing = False
        except KeyboardInterrupt:
            logger.info("Escucha detenida por el usuario.")
        except Exception as e:
            logger.error(f"Error en el stream de audio: {e}")
