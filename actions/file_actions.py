import os
from pathlib import Path
from core.logger import logger
from services.file_search_service import FileSearchService

# Folder alias mapping
KNOWN_FOLDERS = {
    "descargas": "Downloads",
    "documentos": "Documents",
    "mis documentos": "Documents",
    "escritorio": "Desktop",
    "imágenes": "Pictures",
    "imagenes": "Pictures",
    "mis imágenes": "Pictures",
    "música": "Music",
    "vídeos": "Videos",
    "videos": "Videos"
}

def open_user_folder(folder_query):
    """
    Abre una de las carpetas estándar del usuario, o la carpeta del proyecto.
    """
    clean_query = folder_query.lower().strip()
    
    # Custom project rule
    if "proyecto" in clean_query or "actual" in clean_query or "jarvis" in clean_query:
        try:
            os.startfile(os.getcwd())
            return "Abriendo la carpeta raíz del proyecto Jarvis, señor."
        except Exception as e:
            logger.error(f"Error abriendo directorio pwd: {e}")
            return "No he podido abrir la carpeta del proyecto."

    # Parse aliases
    target_dir_name = KNOWN_FOLDERS.get(clean_query, None)
    
    # If not in KNOWN_FOLDERS, assume they tried specifying a valid native directory name
    if not target_dir_name:
        target_dir_name = clean_query.capitalize()

    user_profile = os.environ.get('USERPROFILE', '')
    target_path = Path(user_profile) / target_dir_name
    
    if target_path.exists() and target_path.is_dir():
        try:
            os.startfile(target_path)
            return f"Abriendo la carpeta de {folder_query}, señor."
        except Exception as e:
            logger.error(f"Error abriendo {target_path}: {e}")
            return f"He encontrado la carpeta de {folder_query}, pero hubo un error al abrirla."
            
    return f"Lo siento señor, no pude localizar la carpeta {folder_query} en su perfil de usuario."


def find_and_report_file(filename_query):
    """
    Usa FileSearchService para buscar y decir DÓNDE está el archivo. Omitir apertura.
    """
    searcher = FileSearchService()
    found_path = searcher.search_local_file(filename_query)
    
    if found_path:
        # Extraer carpeta contenedora de forma bonita
        parent_folder = found_path.parent.name
        return f"Encontré un archivo que coincide. Está localizado en la carpeta {parent_folder}."
    else:
        return f"No he logrado localizar el archivo {filename_query} en los directorios habituales."


def find_and_open_file(filename_query):
    """
    Usa FileSearchService para buscar y ABRIR directamente el archivo encontrado.
    """
    searcher = FileSearchService()
    found_path = searcher.search_local_file(filename_query)
    
    if found_path:
        try:
            os.startfile(found_path)
            # Solo decir nombre sin extensión
            return f"Archivo localizado. Abriendo {found_path.stem}, señor."
        except Exception as e:
            logger.error(f"Error ejecutando os.startfile en {found_path}: {e}")
            return f"He encontrado el archivo, pero el sistema no pudo abrirlo adecuadamente."
    else:
        return f"No he logrado localizar el archivo {filename_query} en los directorios habituales."
