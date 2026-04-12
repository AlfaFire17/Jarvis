from core.logger import logger

def remember_fact(memory_service, text):
    """Guarda un texto tal cual como un hecho en la memoria persistente."""
    if not text:
        return "Lo siento señor, no detecté qué es exactamente lo que debo recordar."
        
    memory_service.save_fact(text)
    return "Hecho. Lo he anotado en su memoria de perfil persistente, señor."

def forget_fact(memory_service, keyword):
    """Busca y elimina un hecho en base a una palabra clave."""
    if not keyword:
        return "Lo siento, necesito que especifique qué es lo que debo olvidar."
        
    count = memory_service.delete_fact(keyword)
    if count > 0:
        return f"De acuerdo. He borrado {count} elementos de la memoria relacionados con '{keyword}'."
    else:
        return f"No he encontrado nada en la memoria persistente sobre '{keyword}'."

def query_profile(memory_service):
    """Devuelve todo el conglomerado de hechos almacenados."""
    return memory_service.get_profile_summary()
