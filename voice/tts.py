import os
import asyncio
import pygame
import time as t
from edge_tts import Communicate
from elevenlabs import ElevenLabs
from core.config import Config
from core.logger import logger

class TTSProvider:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.25)
        except Exception as e:
            logger.error(f"Error inicializando mixer de audio: {e}")

    def play_audio(self, file_path):
        """Reproduce un archivo de audio usando pygame."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                t.sleep(0.1)
            pygame.mixer.music.unload()
        except Exception as e:
            logger.error(f"Error reproduciendo audio {file_path}: {e}")

    async def speak_edge(self, text):
        """Genera y reproduce voz usando edge-tts."""
        output_file = os.path.join(self.script_dir, "temp_speech.mp3")
        try:
            if os.path.exists(output_file):
                os.remove(output_file)
        except Exception as e:
            logger.debug(f"No se pudo borrar archivo temporal: {e}")
        
        try:
            communicate = Communicate(text, Config.VOICE_EDGE, pitch="+0Hz", rate="+0%")
            await communicate.save(output_file)
            self.play_audio(output_file)
            return True
        except Exception as e:
            logger.error(f"Error con Edge-TTS: {e}")
            return False

    def speak_elevenlabs(self, text):
        """Genera y reproduce voz usando ElevenLabs."""
        if not Config.ELEVENLABS_API_KEY:
            return False
            
        try:
            client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
            audio = client.generate(text=text, voice=Config.VOICE_ID, model="eleven_multilingual_v2")
            output_file = os.path.join(self.script_dir, "temp_speech_eleven.mp3")
            with open(output_file, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            self.play_audio(output_file)
            return True
        except Exception as e:
            logger.error(f"Error con ElevenLabs: {e}")
            return False

    async def speak(self, text):
        """Método unificado que intenta ElevenLabs y cae a Edge-TTS."""
        logger.info(f"Hablando: {text}")
        success = False
        if Config.ELEVENLABS_API_KEY:
            success = self.speak_elevenlabs(text)
        
        if not success:
            await self.speak_edge(text)
