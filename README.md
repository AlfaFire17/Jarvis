# 🤖 JARVIS - Asistente Virtual Multimodal (Fase 11)

JARVIS es un asistente personal de vanguardia inspirado en el universo de Iron Man, diseñado específicamente para la productividad y el gaming de **Pablo Soriano**. Combina inteligencia artificial local, visión de pantalla y automatización avanzada de Windows en una interfaz elegante y minimalista.

## 🚀 Capacidades Destacadas

- **🧠 Cerebro Híbrido (Ollama + Gemini)**:
  - IA Local como núcleo principal usando modelos como `Llama3 (8B)` y `Phi3`.
  - Funcionamiento 100% privado y sin cuotas por uso.
  - Fallback inteligente a la nube (Gemini) en caso de fallos locales.
  
- **🎮 Perfiles de Rendimiento (Gaming Ready)**:
  - **Modo Gaming**: Descarga automática del modelo de la VRAM para priorizar el rendimiento en juegos.
  - **Modo Equilibrado**: Balance entre velocidad y consumo.
  - **Modo Rápido**: Respuestas instantáneas con el modelo siempre en memoria.

- **👁️ Visión de Pantalla (Screen Vision)**:
  - Análisis en tiempo real de lo que ves en el monitor.
  - Explicación de errores de código, resumen de ventanas y lectura de texto (OCR contextual).
  - Soporte para preguntas de seguimiento sobre el contexto visual.

- **🎙️ Voz y Sonido Premium**:
  - Voz masculina, grave y profesional asistida por **ElevenLabs** y **Edge-TTS**.
  - Reconocimiento de voz local continuo ("Jarvis").
  - Modo conversación fluido sin necesidad de repetir la palabra de activación.

- **🛠️ Automatización del Sistema**:
  - Control total de **Spotify**, **Steam**, **YouTube** y aplicaciones de Windows.
  - Gestión de archivos, carpetas y búsqueda inteligente.
  - Sistema de recordatorios, alarmas y temporizadores con persistencia.
  - Memoria a largo plazo sobre el usuario y sus preferencias.

- **🖥️ Interfaz HUD Iron Man**:
  - Overlay flotante con indicadores de estado, backend de IA y modo de rendimiento.
  - Efectos visuales dinámicos (Glow naranja, cian, verde esmeralda).

## 📂 Estructura de la Arquitectura

```text
Jarvis/
├── actions/         # Scripts de interacción (Apps, Archivos, Visión, LLM)
├── core/            # Núcleo: Configuración, Router de Intenciones, GUI Controller
├── data/            # Memoria persistente y Agenda (JSON)
├── gui/             # Interfaz visual PySide6 (Overlay animado)
├── integrations/    # Clientes API (Gemini, Ollama, ElevenLabs)
├── services/        # Lógica de fondo (Memoria, Scheduler, Visión, Performance)
├── voice/           # Motor de audio: Listener (Vosk) y TTS
└── jarvis.py        # Punto de entrada principal
```

## 🛠️ Requisitos Técnicos

- **Hardware Recomendado**: GPU NVIDIA (RTX 3070+ para Llama3), 16GB+ RAM.
- **Dependencias**:
  - Python 3.11+
  - [Ollama](https://ollama.com/) (para IA Local).
  - PySide6, mss, pywin32, edge-tts, elevenlabs, vosk, pygame.

## 🖱️ Comandos de Ejemplo

- *"Jarvis, ¿qué ves en mi pantalla?"*
- *"Activa el modo gaming"*
- *"Pon la lista de reproducción de Rock en Spotify"*
- *"Recuérdame sacar la basura en 10 minutos"*
- *"Busca el archivo de balance anual"*

---
*Desarrollado con ❤️ por **Pablo Soriano**, con la asistencia de Perplexity y la estética de las Industrias Stark.*
