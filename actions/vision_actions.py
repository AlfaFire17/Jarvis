from core.logger import logger


def analyze_current_screen(vision_service):
    """Analiza la pantalla actual y devuelve un resumen visual."""
    return vision_service.analyze_screen()


def read_screen_text(vision_service):
    """Lee y extrae el texto visible en pantalla."""
    return vision_service.read_screen_text()


def summarize_screen(vision_service):
    """Resume el contenido visible en pantalla."""
    return vision_service.summarize_screen()


def explain_screen_error(vision_service):
    """Detecta y explica errores visibles en pantalla."""
    return vision_service.explain_screen_error()


def get_active_window_info(vision_service):
    """Devuelve el título de la ventana activa."""
    title = vision_service.get_active_window_title()
    if title and title != "Desconocida":
        return f"La ventana activa es: {title}."
    return "No he podido determinar la ventana activa, señor."


def copy_visible_text(vision_service):
    """Copia el texto visible al portapapeles."""
    return vision_service.copy_screen_text_to_clipboard()


def followup_visual(vision_service, question):
    """Realiza un follow-up sobre el contexto visual reciente."""
    return vision_service.followup_analysis(question)
