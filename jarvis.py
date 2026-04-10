import asyncio
import sys
from core.config import Config
from core.logger import logger
from voice.listener import VoiceListener
from voice.tts import TTSProvider
from core.intent_router import IntentRouter, Intent
from actions.system_actions import open_perplexity, open_youtube, say_hello, no_command_response
from integrations.perplexity_client import PerplexityClient

async def on_trigger(listener, tts, router, perplexity):
    """Acciones a realizar cuando se detecta el wake word."""
    logger.info("Protocolo JARVIS: Activado.")
    
    # Feedback visual/log: estamos escuchando
    logger.info("<<< Escuchando orden... >>>")
    
    # 1. Capturar la orden del usuario
    command_text = listener.capture_command(timeout=5.0)
    
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
        await tts.speak("Abriendo Perplexity, señor.")
        open_perplexity()
        
    elif intent == Intent.OPEN_YOUTUBE:
        await tts.speak("Abriendo YouTube, señor.")
        open_youtube()
        
    elif intent == Intent.GENERAL_QUERY:
        # Consulta real a Perplexity
        await tts.speak("Consultando con mi motor de búsqueda...")
        answer = perplexity.query(original_text)
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
    logger.info("--- JARVIS Voice Assistant (Fase 2: Comando Único) ---")
    
    tts = TTSProvider()
    router = IntentRouter()
    perplexity = PerplexityClient()
    listener = VoiceListener()

    if not listener.initialize():
        logger.error("No se pudo inicializar el modelo de voz.")
        sys.exit(1)

    # 3. Definir el callback de disparo
    def trigger_callback():
        # Ejecutar el flujo de comando en el loop de eventos
        asyncio.run(on_trigger(listener, tts, router, perplexity))

    # 4. Iniciar escucha
    try:
        listener.listen(trigger_callback)
    except KeyboardInterrupt:
        logger.info("Deteniendo JARVIS...")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")

if __name__ == "__main__":
    main()
