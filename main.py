import argparse
import queue
import threading
import time

from config import (
    CAMERA_SOURCE, DB_PATH, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID,
    ESP32_BAUDRATE, ESP32_PORT, DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
    DEEPSEEK_VISION_MODEL, WHISPER_MODEL,
)
from ai.llm import LLM
from ai.tools import Tools
from audio.microfono import Microfono
from audio.stt import ProcesadorSTT
from audio.tts import TTS
from memoria.memoria import Memory
from nucleo.orquestador import Orquestador
from nucleo.pulsador import ControladorPulsador
from pantalla.pantalla import Display
from robot.esp32 import ESP32
from robot.esp32_simulada import ESP32Simulada
from robot.movimiento import Movimiento
from vision.camara import Camara
from vision.vision import Vision


def leer_argumentos():
    parser = argparse.ArgumentParser(description="Tekni")
    parser.add_argument("--prueba", action="store_true",
                        help="ESP32 simulada y texto de estado en pantalla (sin mover motores).")
    parser.add_argument("--ventana", action="store_true",
                        help="Abre la pantalla en una ventana en vez de pantalla completa.")
    return parser.parse_args()


def hilo_heartbeat(esp32, intervalo=0.5):
    while True:
        if not esp32.heartbeat():
            print("Aviso: heartbeat sin confirmación; la ESP32 debe detener los motores por watchdog.")
        time.sleep(intervalo)


def hilo_stt(cola_audio, cola_texto, modelo):
    # El modelo se carga acá para no congelar la ventana mientras arranca.
    stt = ProcesadorSTT(cola_audio, callback_texto=cola_texto.put, modelo=modelo)
    stt.iniciar_procesamiento()


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
    args = leer_argumentos()
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("Configurá DEEPSEEK_API_KEY para iniciar Tekni.")

    cola_audio = queue.Queue(maxsize=8)
    cola_texto = queue.Queue()

    if args.prueba:
        esp32 = ESP32Simulada()
    else:
        esp32 = ESP32(ESP32_PORT, ESP32_BAUDRATE)
    if not esp32.conectar():
        print("Se inicia en modo limitado: el movimiento no estará disponible.")
    movimiento = Movimiento(esp32)
    memoria = Memory(DB_PATH)

    camara = None
    vision = None
    try:
        camara = Camara(CAMERA_SOURCE)
        vision = Vision(camara, modelo=DEEPSEEK_VISION_MODEL)
        print("Cámara lista para visión multimodal.")
    except Exception as exc:
        print("Visión desactivada: {}".format(exc))

    pantalla = None
    try:
        pantalla = Display(ventana=args.ventana, debug=args.prueba)
    except Exception as exc:
        print("Pantalla desactivada: {}".format(exc))

    llm = LLM(modelo=DEEPSEEK_MODEL)
    tts = TTS(api_key=ELEVENLABS_API_KEY, voice_id=ELEVENLABS_VOICE_ID)
    herramientas = Tools(movement=movimiento, memory=memoria, vision=vision)
    orquestador = Orquestador(llm, herramientas, tts=tts, memoria=memoria, pantalla=pantalla)

    microfono = Microfono(cola_audio)
    try:
        microfono.iniciar_escucha()
    except Exception as exc:
        print("Micrófono desactivado: {}".format(exc))
    pulsador = ControladorPulsador(orquestador, microfono)
    if pantalla is not None:
        pantalla.conectar_pulsador(pulsador.presionado, pulsador.soltado)
    else:
        print("Sin pantalla no hay pulsador por teclado: no se puede iniciar una interacción.")

    threading.Thread(target=hilo_heartbeat, args=(esp32,), name="esp32-heartbeat", daemon=True).start()
    threading.Thread(target=hilo_stt, args=(cola_audio, cola_texto, WHISPER_MODEL), name="whisper-stt", daemon=True).start()
    threading.Thread(target=hilo_procesar_ordenes, args=(cola_texto, orquestador), name="orquestador", daemon=True).start()

    print("Resumen: ESP32={} | cámara={} | pantalla={} | micrófono={} | voz={}".format(
        "simulada" if args.prueba else "real",
        "ok" if vision else "no",
        "ok" if pantalla else "no",
        "ok" if microfono.stream else "no",
        "ok" if (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID) else "solo texto",
    ))
    print("Tekni iniciado. Mantené presionada la barra ESPACIADORA para hablar y soltala al terminar.")
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
        microfono.detener_escucha()
        memoria.cerrar()
        esp32.cerrar()


if __name__ == "__main__":
    main()
