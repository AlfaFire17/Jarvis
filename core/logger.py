import logging
import sys

def setup_logger():
    """Configures the global logger for the project."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("jarvis.log", encoding='utf-8')
        ]
    )
    return logging.getLogger("JARVIS")

# Initialize and export a default logger
logger = setup_logger()
Pelican = logger # For backward compatibility or alternative names if needed
