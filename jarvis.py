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
    get_current_time, get_current_date, get_weather, play_spotify,
    shutdown_computer, cancel_shutdown, lock_workstation, open_task_manager, open_settings
)
from actions.app_actions import open_application, close_application
from actions.file_actions import open_user_folder, find_and_report_file, find_and_open_file
from integrations.gemini_client import GeminiClient
from services.memory_service import MemoryService

# Import the new GUI components
from core.gui_controller import JARVISGUIController
from gui.overlay import JARVISOverlay

async def on_trigger(listener, tts, router, gemini, gui, memory):
    """Acciones a realizar cuando se detecta el wake word."""
    logger.info("Protocolo JARVIS: Activado.")
    gui.set_wake.emit()
    
    await asyncio.sleep(0.5)
    
    logger.info("<<< Escuchando orden... >>>")
    gui.set_listening.emit()
    
    command_text = listener.capture_command(timeout=7.0)
    
    if not command_text:
        response = no_command_response()
        gui.set_responding.emit(response)
        await tts.speak(response)
        return

    gui.set_transcription.emit(command_text)

    intent, payload = router.route(command_text)
    
    response = ""
    source = "local"
    success = True
    
    if intent == Intent.GREETING:
        if "buenas noches" in command_text.lower():
            response = "Buenas noches, señor. Que descanse."
        else:
            response = say_hello()
            
    elif intent == Intent.SHUTDOWN:
        response = shutdown_computer()
        
    elif intent == Intent.CANCEL_SHUTDOWN:
        response = cancel_shutdown()

    elif intent == Intent.SYSTEM_ACTION:
        if "bloquea" in command_text.lower():
            response = lock_workstation()
        elif "administrador de tareas" in command_text.lower():
            response = open_task_manager()
        elif "configuración" in command_text.lower():
            response = open_settings()

    elif intent == Intent.OPEN_APP:
        response = open_application(payload)
        
    elif intent == Intent.CLOSE_APP:
        response = close_application(payload)

    elif intent == Intent.OPEN_FOLDER:
        response = open_user_folder(payload)

    elif intent == Intent.SEARCH_FILE:
        response = find_and_report_file(payload)

    elif intent == Intent.OPEN_FILE:
        response = find_and_open_file(payload)

    elif intent == Intent.GET_RECENT_MEMORY:
        response = memory.get_recent_interactions(limit=3)

    elif intent == Intent.CHECK_LAST_COMMAND:
        response = memory.get_last_command()

    elif intent == Intent.SEARCH_MEMORY:
        response = memory.search_interactions(payload) if payload else "Lo siento señor, no he entendido qué desea buscar en la memoria."

    elif intent == Intent.OPEN_PERPLEXITY:
        response = "Abriendo Perplexity, señor. Siempre es bueno buscar respuestas."
        open_perplexity()
        
    elif intent == Intent.OPEN_YOUTUBE:
        response = "Entendido. Abriendo YouTube."
        open_youtube()

    elif intent == Intent.PLAY_SPOTIFY:
        response = play_spotify(payload)

    elif intent == Intent.GET_TIME:
        response = get_current_time()

    elif intent == Intent.GET_DATE:
        response = get_current_date()

    elif intent == Intent.GET_WEATHER:
        response = get_weather(payload) if payload else get_weather()
        
    elif intent == Intent.GENERAL_QUERY:
        source = "gemini"
        gui.set_responding.emit("Consultando en mi base de datos, un momento...")
        await tts.speak("Consultando en mi base de datos, un momento...")
        answer = gemini.ask(payload)
        response = answer
        if "Lo siento" in answer or "ocurrido un error" in answer:
            success = False
    
    elif intent == Intent.UNKNOWN:
        response = no_command_response()
        success = False

    if response:
        memory.save_interaction(
            user_input=command_text,
            action_type=intent,
            response_text=response,
            success=success,
            source=source
        )

        gui.set_responding.emit(response)
        await tts.speak(response)

def run_voice_loop(listener, tts, router, gemini, gui, memory):
    def trigger_callback():
        asyncio.run(on_trigger(listener, tts, router, gemini, gui, memory))

    try:
        listener.listen(trigger_callback)
    except Exception as e:
        logger.critical(f"Error fatal en el núcleo de voz: {e}")

def main():
    if not Config.validate():
        logger.error("Error validando configuración. Abortando.")
        sys.exit(1)

    app = QApplication(sys.argv)

    logger.info("--- JARVIS Voice Assistant (Fase 7: Desktop Control) ---")
    
    tts = TTSProvider()
    router = IntentRouter()
    gemini = GeminiClient()
    listener = VoiceListener()
    memory = MemoryService()

    if not listener.initialize():
        logger.error("No se pudo inicializar el sistema de voz.")
        sys.exit(1)

    gui_controller = JARVISGUIController()
    overlay = JARVISOverlay(gui_controller)

    voice_thread = threading.Thread(
        target=run_voice_loop,
        args=(listener, tts, router, gemini, gui_controller, memory),
        daemon=True
    )
    voice_thread.start()

    logger.info("JARVIS GUI, Memoria y sistema de voz iniciados. Esperando comando...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()





