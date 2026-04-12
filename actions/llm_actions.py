from services.performance_manager import PerformanceProfile

def set_performance_profile(perf_manager, llm_service, profile_name):
    """Acción para cambiar el perfil de rendimiento."""
    success = perf_manager.set_profile(profile_name)
    if success:
        # Sincronizar el modelo inmediatamente
        llm_service.ollama.model = perf_manager.model_name
        return f"Perfil cambiado a modo {profile_name}, señor. El sistema se ha optimizado."
    return "No he podido reconocer ese perfil de rendimiento."

def set_llm_backend(llm_service, backend):
    """Acción para cambiar el backend de IA (local/cloud)."""
    success = llm_service.set_backend(backend)
    if success:
        return f"Cerebro principal cambiado a {backend}, señor."
    return "Ese backend no está disponible."

def unload_model(llm_service):
    """Acción para liberar la VRAM manualmente."""
    llm_service.ollama.unload()
    return "Memoria de video liberada, señor. El modelo ha sido descargado."

def get_llm_status(llm_service, perf_manager):
    """Retorna un reporte del estado de la IA."""
    status = llm_service.get_status()
    p_status = perf_manager.get_status()
    
    return (f"Estoy usando el backend {status['backend']} con el modelo {status['model']}. "
            f"El perfil de rendimiento actual es {p_status['profile']}.")
