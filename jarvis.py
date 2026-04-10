import asyncio
import sys
from core.config import Config
from core.logger import logger
from voice.listener import VoiceListener
from voice.tts import TTSProvider
from core.intent_router import IntentRouter, Intent
from actions.system_actions import open_perplexity, open_youtube, say_hello, no_command_response
from integrations.gemini_client import GeminiClient

async def on_trigger(listener, tts, router, gemini):
    """Acciones a realizar cuando se detecta el wake word."""
    logger.info("Protocolo JARVIS: Activado.")
    
    # Visual feedback: listening
    logger.info("<<< Escuchando orden... >>>")
    
    # 1. Capturar la orden del usuario
    # Damos un poco más de tiempo para la orden (7 segundos)
    command_text = listener.capture_command(timeout=7.0)
    
    if not command_text:
        response = no_command_response()
        await tts.speak(response)
        return

    # 2. Enrutar la intención
    intent, original_text = router.route(command_text)
    
    # 3. Ejecutar acción
    if intent == Intent.GREETING:
        response = say_hello()
        await tts.speak(response)
        
    elif intent == Intent.OPEN_PERPLEXITY:
        await tts.speak("Abriendo Perplexity, señor. Siempre es bueno buscar respuestas.")
        open_perplexity()
        
    elif intent == Intent.OPEN_YOUTUBE:
        await tts.speak("Entendido. Abriendo YouTube.")
        open_youtube()
        
    elif intent == Intent.GENERAL_QUERY:
        # Consulta real a Gemini
        await tts.speak("Consultando en mi base de datos, un momento...")
        answer = gemini.ask(original_text)
        await tts.speak(answer)
    
    elif intent == Intent.UNKNOWN:
        response = no_command_response()
        await tts.speak(response)

def main():
    # 1. Validar configuración
    if not Config.validate():
        logger.error("Error validando configuración. Abortando.")
        sys.exit(1)

    # 2. Inicializar servicios
    logger.info("--- JARVIS Voice Assistant (Fase 2: Gemini Integration) ---")
    
    tts = TTSProvider()
    router = IntentRouter()
    gemini = GeminiClient()
    listener = VoiceListener()

    if not listener.initialize():
        logger.error("No se pudo inicializar el sistema de voz.")
        sys.exit(1)

    # 3. Definir el callback de disparo
    def trigger_callback():
        # Ejecutar el flujo de comando en el loop de eventos
        asyncio.run(on_trigger(listener, tts, router, gemini))

    # 4. Iniciar escucha
    try:
        listener.listen(trigger_callback)
    except KeyboardInterrupt:
        logger.info("Deteniendo JARVIS...")
    except Exception as e:
        logger.critical(f"Error fatal en el núcleo: {e}")

if __name__ == "__main__":
    main()

