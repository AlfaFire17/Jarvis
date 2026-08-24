# 🤖 A.L.F.A. - Asistente Virtual Multimodal (Microfase 11.1)

A.L.F.A. es un asistente personal de vanguardia diseñado específicamente para la productividad, la automatización y el gaming de **Pablo Soriano**. Combina inteligencia artificial local, visión de pantalla y automatización avanzada de Windows en una interfaz elegante, futurista y minimalista presidida por el símbolo griego **α** en rojo brillante.

## 🚀 Capacidades Destacadas

- **🔴 Identidad Visual y Verbal (A.L.F.A.)**:
  - Nombre oficial: **A.L.F.A.** (pronunciado *"Alfa"*).
  - Wake word principal: **"Alfa"** (español).
  - Creador real: **Pablo Soriano** (con asistencia de Perplexity).
  - HUD Flotante: Letra griega **α** en rojo carmesí brillante con efectos de resplandor dinámicos y micro-animaciones.

- **🧠 Cerebro Híbrido (Ollama + Gemini)**:
  - IA Local como núcleo principal usando modelos como `Llama3 (8B)` y `Phi3`.
  - Funcionamiento 100% privado y sin cuotas por uso.
  - Fallback inteligente a la nube (Gemini) en caso de fallos locales.
  
- **🎮 Perfiles de Rendimiento (Gaming Ready)**:
  - **Modo Gaming / Ahorro**: Descarga automática del modelo de la VRAM para priorizar el rendimiento en juegos.
  - **Modo Equilibrado**: Balance entre velocidad y consumo (timeout de 5 min).
  - **Modo Rápido**: Respuestas instantáneas con el modelo siempre cargado en VRAM.

- **👁️ Visión de Pantalla (Screen Vision)**:
  - Análisis en tiempo real de lo que ves en el monitor.
  - Explicación de errores de código, resumen de ventanas y lectura de texto (OCR contextual).
  - Soporte para preguntas de seguimiento sobre el contexto visual.

- **🎙️ Voz y Sonido Premium**:
  - Voz masculina, grave y profesional asistida por **ElevenLabs** y **Edge-TTS**.
  - Reconocimiento de voz local continuo ("Alfa").
  - Modo conversación fluido sin necesidad de repetir la palabra de activación.

- **🛠️ Automatización del Sistema**:
  - Control total de **Spotify**, **Steam**, **YouTube** y aplicaciones de Windows.
  - Gestión de archivos, carpetas y búsqueda inteligente.
  - Sistema de recordatorios, alarmas y temporizadores con persistencia.
  - Memoria a largo plazo sobre el usuario y sus preferencias.
  - Tecla rápida global **F4** para silencio / mute absoluto.

## 📂 Estructura de la Arquitectura

```text
Jarvis/
├── actions/         # Scripts de interacción (Apps, Archivos, Visión, LLM, Memoria)
├── core/            # Núcleo: Configuración, IntentRouter, ALFAGGUIController, Logger
├── data/            # Memoria persistente (jarvis_memory.json) y Agenda (agenda.json)
├── gui/             # Interfaz visual PySide6 (ALFAOverlay con símbolo α rojo)
├── integrations/    # Clientes API (Gemini, Ollama, ElevenLabs)
├── services/        # Lógica de fondo (Memory, ALFAScheduler, Vision, Performance, Hotkey)
├── voice/           # Motor de audio: Listener (Vosk, wake word "alfa") y TTS
├── jarvis.py        # Punto de entrada principal
└── start_alfa.vbs   # Lanzador silencioso manual en segundo plano
```

## 🛠️ Requisitos Técnicos

- **Sistema Operativo**: Windows 10 / 11.
- **Hardware Recomendado**: GPU NVIDIA (RTX 3070+ para Llama3), 16GB+ RAM.
- **Dependencias**:
  - Python 3.11+
  - [Ollama](https://ollama.com/) (para IA Local).
  - PySide6, mss, pywin32, edge-tts, elevenlabs, vosk, sounddevice, pygame, winotify.

## 🖱️ Comandos de Ejemplo

- *"Alfa, ¿qué hora es?"*
- *"Alfa, ¿quién te creó?"*
- *"Alfa, activa el modo gaming"*
- *"Alfa, pon la lista de reproducción de Rock en Spotify"*
- *"Alfa, recuérdame sacar la basura en 10 minutos"*
- *"Alfa, ¿qué ves en mi pantalla?"*

---
*Desarrollado con ❤️ por **Pablo Soriano**, con la asistencia de Perplexity.*
