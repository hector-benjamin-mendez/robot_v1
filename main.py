import queue
import threading
import time

from config import (
    CAMERA_SOURCE, DB_PATH, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID,
    ESP32_BAUDRATE, ESP32_PORT, OPENAI_API_KEY, OPENAI_MODEL,
    OPENAI_VISION_MODEL, WAKE_WORD, WHISPER_MODEL,
)
from ai.llm import LLM
from ai.tools import Tools
from audio.microfono import Microfono
from audio.stt import ProcesadorSTT
from audio.tts import TTS
from memoria.memoria import Memory
from nucleo.orquestador import Orquestador
from pantalla.pantalla import Display
from robot.esp32 import ESP32
from robot.movimiento import Movimiento
from vision.camara import Camara
from vision.vision import Vision


def hilo_heartbeat(esp32, intervalo=0.5):
    while True:
        if not esp32.heartbeat():
            print("Aviso: heartbeat sin confirmación; la ESP32 debe detener los motores por watchdog.")
        time.sleep(intervalo)


def hilo_procesar_ordenes(cola_texto, orquestador):
    while True:
        texto = cola_texto.get()
        if texto is None:
            return
        try:
            orquestador.procesar_texto(texto)
        except Exception as exc:
            print("Error procesando la orden: {}".format(exc))
            orquestador.error("Tuve un problema procesando esa orden.")


def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("Configurá OPENAI_API_KEY antes de iniciar Tekni.")

    cola_audio = queue.Queue(maxsize=8)
    cola_texto = queue.Queue()
    esp32 = ESP32(ESP32_PORT, ESP32_BAUDRATE)
    if not esp32.conectar():
        print("Se inicia en modo limitado: el movimiento no estará disponible.")
    movimiento = Movimiento(esp32)
    memoria = Memory(DB_PATH)

    camara = None
    vision = None
    try:
        camara = Camara(CAMERA_SOURCE)
        vision = Vision(camara, modelo=OPENAI_VISION_MODEL)
        print("Cámara lista para visión multimodal.")
    except Exception as exc:
        print("Visión desactivada: {}".format(exc))

    pantalla = None
    try:
        pantalla = Display()
    except Exception as exc:
        print("Pantalla desactivada: {}".format(exc))

    llm = LLM(modelo=OPENAI_MODEL)
    tts = TTS(api_key=ELEVENLABS_API_KEY, voice_id=ELEVENLABS_VOICE_ID)
    herramientas = Tools(movement=movimiento, memory=memoria, vision=vision)
    orquestador = Orquestador(llm, herramientas, tts=tts, memoria=memoria, pantalla=pantalla)

    stt = ProcesadorSTT(cola_audio, callback_texto=cola_texto.put, modelo=WHISPER_MODEL)
    microfono = Microfono(cola_audio, wake_word=WAKE_WORD)

    threading.Thread(target=hilo_heartbeat, args=(esp32,), name="esp32-heartbeat", daemon=True).start()
    threading.Thread(target=stt.iniciar_procesamiento, name="whisper-stt", daemon=True).start()
    threading.Thread(target=hilo_procesar_ordenes, args=(cola_texto, orquestador), name="orquestador", daemon=True).start()
    threading.Thread(target=microfono.iniciar_escucha, name="microfono-wakeword", daemon=True).start()

    print("Tekni iniciado. Decí la palabra de activación configurada.")
    try:
        if pantalla is not None:
            pantalla.iniciar()  # Pygame se mantiene en el hilo principal.
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("Cerrando Tekni...")
    finally:
        if esp32.serial is not None:
            esp32.enviar("STOP")
        if camara is not None:
            camara.cerrar()
        memoria.cerrar()
        esp32.cerrar()


if __name__ == "__main__":
    main()
