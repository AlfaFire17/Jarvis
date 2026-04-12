import os
import json
from datetime import datetime
from core.logger import logger
from core.config import Config

class MemoryService:
    def __init__(self):
        self.file_path = Config.MEMORY_FILE_PATH
        self.max_history = 200 # MAX interactions to keep
        self._ensure_data_directory()
        self.memory = self.load_memory()

    def _ensure_data_directory(self):
        """Asegura que el directorio data/ exista."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def load_memory(self):
        """Carga el JSON de memoria o lo crea si no existe/está corrupto."""
        default_structure = {
            "sessions": [], 
            "scheduled_events": [],
            "persistent_profile_memory": {
                "facts": []
            }
        }
        
        if not os.path.exists(self.file_path):
            logger.info("Archivo de memoria no encontrado. Inicializando memoria nueva.")
            return default_structure

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                dirty = False
                if "sessions" not in data:
                    logger.warning("Estructura JSON inválida. Regenerando 'sessions'.")
                    data["sessions"] = []
                    dirty = True
                if "scheduled_events" not in data:
                    logger.info("Añadiendo tabla 'scheduled_events' al JSON heredado.")
                    data["scheduled_events"] = []
                    dirty = True
                if "persistent_profile_memory" not in data:
                    logger.info("Añadiendo perfil persistente al JSON heredado.")
                    data["persistent_profile_memory"] = {"facts": []}
                    dirty = True
                if "facts" not in data.get("persistent_profile_memory", {}):
                    data["persistent_profile_memory"] = {"facts": []}
                    dirty = True
                
                # Opcional: limpiar eventos anticuados / disparados / cancelados masivos si hace falta
                
                return data
        except json.JSONDecodeError:
            logger.error("Archivo de memoria corrupto. Creando uno nuevo de forma segura.")
            return default_structure
        except Exception as e:
            logger.error(f"Error cargando memoria JSON: {e}")
            return default_structure

    def _save_memory(self):
        """Guarda el JSON de forma atómica usando un archivo .tmp para no corromper datos."""
        tmp_path = self.file_path + ".tmp"
        
        # Trim history if necessary before saving
        if len(self.memory["sessions"]) > self.max_history:
            self.memory["sessions"] = self.memory["sessions"][-self.max_history:]
            
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            
            # Atomic replace (seguro en Windows con Python moderno y POSIX)
            os.replace(tmp_path, self.file_path)
        except Exception as e:
            logger.error(f"Error crítico guardando la memoria: {e}")

    def save_interaction(self, user_input, action_type, response_text, success=True, source="local"):
        """Guarda una nueva interacción en el JSON."""
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "wake_word": Config.WAKE_PHRASE,
            "user_input": user_input,
            "action_type": action_type,
            "response_text": response_text,
            "source": source,
            "success": success
        }
        
        self.memory["sessions"].append(entry)
        self._save_memory()

    def get_recent_interactions(self, limit=3):
        """Devuelve un resumen coloquial de las últimas interacciones."""
        sessions = self.memory.get("sessions", [])
        if not sessions:
            return "Aún no tengo ninguna conversación guardada en mi memoria, señor."
            
        recent = sessions[-limit:]
        
        # Generar resumen legible para TTS
        resumen = "Las últimas interacciones fueron: "
        for idx, s in enumerate(recent):
            resumen += f"Usted pidió '{s['user_input']}' y yo ejecuté la acción '{s['action_type']}'. "
            
        return resumen

    def search_interactions(self, keyword):
        """Busca en el historial por palabra clave."""
        sessions = self.memory.get("sessions", [])
        clean_key = keyword.lower().strip()
        
        # Buscar de más reciente a más antigua
        for s in reversed(sessions):
            if clean_key in s['user_input'].lower() or clean_key in s['response_text'].lower():
                return f"Encontré esto sobre {keyword}: Usted dijo '{s['user_input']}' y yo respondí '{s['response_text']}'."
                
        return f"No he encontrado nada en mi memoria reciente sobre '{keyword}', señor."

    def get_last_command(self):
        """Devuelve exactamente la última orden ejecutada."""
        sessions = self.memory.get("sessions", [])
        if not sessions:
            return "No existe ningún comando previo registrado en mi base de datos, señor."
            
        ultimo = sessions[-1]
        return f"El último comando que me ordenó fue '{ultimo['user_input']}', el cual resultó en la acción '{ultimo['action_type']}'."

    # --- FUNCIONES DE SCHEDULING (Fase 8) ---
    def get_scheduled_events(self):
        """Devuelve la lista actual de eventos programados (alarmas/recordatorios)."""
        return self.memory.get("scheduled_events", [])

    def add_scheduled_event(self, event_dict):
        """Añade un nuevo evento validando la estructura básica."""
        if "scheduled_events" not in self.memory:
            self.memory["scheduled_events"] = []
            
        self.memory["scheduled_events"].append(event_dict)
        self._save_memory()
        
    def update_event_status(self, event_id, new_status):
        """Actualiza el estado de un evento (e.g., 'pending' -> 'triggered' o 'cancelled')."""
        events = self.memory.get("scheduled_events", [])
        for e in events:
            if e.get("id") == event_id:
                e["status"] = new_status
                logger.info(f"Evento {event_id} marcado como {new_status}")
                self._save_memory()
                return True
        return False

    # --- FUNCIONES DE PERFIL PERSISTENTE (Fase 9) ---
    def save_fact(self, fact_text):
        """Guarda un nuevo hecho en la memoria persistente."""
        import uuid
        fact_id = "mem_" + uuid.uuid4().hex[:8]
        fact_entry = {
            "id": fact_id,
            "value": fact_text,
            "created_at": datetime.now().isoformat()
        }
        
        profile = self.memory.setdefault("persistent_profile_memory", {"facts": []})
        facts = profile.setdefault("facts", [])
        facts.append(fact_entry)
        self._save_memory()
        return True
        
    def delete_fact(self, keyword):
        """Borra hechos que coincidan con la keyword."""
        profile = self.memory.get("persistent_profile_memory", {})
        facts = profile.get("facts", [])
        
        clean_key = keyword.lower().strip()
        new_facts = [f for f in facts if clean_key not in f.get("value", "").lower()]
        
        deleted_count = len(facts) - len(new_facts)
        if deleted_count > 0:
            profile["facts"] = new_facts
            self._save_memory()
        
        return deleted_count

    def get_profile_summary(self):
        """Devuelve un string con todos los hechos persistentes almacenados."""
        profile = self.memory.get("persistent_profile_memory", {})
        facts = profile.get("facts", [])
        
        if not facts:
            return "Aún no me ha pedido que memorice ningún dato sobre usted, señor."
            
        resumen = "Esto es lo que recuerdo sobre usted: "
        for f in facts:
            resumen += f"{f['value']}. "
            
        return resumen

