import asyncio
import sys
from core.config import Config
from core.logger import logger
from voice.listener import VoiceListener
from voice.tts import TTSProvider
from actions.system_actions import open_browser_with_urls, say_hello
from services.agenda_service import AgendaService
from integrations.perplexity_client import PerplexityClient

async def on_trigger(tts, agenda, perplexity):
    """Acciones a realizar cuando se detecta el comando de voz."""
    logger.info("Procesando comando JARVIS...")
    
    # Saludo inicial
    greeting = say_hello()
    await tts.speak(greeting)
    
    # Acción de prueba: abrir apps
    open_browser_with_urls()
    
    # Log de estado de servicios
    logger.info(f"Agenda actual eventos: {len(agenda.get_events())}")
    
    # Prueba técnica de Perplexity (Opcional en logs para esta fase)
    # response = perplexity.test_connection()
    # logger.info(f"Test Perplexity: {response}")

def main():
    # 1. Validar configuración
    if not Config.validate():
        logger.error("Error validando configuración. Abortando.")
        sys.exit(1)

    # 2. Inicializar servicios
    logger.info("--- JARVIS Voice Assistant Iniciado (Fase 1) ---")
    
    tts = TTSProvider()
    agenda = AgendaService()
    perplexity = PerplexityClient()
    listener = VoiceListener()

    if not listener.initialize():
        logger.error("No se pudo inicializar el modelo de voz.")
        sys.exit(1)

    # 3. Definir el callback de disparo
    def trigger_callback():
        # Ejecutar en el bucle de eventos asíncrono
        asyncio.run(on_trigger(tts, agenda, perplexity))

    # 4. Iniciar escucha
    try:
        listener.listen(trigger_callback)
    except KeyboardInterrupt:
        logger.info("Deteniendo JARVIS...")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")

if __name__ == "__main__":
    main()
