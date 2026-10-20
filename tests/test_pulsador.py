import os
import queue
import sys
import types
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np

from nucleo.estado import Estado
from nucleo.orquestador import Orquestador
from nucleo.pulsador import ControladorPulsador


class MicrofonoFalso:
    def __init__(self, devuelve=True, con_stream=True):
        self.stream = object() if con_stream else None
        self.esta_escuchando = False
        self.devuelve = devuelve

    def iniciar_grabacion(self):
        self.esta_escuchando = True

    def detener_grabacion(self):
        self.esta_escuchando = False
        return self.devuelve


class OrquestadorFalso:
    def __init__(self):
        self.estado = Estado.NORMAL

    def cambiar_estado(self, nuevo):
        self.estado = nuevo

    def indicar_escucha(self):
        self.cambiar_estado(Estado.ESCUCHANDO)


class PulsadorTests(unittest.TestCase):
    def test_presionar_y_soltar_con_audio_pasa_a_pensando(self):
        orq, mic = OrquestadorFalso(), MicrofonoFalso(devuelve=True)
        p = ControladorPulsador(orq, mic)
        p.presionado()
        self.assertEqual(orq.estado, Estado.ESCUCHANDO)
        self.assertTrue(mic.esta_escuchando)
        p.soltado()
        self.assertEqual(orq.estado, Estado.PENSANDO)

    def test_audio_descartado_vuelve_a_reposo(self):
        orq, mic = OrquestadorFalso(), MicrofonoFalso(devuelve=False)
        p = ControladorPulsador(orq, mic)
        p.presionado()
        p.soltado()
        self.assertEqual(orq.estado, Estado.NORMAL)

    def test_ignora_pulsacion_si_esta_ocupado(self):
        orq, mic = OrquestadorFalso(), MicrofonoFalso()
        orq.estado = Estado.HABLANDO
        ControladorPulsador(orq, mic).presionado()
        self.assertFalse(mic.esta_escuchando)
        self.assertEqual(orq.estado, Estado.HABLANDO)

    def test_ignora_pulsacion_sin_microfono(self):
        orq, mic = OrquestadorFalso(), MicrofonoFalso(con_stream=False)
        ControladorPulsador(orq, mic).presionado()
        self.assertEqual(orq.estado, Estado.NORMAL)

    def test_soltar_sin_haber_presionado_no_hace_nada(self):
        orq, mic = OrquestadorFalso(), MicrofonoFalso()
        ControladorPulsador(orq, mic).soltado()
        self.assertEqual(orq.estado, Estado.NORMAL)


class PantallaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        from pantalla.pantalla import Display
        cls.pygame = pygame
        cls.display = Display(ventana=True, debug=True)

    @classmethod
    def tearDownClass(cls):
        cls.pygame.quit()

    def test_espacio_llama_a_los_callbacks(self):
        pg = self.pygame
        eventos = []
        self.display.conectar_pulsador(lambda: eventos.append("down"), lambda: eventos.append("up"))
        pg.event.clear()
        pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_SPACE))
        pg.event.post(pg.event.Event(pg.KEYUP, key=pg.K_SPACE))
        self.assertTrue(self.display.procesar_eventos())
        self.assertEqual(eventos, ["down", "up"])

    def test_escape_cierra(self):
        pg = self.pygame
        pg.event.clear()
        pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))
        self.assertFalse(self.display.procesar_eventos())

    def test_estado_cambia_la_cara_y_dibuja(self):
        self.display.actualizar_segun_estado(Estado.ERROR)
        self.display.actualizar()
        self.assertEqual(self.display.animacion_actual, "llorando")
        self.display.actualizar_segun_estado(Estado.NORMAL)
        self.display.actualizar()
        self.assertEqual(self.display.animacion_actual, "normal")
        self.display.dibujar()  # no debe fallar con el texto de depuración


class LLMFalso:
    def __init__(self, respuestas):
        self.respuestas = list(respuestas)

    def preguntar(self, historial, tools=None):
        return {"message": self.respuestas.pop(0)}


class HerramientasFalsas:
    def __init__(self):
        self.llamadas = []

    def ejecutar(self, nombre, argumentos):
        self.llamadas.append((nombre, argumentos))
        return {"success": True, "resultado": True}


class TTSFalso:
    def __init__(self):
        self.dicho = []

    def hablar(self, texto):
        self.dicho.append(texto)


class OrquestadorTests(unittest.TestCase):
    def test_herramienta_y_respuesta_final(self):
        tool_call = {"id": "c1", "type": "function", "function": {"name": "detener", "arguments": "{}"}}
        llm = LLMFalso([
            {"role": "assistant", "content": "", "tool_calls": [tool_call]},
            {"role": "assistant", "content": "Listo, frené."},
        ])
        herramientas, tts = HerramientasFalsas(), TTSFalso()
        orq = Orquestador(llm, herramientas, tts=tts)
        orq.procesar_texto("pará")
        self.assertEqual(herramientas.llamadas, [("detener", {})])
        self.assertEqual(tts.dicho, ["Listo, frené."])
        self.assertEqual(orq.estado, Estado.NORMAL)

    def test_texto_vacio_vuelve_a_reposo(self):
        orq = Orquestador(LLMFalso([]), HerramientasFalsas())
        orq.estado = Estado.PENSANDO
        orq.procesar_texto("")
        self.assertEqual(orq.estado, Estado.NORMAL)


class LLMTests(unittest.TestCase):
    def test_preguntar_devuelve_diccionario(self):
        from openai.types.chat import ChatCompletionMessage
        from ai.llm import LLM
        mensaje = ChatCompletionMessage.model_validate({
            "role": "assistant", "content": None,
            "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "detener", "arguments": "{}"}}],
        })
        respuesta = types.SimpleNamespace(choices=[types.SimpleNamespace(message=mensaje)])
        llm = LLM(api_key="x")
        llm.cliente = mock.Mock()
        llm.cliente.chat.completions.create.return_value = respuesta
        resultado = llm.preguntar([{"role": "user", "content": "hola"}], tools=[{"type": "function"}])
        mensaje_dict = resultado["message"]
        self.assertIsInstance(mensaje_dict, dict)
        self.assertEqual(mensaje_dict["tool_calls"][0]["function"]["name"], "detener")
        enviado = llm.cliente.chat.completions.create.call_args.kwargs
        self.assertEqual(enviado["extra_body"], {"thinking": {"type": "disabled"}})


class AudioTests(unittest.TestCase):
    def test_microfono_devuelve_si_encolo(self):
        sys.modules.setdefault("sounddevice", types.ModuleType("sounddevice"))
        from audio.microfono import Microfono
        cola = queue.Queue(maxsize=1)
        mic = Microfono(cola)
        mic.iniciar_grabacion()
        mic.buffer_audio = [np.zeros(8000, dtype=np.float32)]  # 0,5 s
        self.assertTrue(mic.detener_grabacion())
        mic.iniciar_grabacion()
        mic.buffer_audio = [np.zeros(100, dtype=np.float32)]  # demasiado corto
        self.assertFalse(mic.detener_grabacion())

    def test_stt_avisa_cuando_no_hay_texto(self):
        modulo = types.ModuleType("faster_whisper")
        modulo.WhisperModel = lambda *a, **k: object()
        sys.modules["faster_whisper"] = modulo
        from audio.stt import ProcesadorSTT
        cola = queue.Queue()
        recibidos = []
        stt = ProcesadorSTT(cola, callback_texto=recibidos.append, modelo="tiny")
        stt.transcribir = lambda audio: ""
        cola.put(np.zeros(16000, dtype=np.float32))
        cola.put(None)
        stt.iniciar_procesamiento()
        self.assertEqual(recibidos, [""])


if __name__ == "__main__":
    unittest.main()
