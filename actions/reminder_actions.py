import time
import uuid
import datetime
from core.logger import logger

def _generate_id():
    return uuid.uuid4().hex[:8]

def compute_delay_seconds(duration, unit):
    """Convierte duración dictada a una cantidad de segundos."""
    try:
        val = int(duration)
    except:
        return None
    
    if "hora" in unit:
        return val * 3600
    elif "minuto" in unit:
        return val * 60
    return None

def create_timer(memory, duration, unit, label=None):
    """Crea un evento tipo timer."""
    seconds = compute_delay_seconds(duration, unit)
    if seconds is None:
        return "No he logrado calcular el tiempo para el temporizador, señor."
        
    trigger_epoch = time.time() + seconds
    msg = label if label else "Temporizador terminado"
    event_id = _generate_id()
    
    event = {
        "id": event_id,
        "type": "temporizador",
        "message": msg,
        "trigger_time": trigger_epoch,
        "status": "pending",
        "created_at": time.time()
    }
    
    memory.add_scheduled_event(event)
    return f"Temporizador de {duration} {unit} establecido, señor. El identificador es {event_id[:4]}."

def create_reminder(memory, message, duration, unit):
    """Crea un recordatorio a X tiempo de distancia."""
    seconds = compute_delay_seconds(duration, unit)
    if seconds is None:
        return "No pude comprender en cuánto tiempo desea este recordatorio."
        
    trigger_epoch = time.time() + seconds
    event_id = _generate_id()
    
    event = {
        "id": event_id,
        "type": "recordatorio",
        "message": message.capitalize(),
        "trigger_time": trigger_epoch,
        "status": "pending",
        "created_at": time.time()
    }
    
    memory.add_scheduled_event(event)
    return f"Le recordaré que {message} en {duration} {unit}, señor."

def create_alarm(memory, hour_str, minute_str):
    """Crea una alarma para una hora específica en formato 24H."""
    try:
        h = int(hour_str)
        m = int(minute_str)
    except:
        return "No he entendido bien la hora de la alarma, señor."
        
    now = datetime.datetime.now()
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    
    # Si la hora ya pasó hoy, se programa para mañana
    if target <= now:
        target = target + datetime.timedelta(days=1)
        
    trigger_epoch = target.timestamp()
    event_id = _generate_id()
    
    event = {
        "id": event_id,
        "type": "alarma",
        "message": f"Alarma de las {h:02d}:{m:02d}",
        "trigger_time": trigger_epoch,
        "status": "pending",
        "created_at": time.time()
    }
    
    memory.add_scheduled_event(event)
    day_str = "hoy" if target.day == now.day else "mañana"
    return f"Alarma configurada para {day_str} a las {h:02d}:{m:02d}, señor."

def cancel_matching_events(memory, event_type, query=None):
    """Cancela aquellos eventos que coincidan parcialmente (o el más próximo si es vago)."""
    events = memory.get_scheduled_events()
    pending = [e for e in events if e.get("status") == "pending" and event_type in e.get("type", "")]
    
    if not pending:
        return f"No encontré ningún {event_type} pendiente para cancelar, señor."
        
    # Filtrar por texto si hay query
    if query:
        q_clean = query.lower()
        pending = [e for e in pending if q_clean in e.get("message", "").lower()]
        if not pending:
            return f"No encontré un {event_type} pendiente relacionado con '{query}'."

    # Cancelamos el más antiguo creado que encaje
    target = pending[0]
    memory.update_event_status(target["id"], "cancelled")
    return f"He cancelado el {event_type} pendiente: {target['message']}."

def list_pending_events(memory):
    """Devuelve un listado fluido de alarmas y recordatorios vigentes."""
    events = memory.get_scheduled_events()
    pending = [e for e in events if e.get("status") == "pending"]
    
    if not pending:
        return "Actualmente no tiene ningún evento pendiente en su agenda, señor."
        
    timers = len([e for e in pending if e["type"] == "temporizador"])
    alarms = len([e for e in pending if e["type"] == "alarma"])
    reminders = len([e for e in pending if e["type"] == "recordatorio"])
    
    resumen = []
    if timers > 0: resumen.append(f"{timers} temporizadores")
    if alarms > 0: resumen.append(f"{alarms} alarmas")
    if reminders > 0: resumen.append(f"{reminders} recordatorios")
    
    response = f"Tiene pendiente " + ", ".join(resumen) + ". "
    
    # Detalle del evento que ocurrirá más pronto
    soonest = min(pending, key=lambda x: x["trigger_time"])
    minutes_left = int(max(0, soonest["trigger_time"] - time.time()) / 60)
    
    response += f"El más próximo es {soonest['message']} en aproximadamente {minutes_left} minutos."
    return response

def get_time_remaining(memory):
    events = memory.get_scheduled_events()
    pending = [e for e in events if e.get("status") == "pending" and e.get("type") == "temporizador"]
    
    if not pending:
        return "No hay ningún temporizador activo actualmente."
        
    soonest = min(pending, key=lambda x: x["trigger_time"])
    secs_left = int(max(0, soonest["trigger_time"] - time.time()))
    
    mins = secs_left // 60
    secs = secs_left % 60
    
    if mins > 0:
        return f"Quedan {mins} minutos y {secs} segundos en el temporizador, señor."
    return f"Quedan escasos {secs} segundos, señor."
