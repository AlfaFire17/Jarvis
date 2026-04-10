import asyncio
import sys
import threading
from PySide6.QtWidgets import QApplication

from core.config import Config
from core.logger import logger
from voice.listener import VoiceListener
from voice.tts import TTSProvider
from core.intent_router import IntentRouter, Intent
from actions.system_actions import (
    open_perplexity, open_youtube, say_hello, no_command_response,
    get_current_time, get_current_date, get_weather, play_spotify, launch_steam
)
from integrations.gemini_client import GeminiClient

# Import the new GUI components
from core.gui_controller import JARVISGUIController
from gui.overlay import JARVISOverlay

async def on_trigger(listener, tts, router, gemini, gui):
    """Acciones a realizar cuando se detecta el wake word."""
    logger.info("Protocolo JARVIS: Activado.")
    gui.set_wake.emit()
    
    # Damos un pequeño margen para que la GUI pase a "Escuchando..."
    await asyncio.sleep(0.5)
    
    # Visual feedback: listening
    logger.info("<<< Escuchando orden... >>>")
    gui.set_listening.emit()
    
    # 1. Capturar la orden del usuario
    command_text = listener.capture_command(timeout=7.0)
    
    if not command_text:
        response = no_command_response()
        gui.set_responding.emit(response)
        await tts.speak(response)
        return

    # Mostrar la transcripción
    gui.set_transcription.emit(command_text)

    # 2. Enrutar la intención
    intent, payload = router.route(command_text)
    
    # 3. Ejecutar acción y preparar respuesta para GUI y TTS
    response = ""
    
    if intent == Intent.GREETING:
        response = say_hello()
        
    elif intent == Intent.OPEN_PERPLEXITY:
        response = "Abriendo Perplexity, señor. Siempre es bueno buscar respuestas."
        open_perplexity()
        
    elif intent == Intent.OPEN_YOUTUBE:
        response = "Entendido. Abriendo YouTube."
        open_youtube()

    elif intent == Intent.OPEN_STEAM:
        response = launch_steam(payload)

    elif intent == Intent.PLAY_SPOTIFY:
        response = play_spotify(payload)

    elif intent == Intent.GET_TIME:
        response = get_current_time()

    elif intent == Intent.GET_DATE:
        response = get_current_date()

    elif intent == Intent.GET_WEATHER:
        response = get_weather(payload) if payload else get_weather()
        
    elif intent == Intent.GENERAL_QUERY:
        gui.set_responding.emit("Consultando en mi base de datos, un momento...")
        await tts.speak("Consultando en mi base de datos, un momento...")
        answer = gemini.ask(payload)
        gui.set_responding.emit(answer)
        await tts.speak(answer)
        return # evitamos doble speak
    
    elif intent == Intent.UNKNOWN:
        response = no_command_response()

    # Emitir y hablar respuesta estandar
    if response:
        gui.set_responding.emit(response)
        await tts.speak(response)

def run_voice_loop(listener, tts, router, gemini, gui):
    """Función para el hilo en segundo plano que escucha perpetuamente."""
    # 3. Definir el callback de disparo
    def trigger_callback():
        # Ejecutar el flujo de comando en el loop de eventos del hilo de fondo
        asyncio.run(on_trigger(listener, tts, router, gemini, gui))

    # 4. Iniciar escucha
    try:
        listener.listen(trigger_callback)
    except Exception as e:
        logger.critical(f"Error fatal en el núcleo de voz: {e}")

def main():
    # 1. Validar configuración
    if not Config.validate():
        logger.error("Error validando configuración. Abortando.")
        sys.exit(1)

    # Inicializar la aplicación Qt primero
    app = QApplication(sys.argv)

    # 2. Inicializar servicios de IA y Audio
    logger.info("--- JARVIS Voice Assistant (Fase 5: GUI Overlay) ---")
    
    tts = TTSProvider()
    router = IntentRouter()
    gemini = GeminiClient()
    listener = VoiceListener()

    if not listener.initialize():
        logger.error("No se pudo inicializar el sistema de voz.")
        sys.exit(1)

    # Inicializar Controlador GUI y Ventana
    gui_controller = JARVISGUIController()
    overlay = JARVISOverlay(gui_controller)
    # No llamamos a overlay.show() explícitamente para que inicie invisible

    # Arrancar el hilo de asistente de voz (hilo daemon significa que se cierra al cerrar la app)
    voice_thread = threading.Thread(
        target=run_voice_loop,
        args=(listener, tts, router, gemini, gui_controller),
        daemon=True
    )
    voice_thread.start()

    logger.info("JARVIS GUI y sistema de voz iniciados. Esperando comando...")
    
    # Bloquear el hilo principal con el loop de Qt
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



