from core.logger import logger

def generate_daily_briefing_action(briefing_service, force=False):
    """
    Acción invocable desde el router para generar o actualizar el informe diario.
    """
    try:
        res = briefing_service.generate_briefing(force=force, mode="manual_command", open_browser=True)
        if not res.get("success"):
            return "Lo siento señor, ha ocurrido un problema generando su informe diario."

        if force:
            return "He actualizado y abierto su informe diario con las últimas noticias, correo y mercados, señor."
        else:
            return "He preparado y abierto su informe diario en el navegador, señor."

    except Exception as e:
        logger.error(f"Error en acción de generación de informe diario: {e}")
        return "Ha ocurrido un error inesperado al procesar su informe diario, señor."

def open_latest_daily_briefing_action(briefing_service):
    """
    Acción para abrir el informe diario existente o generarlo si no existe.
    """
    try:
        opened = briefing_service.open_report()
        if opened:
            return "Abriendo su informe diario en el navegador, señor."
        
        # Si no existía informe, generarlo
        res = briefing_service.generate_briefing(force=False, mode="manual_command", open_browser=True)
        if res.get("success"):
            return "He generado y abierto su informe diario de hoy, señor."
        return "No he podido abrir ni generar el informe diario, señor."

    except Exception as e:
        logger.error(f"Error en acción de apertura de informe diario: {e}")
        return "Lo siento señor, no he podido abrir el informe diario."

def get_daily_briefing_status_action(briefing_service):
    """
    Devuelve el estado actual de la generación del informe diario.
    """
    try:
        data = briefing_service.memory.get_daily_briefing_data()
        last_date = data.get("last_auto_generated_date", "ninguna")
        status = data.get("last_generation_status", "desconocido")
        
        if last_date:
            return f"El último informe diario fue generado correctamente para la fecha {last_date}, señor."
        return "Aún no se ha generado ningún informe diario hoy, señor."
    except Exception as e:
        logger.error(f"Error consultando estado del informe diario: {e}")
        return "No he podido verificar el estado del informe diario, señor."

def configure_google_integrations_action(auth_manager):
    """
    Inicia el flujo de autenticación interactivo de Google Workspace.
    """
    try:
        if not auth_manager.has_credentials_file():
            return "No he encontrado el archivo credentials.json. Por favor, coloque sus credenciales OAuth en la carpeta data/private/credentials.json para conectar Google Calendar y Gmail."

        creds = auth_manager.get_credentials(interactive=True)
        if creds and creds.valid:
            return "Excelente. La autenticación con Google Workspace para Calendar y Gmail ha sido completada correctamente, señor."
        return "No se ha completado la autorización con Google Workspace, señor."
    except Exception as e:
        logger.error(f"Error en configuración interactiva de Google: {e}")
        return "Ha ocurrido un fallo durante el proceso de autenticación con Google."
