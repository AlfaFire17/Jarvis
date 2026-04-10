import os
import json
from core.config import Config
from core.logger import logger

class AgendaService:
    def __init__(self):
        self.file_path = Config.AGENDA_PATH
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea el archivo de agenda si no existe."""
        if not os.path.exists(self.file_path):
            logger.info(f"Creando nuevo archivo de agenda en: {self.file_path}")
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)

    def get_events(self):
        """Lee todos los eventos de la agenda."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo agenda: {e}")
            return []

    def add_event(self, title, date, description=""):
        """Añade un nuevo evento a la agenda."""
        events = self.get_events()
        new_event = {
            "title": title,
            "date": date,
            "description": description
        }
        events.append(new_event)
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=4, ensure_ascii=False)
            logger.info(f"Evento añadido: {title}")
            return True
        except Exception as e:
            logger.error(f"Error guardando evento: {e}")
            return False

    def validate_structure(self):
        """Valida que el JSON tenga la estructura correcta."""
        events = self.get_events()
        if not isinstance(events, list):
            return False
        return True
