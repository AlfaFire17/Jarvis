import os
from pathlib import Path
from core.logger import logger

class FileSearchService:
    def __init__(self):
        # Directorios comunes de búsqueda para no congelar el PC
        user_profile = os.environ.get('USERPROFILE', '')
        self.search_directories = [
            Path(user_profile) / "Desktop",
            Path(user_profile) / "Documents",
            Path(user_profile) / "Downloads",
            Path(os.getcwd())  # Carpeta de Jarvis
        ]

    def search_local_file(self, filename) -> Path:
        """
        Busca un archivo por nombre en los directorios comunes del usuario.
        Retorna un objeto Path si lo encuentra, None si no.
        """
        logger.info(f"Iniciando búsqueda de archivo: {filename}")
        clean_filename = filename.lower().strip()
        
        # Estrategia rápida: iterar por carpetas clave usando rglob (recursivo)
        # Limitado por defecto a lo que encuentre primero para ganar velocidad.
        for directory in self.search_directories:
            if not directory.exists() or not directory.is_dir():
                continue
                
            logger.info(f"Buscando en: {directory}")
            try:
                # Buscar coincidencias parciales con rglob
                for path in directory.rglob(f"*{clean_filename}*"):
                    if path.is_file():
                        logger.info(f"Archivo encontrado: {path}")
                        return path
            except PermissionError:
                # Si una subcarpeta requiere admin de repente, la saltamos
                continue
            except Exception as e:
                logger.error(f"Error buscando en {directory}: {e}")

        logger.warning(f"Archivo '{filename}' no encontrado en las rutas estándar.")
        return None
