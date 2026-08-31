import re
import html
from datetime import datetime, timedelta
from core.logger import logger
from integrations.google_auth import GoogleAuthManager

try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

class GmailClient:
    """
    Cliente para la API oficial de Gmail (Estricto solo lectura).
    No modifica etiquetas, no marca como leído, no envía ni elimina correos.
    """
    def __init__(self, auth_manager=None):
        self.auth_manager = auth_manager or GoogleAuthManager()

    def get_recent_messages(self, lookback_days=3, max_results=30):
        """
        Recupera metadatos y extractos de los correos recientes fuera de Spam/Papelera.
        """
        if not GOOGLE_API_AVAILABLE:
            return {
                "connected": False,
                "reason": "Librerías de Google API no instaladas.",
                "messages": []
            }

        creds = self.auth_manager.get_credentials(interactive=False)
        if not creds:
            has_creds = self.auth_manager.has_credentials_file()
            reason = "Se requiere iniciar sesión." if has_creds else "credentials.json no encontrado."
            return {
                "connected": False,
                "reason": reason,
                "messages": []
            }

        try:
            service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

            # Query de búsqueda segura (excluye Spam y Papelera)
            query = f"-in:spam -in:trash newer_than:{lookback_days}d"
            
            response = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages_meta = response.get('messages', [])
            if not messages_meta and lookback_days < 7:
                # Ampliar rango si no hay correos en los últimos días
                query_fallback = f"-in:spam -in:trash newer_than:7d"
                response = service.users().messages().list(
                    userId='me',
                    q=query_fallback,
                    maxResults=max_results
                ).execute()
                messages_meta = response.get('messages', [])

            result_messages = []
            for msg_item in messages_meta:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg_item['id'],
                    format='full'
                ).execute()
                
                parsed = self._parse_message(msg_data)
                if parsed:
                    result_messages.append(parsed)

            return {
                "connected": True,
                "reason": "OK",
                "messages": result_messages
            }

        except Exception as e:
            logger.error(f"Error consultando Gmail API: {e}")
            return {
                "connected": False,
                "reason": f"Error de consulta: {str(e)}",
                "messages": []
            }

    def _parse_message(self, msg_data):
        """Parsea la cabecera y snippet de un mensaje de Gmail."""
        try:
            headers = msg_data.get('payload', {}).get('headers', [])
            headers_dict = {h['name'].lower(): h['value'] for h in headers}

            subject = headers_dict.get('subject', '(Sin asunto)').strip()
            sender_raw = headers_dict.get('from', 'Desconocido').strip()
            date_raw = headers_dict.get('date', '')

            # Formatear remitente de forma amigable (e.g. "Amazon.es <no-reply@amazon.es>" -> "Amazon.es")
            sender_name, sender_email = self._split_sender(sender_raw)

            # Saneamiento del snippet
            snippet = msg_data.get('snippet', '')
            snippet_clean = html.unescape(snippet).strip()
            snippet_clean = re.sub(r'\s+', ' ', snippet_clean)

            # Obtener identificador/enlace
            msg_id = msg_data.get('id', '')
            web_link = f"https://mail.google.com/mail/u/0/#inbox/{msg_id}" if msg_id else ""

            # Extraer fecha formateada
            internal_date_ms = int(msg_data.get('internalDate', 0))
            if internal_date_ms > 0:
                msg_dt = datetime.fromtimestamp(internal_date_ms / 1000.0)
                date_display = self._format_relative_time(msg_dt)
            else:
                date_display = date_raw

            label_ids = msg_data.get('labelIds', [])

            return {
                "id": msg_id,
                "subject": subject,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "snippet": snippet_clean,
                "date_display": date_display,
                "link": web_link,
                "labels": label_ids
            }
        except Exception as e:
            logger.warning(f"Error parseando mensaje de Gmail: {e}")
            return None

    def _split_sender(self, sender_raw):
        """Extrae el nombre visual y el email del remitente."""
        match = re.match(r'^(.*?)\s*<([^>]+)>$', sender_raw)
        if match:
            name = match.group(1).replace('"', '').strip()
            email = match.group(2).strip()
            return name if name else email, email
        return sender_raw.replace('"', '').strip(), sender_raw.strip()

    def _format_relative_time(self, msg_dt):
        """Genera un string relativo amigable (hace 2 h, hoy a las 14:20, etc.)."""
        now = datetime.now()
        diff = now - msg_dt
        
        if diff.total_seconds() < 3600:
            mins = max(1, int(diff.total_seconds() // 60))
            return f"Hace {mins} min"
        elif diff.total_seconds() < 86400 and msg_dt.date() == now.date():
            return f"Hoy {msg_dt.strftime('%H:%M')}"
        elif diff.days == 1:
            return f"Ayer {msg_dt.strftime('%H:%M')}"
        else:
            return msg_dt.strftime('%d %b %H:%M')
