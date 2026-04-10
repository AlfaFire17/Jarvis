import sounddevice as sd
import numpy as np
import edge_tts
import asyncio
import os
import subprocess
import pygame
import time as t
import json
import zipfile
import urllib.request
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

# Configuration
FS = 16000       # Vosk prefiere 16kHz
CHANNELS = 1
VOICE_EDGE = "es-ES-AlvaroNeural"
PERPLEXITY_URL = "https://www.perplexity.ai"
YOUTUBE_URL = "https://www.youtube.com/watch?v=v2AC41dglnM&list=RDv2AC41dglnM&start_radio=1"
OPERA_PATH = os.getenv("OPERA_PATH") or "C:\\Users\\pablo\\AppData\\Local\\Programs\\Opera GX\\opera.exe"

# ElevenLabs config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "JBFqnCBv7vXP5ghY067B")

GREETING_TEXT = "Aquí estoy señor, siempre disponible para tí"
WAKE_PHRASE = "jarvis estas ahi"

# Model configuration
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
MODEL_DIR = os.path.join(script_dir, "vosk-model-small-es-0.42")

def download_model():
    """Descarga y extrae el modelo de Vosk si no existe."""
    if not os.path.exists(MODEL_DIR):
        print("Modelo de voz no encontrado. Descargando (~40MB)...")
        zip_path = os.path.join(script_dir, "model.zip")
        try:
            urllib.request.urlretrieve(MODEL_URL, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(script_dir)
            os.remove(zip_path)
            print("Modelo descargado y extraído correctamente.")
        except Exception as e:
            print(f"Error descargando el modelo: {e}")
            return False
    return True

# Initialize pygame mixer
try:
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.25) # Volumen al 25%
except Exception as e:
    print(f"Error inicializando mixer de audio: {e}")

def play_audio(file_path):
    """Reproduce un archivo de audio usando pygame."""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            t.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Error reproduciendo audio: {e}")

async def speak_edge(text):
    """Genera y reproduce voz usando edge-tts."""
    output_file = os.path.join(script_dir, "temp_speech.mp3")
    try:
        if os.path.exists(output_file):
            os.remove(output_file)
    except: pass
    
    communicate = edge_tts.Communicate(text, VOICE_EDGE, pitch="+0Hz", rate="+0%")
    await communicate.save(output_file)
    play_audio(output_file)

def speak_elevenlabs(text):
    """Genera y reproduce voz usando ElevenLabs."""
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(text=text, voice=VOICE_ID, model="eleven_multilingual_v2")
        output_file = os.path.join(script_dir, "temp_speech_eleven.mp3")
        with open(output_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        play_audio(output_file)
    except Exception as e:
        print(f"Error con ElevenLabs, usando fallback: {e}")
        asyncio.run(speak_edge(text))

def open_apps():
    """Abre Opera GX con las URLs especificadas."""
    try:
        if os.path.exists(OPERA_PATH):
            subprocess.Popen([OPERA_PATH, PERPLEXITY_URL])
            subprocess.Popen([OPERA_PATH, YOUTUBE_URL])
        else:
            print(f"Error: Opera GX no encontrado en {OPERA_PATH}")
    except Exception as e:
        print(f"Error abriendo apps: {e}")

async def on_trigger():
    """Acciones a realizar cuando se detecta el comando de voz."""
    print("\n¡Comando detectado! Ejecutando protocolo JARVIS...")
    if ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != "your_api_key_here":
        speak_elevenlabs(GREETING_TEXT)
    else:
        await speak_edge(GREETING_TEXT)
    open_apps()

def main():
    if not download_model():
        return

    print("Cargando modelo de lenguaje...")
    model = Model(MODEL_DIR)
    # Usamos gramática limitada para mejorar la precisión y velocidad
    rec = KaldiRecognizer(model, FS, '["jarvis estas ahi", "jarvis", "estas", "ahi", "[unk]"]')

    print("--- JARVIS Voice Assistant Iniciado ---")
    print(f"Escuchando: \"Jarvis, ¿estás ahí?\"")
    print("Presiona Ctrl+C para detener.")

    loop = asyncio.new_event_loop()
    from threading import Thread
    def run_loop(l):
        asyncio.set_event_loop(l)
        l.run_forever()
    th = Thread(target=run_loop, args=(loop,))
    th.daemon = True
    th.start()

    def callback(indata, frames, time, status):
        # Convertir float a int16 para Vosk
        audio_data = (indata * 32767).astype(np.int16).tobytes()
        if rec.AcceptWaveform(audio_data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if WAKE_PHRASE in text:
                asyncio.run_coroutine_threadsafe(on_trigger(), loop)

    try:
        with sd.InputStream(samplerate=FS, channels=CHANNELS, dtype='float32', callback=callback):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nDeteniendo JARVIS...")
    finally:
        loop.call_soon_threadsafe(loop.stop)
        th.join(timeout=1)

if __name__ == "__main__":
    main()
