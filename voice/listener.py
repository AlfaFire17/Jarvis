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
            self.recognizer = KaldiRecognizer(
                self.model, 
                Config.FS, 
                f'["{Config.WAKE_PHRASE}", "jarvis", "estas", "ahi", "[unk]"]'
            )
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

    def listen(self, trigger_callback):
        """Bucle principal de escucha."""
        logger.info(f"Escuchando wake word: \"{Config.WAKE_PHRASE}\"")
        
        try:
            with sd.InputStream(samplerate=Config.FS, device=None, dtype='float32',
                                  channels=Config.CHANNELS, callback=self.callback):
                while True:
                    data = self.q.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        
                        if Config.WAKE_PHRASE in text and not self.is_processing:
                            self.is_processing = True
                            logger.info("Wake word detectado!")
                            trigger_callback()
                            # Cooldown breve para evitar disparos repetidos
                            import time
                            time.sleep(1.0)
                            self.is_processing = False
        except KeyboardInterrupt:
            logger.info("Escucha detenida por el usuario.")
        except Exception as e:
            logger.error(f"Error en el stream de audio: {e}")
