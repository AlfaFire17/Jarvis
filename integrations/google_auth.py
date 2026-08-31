import os
import json
from core.logger import logger
from core.config import Config

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logger.warning("Librerías de Google OAuth no disponibles.")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

class GoogleAuthManager:
    """
    Gestor de autenticación unificada con OAuth 2.0 para Google Workspace (Calendar + Gmail).
    Mantiene tokens y credenciales de forma privada y en ámbitos exclusivamente de solo lectura.
    """
    def __init__(self):
        self.credentials_path = self._resolve_credentials_path()
        self.token_path = Config.GOOGLE_TOKEN_PATH
        self._ensure_private_directory()

    def _ensure_private_directory(self):
        """Asegura que el directorio data/private exista."""
        os.makedirs(Config.PRIVATE_DATA_DIR, exist_ok=True)
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)

    def _resolve_credentials_path(self):
        """Busca el archivo credentials.json en data/private/ o en la raíz del proyecto."""
        if os.path.exists(Config.GOOGLE_CREDENTIALS_PATH):
            return Config.GOOGLE_CREDENTIALS_PATH
        elif os.path.exists(Config.GOOGLE_CREDENTIALS_FALLBACK_PATH):
            return Config.GOOGLE_CREDENTIALS_FALLBACK_PATH
        return None

    def has_credentials_file(self):
        """Comprueba si existe un archivo credentials.json configurado."""
        return self._resolve_credentials_path() is not None

    def get_credentials(self, interactive=False):
        """
        Obtiene credenciales válidas de Google.
        Si el token ha caducado, se refresca automáticamente.
        Si `interactive` es True y no hay token pero existe credentials.json, inicia el flujo OAuth del navegador.
        """
        if not GOOGLE_AUTH_AVAILABLE:
            logger.warning("OAuth de Google no disponible (faltan módulos).")
            return None

        creds = None

        # Cargar token existente si existe
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                logger.error(f"Error al cargar token de Google: {e}")
                creds = None

        # Validar o refrescar credenciales
        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refrescando token de acceso de Google...")
                creds.refresh(Request())
                self._save_token(creds)
                return creds
            except Exception as e:
                logger.error(f"Error al refrescar token de Google: {e}")
                creds = None

        # Autenticación interactiva la primera vez
        cred_file = self._resolve_credentials_path()
        if interactive and cred_file:
            try:
                logger.info("Iniciando flujo de autorización OAuth local para Google Workspace...")
                flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
                creds = flow.run_local_server(port=0, prompt='consent')
                self._save_token(creds)
                logger.info("Autorización de Google completada y token guardado correctamente.")
                return creds
            except Exception as e:
                logger.error(f"Error en el flujo de autorización OAuth: {e}")
                return None

        if not cred_file:
            logger.info("No se encontró credentials.json. Google Workspace permanecerá desactivado.")

        return None

    def _save_token(self, creds):
        """Guarda las credenciales autorizadas en data/private/google_token.json."""
        try:
            self._ensure_private_directory()
            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
        except Exception as e:
            logger.error(f"Error guardando token de Google: {e}")

    def is_authenticated(self):
        """Verifica si A.L.F.A. tiene credenciales de Google funcionales."""
        creds = self.get_credentials(interactive=False)
        return creds is not None and creds.valid
