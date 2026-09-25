# Tekni - Robot inteligente autónomo
## Un robot controlado por Ollama Qwen3 4B dentro de una Jetson Orin NX, utilizando funciones para utilizar los motores,camara y sus herramientas.

### ¿Como funciona?
* Utilizamos un archivo llamado ``` robot.md ``` que funciona como system prompt, con personalidad, funciones y instrucciones para Tekni


### Hardware
Utilizamos el siguiente hardware para Tekni
* Jetson Nano Orin NX (16GB RAM).
* Microcontrolador ESP32
* Camara IMX219
* Micrófono(sin tener modelo aún)
* Parlante(sin tener modelo aún)
* Motores
* Pantalla LCD de 5"


### Arquitectura
Realizamos la siguiente arquitectura de carpetas
| Carpeta | Descripción |
| :--- | :---: |
| ```/ai``` | Todo el flujo del LLM junto a sus herramientas. | 
| ```/audio``` | Todo lo que involucra audio (STT, Micrófono, VAD, TTS). |
| ```/memoria``` | Memoria de Tekni. | 
| ```/pantalla``` | Funcionamiento de la pantalla. | 
| ```/nucleo``` | El corazón de Tekni, estan los estados posibles, el orquestador, manejo de posibles excepciones. | 
| ```/robot``` | Funcionamiento del ESP32 y motores. | 
| ```/vision``` | Funcionamiento de la camara y la visión inteligente de Tekni. |

### Inicialización
Hay que hacer la siguiente serie de pasos para poder iniciar.

1. Actualizamos sistema ```sudo apt update```
2. Instalamos python ```sudo apt install -y python3 python3-pip```
3. Instalamos dependencias ```pip3 install requirements.txt```
4. Instalamos ffmpeg ```sudo apt install ffmpeg```

 