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
from actions.reminder_actions import (
    create_timer, create_alarm, create_reminder,
    cancel_matching_events, list_pending_events, get_time_remaining
)
from actions.memory_actions import remember_fact, forget_fact, query_profile
from actions.vision_actions import (
    analyze_current_screen, read_screen_text, summarize_screen,
    explain_screen_error, get_active_window_info, copy_visible_text, followup_visual
)
from integrations.gemini_client import GeminiClient
from services.memory_service import MemoryService
from services.scheduler_service import JARVIScheduler
from services.conversation_manager import ConversationManager
from services.hotkey_service import JARVISHotkeyManager
from services.vision_service import VisionService

# Import the GUI components
from core.gui_controller import JARVISGUIController
from gui.overlay import JARVISOverlay


async def process_command(command_text, listener, tts, router, gemini, gui, memory, conv_manager, vision):
    """Procesa un comando (ya sea desde wake word o follow-up)."""
    gui.set_transcription.emit(command_text)

    intent, payload = router.route(command_text)

    response = ""
    source = "local"
    success = True

    # --- Fase 9: Control de conversación ---
    if intent == Intent.CONVERSATION_STOP:
        conv_manager.stop_conversation()
        response = "Modo conversación finalizado, señor."
        gui.set_responding.emit(response)
        conv_manager.set_speaking(True)
        await tts.speak(response)
        conv_manager.set_speaking(False)
        memory.save_interaction(command_text, intent, response, True, "local")
        return

    # --- Fase 9: Memoria persistente ---
    elif intent == Intent.SAVE_MEMORY:
        response = remember_fact(memory, payload)

    elif intent == Intent.QUERY_MEMORY:
        response = query_profile(memory)

    elif intent == Intent.DELETE_MEMORY:
        response = forget_fact(memory, payload)

    # --- Comandos existentes (todas las fases anteriores) ---
    elif intent == Intent.GREETING:
        if "buenas noches" in command_text.lower():
            response = "Buenas noches, señor. Que descanse."
        else:
            response = say_hello()

    elif intent == Intent.IDENTITY:
        response = "Fui creado por Pablo Soriano, con asistencia de Perplexity. Mi inspiración estética es el JARVIS de Iron Man, pero mi autor real es Pablo Soriano."

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

    elif intent == Intent.CREATE_TIMER:
        dur = payload[0] if isinstance(payload, tuple) else payload
        unit = payload[1] if isinstance(payload, tuple) and len(payload) > 1 else "minutos"
        label = payload[2] if isinstance(payload, tuple) and len(payload) > 2 else None
        response = create_timer(memory, dur, unit, label)

    elif intent == Intent.CREATE_ALARM:
        if isinstance(payload, tuple) and len(payload) >= 2:
            response = create_alarm(memory, payload[0], payload[1])
        else:
            response = "Lo siento, no he entendido la hora para la alarma."

    elif intent == Intent.CREATE_REMINDER:
        if isinstance(payload, tuple) and len(payload) >= 3:
            response = create_reminder(memory, payload[0], payload[1], payload[2])
        else:
            response = "Lo siento, me faltan datos para establecer el recordatorio."

    elif intent == Intent.CANCEL_EVENT:
        ev_type = payload[0] if isinstance(payload, tuple) else payload
        query_val = payload[1] if isinstance(payload, tuple) and len(payload) > 1 else None
        response = cancel_matching_events(memory, ev_type, query_val)

    elif intent == Intent.LIST_EVENTS:
        response = list_pending_events(memory)

    elif intent == Intent.TIME_REMAINING:
        response = get_time_remaining(memory)

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

    # --- Fase 10: Visión de pantalla ---
    elif intent == Intent.SCREEN_ANALYZE:
        gui.set_analyzing.emit("Analizando pantalla...")
        response = analyze_current_screen(vision)

    elif intent == Intent.SCREEN_READ:
        gui.set_analyzing.emit("Leyendo texto en pantalla...")
        response = read_screen_text(vision)

    elif intent == Intent.SCREEN_ERROR:
        gui.set_analyzing.emit("Analizando error en pantalla...")
        response = explain_screen_error(vision)

    elif intent == Intent.ACTIVE_WINDOW:
        response = get_active_window_info(vision)

    elif intent == Intent.COPY_SCREEN:
        gui.set_analyzing.emit("Copiando texto visible...")
        response = copy_visible_text(vision)

    elif intent == Intent.VISUAL_FOLLOWUP:
        gui.set_analyzing.emit("Analizando contexto visual...")
        response = followup_visual(vision, command_text)

    elif intent == Intent.GENERAL_QUERY:
        source = "gemini"
        gui.set_responding.emit("Procesando...")
        answer = gemini.ask(payload)
        response = answer
        if "Lo siento" in answer or "ocurrido un error" in answer:
            success = False

    elif intent == Intent.UNKNOWN:
        response = no_command_response()
        success = False

    # --- Guardar interacción y responder ---
    if response:
        memory.save_interaction(
            user_input=command_text,
            action_type=intent,
            response_text=response,
            success=success,
            source=source
        )

        gui.set_responding.emit(response)
        conv_manager.set_speaking(True)
        await tts.speak(response)
        conv_manager.set_speaking(False)

        # Si seguimos en conversación, actualizar GUI al modo conversación tras hablar
        if conv_manager.is_conversation_active():
            gui.set_conversation_mode.emit()


async def on_trigger(listener, tts, router, gemini, gui, memory, conv_manager, vision, pre_captured_text=None):
    """Acciones a realizar cuando se detecta el wake word o un follow-up."""

    if pre_captured_text:
        logger.info(f"Procesando follow-up: '{pre_captured_text}'")
        await process_command(pre_captured_text, listener, tts, router, gemini, gui, memory, conv_manager, vision)
        return

    # Activación normal por wake word
    logger.info("Protocolo JARVIS: Activado.")
    gui.set_wake.emit()

    conv_manager.set_speaking(True)
    await tts.speak("Sí, señor.")
    conv_manager.set_speaking(False)

    logger.info("<<< Escuchando orden... >>>")
    gui.set_listening.emit()

    command_text = listener.capture_command(timeout=7.0)

    if not command_text:
        response = no_command_response()
        gui.set_responding.emit(response)
        conv_manager.set_speaking(True)
        await tts.speak(response)
        conv_manager.set_speaking(False)
        return

    await process_command(command_text, listener, tts, router, gemini, gui, memory, conv_manager, vision)


def run_voice_loop(listener, tts, router, gemini, gui, memory, conv_manager, vision):
    def trigger_callback(pre_captured_text=None):
        asyncio.run(on_trigger(listener, tts, router, gemini, gui, memory, conv_manager, vision, pre_captured_text))

    try:
        listener.listen(trigger_callback, conv_manager=conv_manager)
    except Exception as e:
        logger.critical(f"Error fatal en el núcleo de voz: {e}")


def main():
    if not Config.validate():
        logger.error("Error validando configuración. Abortando.")
        sys.exit(1)

    app = QApplication(sys.argv)

    logger.info("--- JARVIS Voice Assistant (Fase 10: Screen Vision) ---")

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

    # Fase 8: Scheduler
    scheduler = JARVIScheduler(memory, gui_controller, tts)
    scheduler.start_monitor()

    # Fase 9: Conversation Manager + Hotkey
    conv_manager = ConversationManager(gui_controller)
    hotkey_manager = JARVISHotkeyManager(conv_manager)
    hotkey_manager.start()

    # Fase 10: Vision Service
    vision = VisionService(gemini_client=gemini)

    voice_thread = threading.Thread(
        target=run_voice_loop,
        args=(listener, tts, router, gemini, gui_controller, memory, conv_manager, vision),
        daemon=True
    )
    voice_thread.start()

    logger.info("JARVIS completo: GUI, Memoria, Planificador, Conversación, Hotkeys y Visión. Esperando comando...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
