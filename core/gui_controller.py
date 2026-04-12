from PySide6.QtCore import QObject, Signal

class JARVISGUIController(QObject):
    """
    Controlador para comunicar el hilo de fondo (voz/lógica) con el hilo principal (GUI)
    usando el sistema de señales de PySide6, lo cual es seguro en entornos multihilo.
    """
    # Señales para los estados:
    set_idle = Signal()
    set_wake = Signal()
    set_listening = Signal()
    set_transcription = Signal(str)
    set_responding = Signal(str)
    
    # Señales Fase 9 (Conversación y Mute)
    set_muted = Signal()
    set_conversation_mode = Signal()
