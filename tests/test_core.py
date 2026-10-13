import os
import tempfile
import unittest

from memoria.memoria import Memory
from robot.movimiento import Movimiento
from ai.tools import Tools


class FakeESP32:
    def __init__(self):
        self.comandos = []

    def enviar(self, comando):
        self.comandos.append(comando)
        return True


class CoreTests(unittest.TestCase):
    def test_memoria_persistencia_basica(self):
        with tempfile.TemporaryDirectory() as carpeta:
            db = os.path.join(carpeta, "tekni.db")
            memoria = Memory(db)
            memoria.guardar_memoria("color", "azul")
            self.assertEqual(memoria.obtener_memorias("color"), ["azul"])
            memoria.guardar_preferencia("idioma", "es")
            self.assertEqual(memoria.obtener_preferencia("idioma"), "es")
            memoria.cerrar()

    def test_movimiento_usa_duracion_limitada(self):
        esp32 = FakeESP32()
        movimiento = Movimiento(esp32)
        self.assertTrue(movimiento.adelante(30, 500))
        self.assertEqual(esp32.comandos[-1], "MOVE FORWARD 30 500")
        self.assertTrue(movimiento.parar())
        self.assertEqual(esp32.comandos[-1], "STOP")

    def test_tools_rechaza_velocidad_fuera_de_rango(self):
        esp32 = FakeESP32()
        herramientas = Tools(Movimiento(esp32))
        resultado = herramientas.ejecutar("mover_adelante", {"velocidad": 99})
        self.assertFalse(resultado["success"])
        self.assertEqual(esp32.comandos, [])


if __name__ == "__main__":
    unittest.main()
