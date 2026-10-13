# Tekni — arquitectura Jetson Nano + ESP32

## Arquitectura elegida

- **Activación:** `openWakeWord` local (palabra por defecto: `alexa`).
- **STT:** `faster-whisper` local con modelo `tiny`, CPU e int8; se puede cambiar con `WHISPER_MODEL`.
- **Razonamiento y herramientas:** API de OpenAI por HTTPS.
- **Visión:** cámara local + análisis multimodal mediante API de OpenAI.
- **Voz:** ElevenLabs por HTTPS; reproducción local del PCM.
- **Memoria:** SQLite local (`data/tekni.db`).
- **Movimiento:** ESP32 por USB serial; cada orden tiene duración máxima de 1 segundo y la ESP32 mantiene un watchdog local de 2 segundos.
- **Pantalla:** Pygame en el hilo principal.

La IA en la nube necesita Internet. La activación, transcripción, memoria y seguridad básica de motores permanecen en el dispositivo; si se cae Internet, razonamiento, visión y TTS remotos no estarán disponibles.

## Estructura

```text
tekni/
├── main.py
├── config.py
├── .env.example
├── ai/llm.py
├── ai/tools.py
├── ai/prompts.md
├── audio/microfono.py
├── audio/stt.py
├── audio/tts.py
├── audio/vad.py
├── memoria/
├── nucleo/
├── pantalla/pantalla.py
├── robot/esp32.py
├── robot/movimiento.py
├── robot/seguridad.py
├── robot/esp32.txt
├── vision/
└── data/                 # se crea automáticamente
```

## Configuración

1. Copiá `.env.example` a `.env` y completá las claves. No subas `.env` a Git.
2. Exportá las variables en la terminal antes de ejecutar:
   ```bash
   set -a
   source .env
   set +a
   ```
3. Instalá dependencias compatibles con el sistema de la Jetson. OpenCV conviene instalarlo desde JetPack/apt para conservar soporte de cámara CSI/GStreamer.
4. Cargá `robot/esp32.txt` en Arduino IDE y flashealo a la ESP32.
5. Verificá `ESP32_PORT`, `CAMERA_SOURCE`, micrófono y parlante.
6. Ejecutá desde la raíz del proyecto: `python3 main.py`.

## Advertencia importante sobre la Jetson Nano original

No confundir **Jetson Nano 4 GB** con **Jetson Orin Nano 4 GB**: son plataformas distintas. NVIDIA marca JetPack 4.6.6 como la versión final para la Jetson Nano original, basada en Ubuntu 18.04. El Python del sistema puede ser demasiado antiguo para algunas versiones actuales de `faster-whisper` y `openwakeword`; verificá `python3 --version` y `cat /etc/nv_tegra_release` antes de instalar. Si hace falta compilar otro Python, no reemplaces el Python del sistema ni los paquetes CUDA de JetPack. La combinación exacta de ruedas ARM64 todavía debe validarse en el equipo físico.

## Seguridad y pruebas

- La velocidad solicitada por las herramientas se limita a 0–50 y cada movimiento dura 100–1000 ms; el firmware detiene motores al terminar la orden o al perder heartbeat.
- **Antes de conectar los motores**, verificá el modelo del driver, la compatibilidad PWM de la versión del core ESP32 y el cableado real. Los pines del firmware son los que venían en el prototipo y no deben considerarse validados para cualquier driver.
- Probá primero con las ruedas levantadas, velocidad baja y un botón físico de corte disponible.
- La confirmación serial significa que la ESP32 aceptó la orden, no que el robot completó una trayectoria ni que el entorno esté libre de obstáculos.
- La cámara IMX219 por CSI puede requerir un pipeline GStreamer con `nvarguscamerasrc`; configurá `CAMERA_SOURCE` para ese pipeline si `0` no funciona.
- El proyecto se revisó estáticamente, pero no se probó con la Jetson, la cámara, el micrófono, ElevenLabs ni los motores reales.
