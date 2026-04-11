import time
import asyncio
import threading
from winotify import Notification, audio
from core.logger import logger
from core.config import Config

class JARVIScheduler:
    def __init__(self, memory, gui_controller, tts, voice_loop=None):
        self.memory = memory
        self.gui_controller = gui_controller
        self.tts = tts
        self.voice_loop = voice_loop
        self._running = False
        self._thread = None

    def start_monitor(self):
        """Inicia el monitor en un hilo secundario independiente."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info("JARVIScheduler iniciado satisfactoriamente en segundo plano.")

    def stop_monitor(self):
        self._running = False

    def _monitor_loop(self):
        """Revisa continuamente los eventos programados pendientes."""
        while self._running:
            try:
                now_ts = time.time()
                events = self.memory.get_scheduled_events()
                
                for event in events:
                    if event.get("status") == "pending":
                        trigger_epoch = event.get("trigger_time", 0)
                        
                        if trigger_epoch <= now_ts:
                            logger.info(f"Evento disparado: {event.get('message')} (ID: {event.get('id')})")
                            self._trigger_event(event)

            except Exception as e:
                logger.error(f"Error en JARVIScheduler loop: {e}")
            
            # Chequear cada 3 segundos evita colapsar el procesador
            time.sleep(3)

    def _trigger_event(self, event):
        """Ejecuta la notificación gráfica y auditiva, y actualiza JSON."""
        event_type = event.get("type", "recordatorio")
        message = event.get("message", "Evento programado")
        
        # 1. Update status
        self.memory.update_event_status(event.get("id"), "triggered")

        # 2. Native Windows Notification
        try:
            toast = Notification(
                app_id="JARVIS Assistant",
                title=f"JARVIS {event_type.capitalize()}",
                msg=message.capitalize(),
                duration="long"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logger.error(f"Error lanzando Windows Toast: {e}")

        # 3. GUI Overlay Alert
        alert_text = f"¡{event_type.upper()}!\n{message}"
        self.gui_controller.set_responding.emit(alert_text)

        # 4. Spoken Audio
        spoken_text = f"Señor, el {event_type} ha finalizado: {message}"
        
        if self.tts:
            try:
                # Correr modo fire-and-forget simulado para no trabar el scheduler
                threading.Thread(target=lambda: asyncio.run(self.tts.speak(spoken_text)), daemon=True).start()
            except Exception as e:
                logger.error(f"Error reproduciendo TTS desde scheduler: {e}")
