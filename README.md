# 🤖 JARVIS - Asistente Personal de Inteligencia Artificial

Este es un asistente inspirado en JARVIS de Iron Man, diseñado específicamente para **Pablo**. El sistema escucha de forma continua y reacciona a comandos de voz para automatizar la rutina diaria.

## 🚀 Funcionalidades Principales

- **Activación por Voz (Wake Word)**: Responde a la frase *"Jarvis, ¿estás ahí?"* utilizando el motor de reconocimiento **Vosk (Offline)**.
- **Respuesta de Voz Premium**: Integración con **edge-tts** (voz de Álvaro) y soporte para **ElevenLabs** para una experiencia de voz masculina, grave y realista.
- **Automatización de Navegador**: Al activarse, JARVIS abre automáticamente **Opera GX** con pestañas preconfiguradas (Perplexity AI y YouTube).
- **Persistencia y Auto-inicio**: Configurado para iniciarse automáticamente con Windows y funcionar de forma totalmente silenciosa en segundo plano.
- **Privacidad Total**: El reconocimiento de voz se realiza de forma local sin enviar audio a la nube.

## 📂 Estructura del Proyecto

```text
Jarvis/
├── jarvis.py                # Núcleo del asistente (Lógica de voz y automatización)
├── start_jarvis.vbs         # Lanzador silencioso para segundo plano
├── .env                     # Configuración de API Keys y rutas
├── vosk-model-.../          # Modelo de lenguaje para reconocimiento offline
└── OpenJarvis/              # Repositorio base de OpenJarvis
```

## 🛠️ Requisitos e Instalación

1. **Python 3.11+**
2. **Librerías Necesarias**:
   ```bash
   pip install sounddevice numpy edge-tts pygame python-dotenv elevenlabs vosk
   ```
3. **Navegador**: Opera GX (configurable en el archivo `.env`).

## ⚙️ Configuración (.env)

El archivo `.env` debe contener las siguientes variables:
- `OPERA_PATH`: Ruta al ejecutable de Opera GX.
- `ELEVENLABS_API_KEY`: Tu llave de API de ElevenLabs (Opcional, fallback a edge-tts).

## 🖱️ Uso

Una vez instalado, simplemente di:  
> **"Jarvis, ¿estás ahí?"**

JARVIS responderá a tu saludo y preparará tu entorno de trabajo inmediatamente.

---
*Desarrollado para Pablo por Antigravity.*
