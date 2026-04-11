import os
import subprocess
from core.logger import logger
from actions.system_actions import launch_steam

# Directorio de nombres amigables a procesos conocidos
# Puedes ajustar estas rutas o ejecutables específicos
APP_ALIASES = {
    "discord": "Discord.exe",
    "spotify": "Spotify.exe",
    "opera": "opera.exe",
    "opera gx": "opera.exe",
    "calculadora": "calc.exe",
    "bloc de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "visual studio code": "code", # Añadimos binario en PATH usualmente
    "vscode": "code",
    "explorador de archivos": "explorer.exe",
    "el explorador": "explorer.exe",
    "cmd": "cmd.exe",
    "terminal": "cmd.exe"
}

# Procesos críticos que JARVIS JAMÁS debe intentar cerrar (Blacklist de seguridad)
PROTECTED_PROCESSES = {
    "explorer.exe", 
    "winlogon.exe", 
    "csrss.exe", 
    "dwm.exe",
    "smss.exe",
    "svchost.exe",
    "taskmgr.exe",
    "system"
}

def open_application(app_name):
    """
    Intenta abrir una aplicación. Revisa el diccionario local primero; 
    si no la encuentra, intenta abrir un ejecutable general en Windows 
    o invoca a Steam como fallback heredado de la Fase 4.
    """
    clean_name = app_name.lower().strip()
    
    # Check Steam explicitly
    if clean_name == "steam":
        return launch_steam("steam")

    # Limpiar artículos comunes para no fallar el diccionario
    if clean_name.startswith("el "):
        clean_name = clean_name[3:]
    elif clean_name.startswith("la "):
        clean_name = clean_name[3:]

    # Si es conocida en nuestro diccionario de alias locales
    if clean_name in APP_ALIASES:
        target_exe = APP_ALIASES[clean_name]
        logger.info(f"Intentando abrir aplicación conocida: {target_exe}")
        try:
            # os.startfile respeta el PATH y los alias de Windows nativos
            os.startfile(target_exe)
            return f"Abriendo {clean_name}, señor."
        except Exception as e:
            logger.error(f"Error abriendo nativa ({target_exe}): {e}")
            # Intento de fallback vía terminal oculta (útil para cmd/calculadora antigua)
            try:
                subprocess.Popen(["start", f"{target_exe}"], shell=True)
                return f"Abriendo {clean_name}, señor."
            except Exception as e2:
                logger.error(f"Fallback fallido ({target_exe}): {e2}")
                return f"Ha ocurrido un error intentando abrir {clean_name}."

    # Si no tiene alias, podemos intentar adivinar si el usuario quiso abrir un .exe genérico
    # pero eso es arriesgado. En este diseño, delegamos a Steam por retrocompatibilidad:
    logger.info(f"Aplicación '{clean_name}' desconocida. Redirigiendo a búsqueda en Steam. (Fallback Phase 4)")
    # Envolvemos steam para que no diga "Abriendo calculadora en steam" si no lo encuentra.
    steam_result = launch_steam(clean_name)
    return steam_result


def close_application(app_name):
    """
    Cierra de forma segura un proceso usando taskkill, comprobando la lista de procesos críticos.
    """
    clean_name = app_name.lower().strip()
    
    # Averiguar el ejecutable (si existe alias, usarlo, de lo contrario inferir ".exe")
    target_exe = APP_ALIASES.get(clean_name, f"{clean_name.replace(' ', '')}.exe")
    
    # Comprobación de seguridad VITAL
    if target_exe.lower() in PROTECTED_PROCESSES:
        logger.warning(f"Intento bloqueado: el usuario intentó cerrar sistema crítico ({target_exe})")
        return f"Me temo que no puedo cerrar {app_name}, señor. Es un proceso vital del sistema."
        
    try:
        logger.info(f"Cerrando proceso: {target_exe}")
        # taskkill /IM proceso.exe /F
        result = subprocess.run(["taskkill", "/IM", target_exe, "/F"], capture_output=True, text=True)
        
        if result.returncode == 0:
            return f"Proceso {app_name} finalizado correctamente."
        elif "no se encontró" in result.stderr.lower() or "not found" in result.stderr.lower() or result.returncode == 128:
            return f"No encontré {app_name} ejecutándose en el sistema."
        else:
            return f"No he podido cerrar {app_name}. Es posible que necesite permisos de administrador."
            
    except Exception as e:
        logger.error(f"Error fatal intentando cerrar aplicación {target_exe}: {e}")
        return f"Ocurrió un fallo de sistema intentando forzar el cierre de {app_name}."
