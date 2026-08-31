from datetime import datetime, timedelta, timezone
from core.logger import logger
from integrations.google_auth import GoogleAuthManager

try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

IMPORTANT_KEYWORDS = [
    "entrega", "examen", "cita", "reunión", "reunion", "pago", "entrevista",
    "viaje", "cumpleaños", "cumpleanos", "medico", "médico", "presentacion",
    "presentación", "proyecto", "vuelo", "veterinario", "parcial", "final", "deadline"
]

class GoogleCalendarClient:
    """
    Cliente para la API oficial de Google Calendar (Solo lectura).
    Recupera la agenda del día y eventos importantes próximos.
    """
    def __init__(self, auth_manager=None):
        self.auth_manager = auth_manager or GoogleAuthManager()

    def get_agenda(self, days_ahead=14):
        """
        Obtiene los eventos de hoy y los próximos eventos destacados en un rango de días.
        Devuelve una estructura normalizada tolerante a fallos.
        """
        if not GOOGLE_API_AVAILABLE:
            return {
                "connected": False,
                "reason": "Librerías de Google API no instaladas.",
                "today_events": [],
                "upcoming_events": []
            }

        creds = self.auth_manager.get_credentials(interactive=False)
        if not creds:
            has_creds = self.auth_manager.has_credentials_file()
            reason = "Se requiere iniciar sesión." if has_creds else "credentials.json no encontrado."
            return {
                "connected": False,
                "reason": reason,
                "today_events": [],
                "upcoming_events": []
            }

        try:
            service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
            
            # Zona horaria local
            now = datetime.now().astimezone()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1) - timedelta(microseconds=1)
            upcoming_end = today_start + timedelta(days=days_ahead + 1)

            time_min_str = today_start.isoformat()
            time_max_str = upcoming_end.isoformat()

            # Consultar eventos del calendario principal
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            raw_events = events_result.get('items', [])
            
            today_events = []
            upcoming_events = []

            for event in raw_events:
                parsed = self._parse_event(event, now, today_start, today_end)
                if parsed:
                    if parsed["is_today"]:
                        today_events.append(parsed)
                    else:
                        upcoming_events.append(parsed)

            return {
                "connected": True,
                "reason": "OK",
                "today_events": today_events,
                "upcoming_events": upcoming_events
            }

        except Exception as e:
            logger.error(f"Error consultando Google Calendar API: {e}")
            return {
                "connected": False,
                "reason": f"Error de consulta: {str(e)}",
                "today_events": [],
                "upcoming_events": []
            }

    def _parse_event(self, event, now, today_start, today_end):
        """Parsea y enriquece un evento individual de Google Calendar."""
        try:
            summary = event.get('summary', 'Sin título')
            start_raw = event.get('start', {})
            end_raw = event.get('end', {})

            is_all_day = 'date' in start_raw
            
            if is_all_day:
                start_dt = datetime.strptime(start_raw['date'], '%Y-%m-%d').astimezone(now.tzinfo)
                end_dt = datetime.strptime(end_raw['date'], '%Y-%m-%d').astimezone(now.tzinfo)
                time_str = "Todo el día"
            else:
                start_str = start_raw.get('dateTime')
                end_str = end_raw.get('dateTime')
                start_dt = datetime.fromisoformat(start_str).astimezone(now.tzinfo)
                end_dt = datetime.fromisoformat(end_str).astimezone(now.tzinfo)
                time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"

            # Determinar si pertenece a hoy
            is_today = (today_start <= start_dt <= today_end) or (is_all_day and start_dt.date() == today_start.date())

            # Calcular tiempo restante o cuenta atrás
            time_until = ""
            if is_today:
                if is_all_day:
                    time_until = "Hoy"
                elif now > end_dt:
                    time_until = "Finalizado"
                elif now >= start_dt and now <= end_dt:
                    time_until = "En curso"
                else:
                    diff = start_dt - now
                    hours, remainder = divmod(int(diff.total_seconds()), 3600)
                    minutes = remainder // 60
                    if hours > 0:
                        time_until = f"faltan {hours} h {minutes} min"
                    else:
                        time_until = f"faltan {minutes} min"
            else:
                days_left = (start_dt.date() - now.date()).days
                if days_left == 1:
                    time_until = "Mañana"
                else:
                    time_until = f"faltan {days_left} días"

            # Detectar si es importante por palabra clave o proximidad
            clean_summary = summary.lower()
            keyword_match = any(kw in clean_summary for kw in IMPORTANT_KEYWORDS)
            is_upcoming_soon = not is_today and (start_dt.date() - now.date()).days <= 7
            is_important = keyword_match or is_upcoming_soon

            location = event.get('location', '').strip()
            html_link = event.get('htmlLink', '')

            return {
                "id": event.get("id"),
                "summary": summary,
                "start_dt": start_dt.isoformat(),
                "date_display": start_dt.strftime('%d %b').upper(),
                "time_str": time_str,
                "time_until": time_until,
                "location": location,
                "link": html_link,
                "is_today": is_today,
                "is_all_day": is_all_day,
                "is_important": is_important
            }
        except Exception as e:
            logger.warning(f"No se pudo parsear un evento de calendario: {e}")
            return None
