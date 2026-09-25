import serial
import time

class ESP32:
    def __init__(self, puerto="/dev/ttyUSB0", baudrate=115200):
        self.puerto = puerto
        self.baudrate = baudrate
        self.serial = None

    def conectar(self):
        try:
            self.serial = serial.Serial(
                self.puerto,
                self.baudrate,
                timeout=1
            )
            time.sleep(2)
            print("🟢 ESP32 conectada")

        except Exception as e:
            print(f"No se pudo conectar con ESP32: {e}")
            self.serial = None

    def enviar(self, comando):
        if self.serial is None:
            print("⚠️ ESP32 no conectada")
            return False
        try:
            mensaje = comando + "\n"
            self.serial.write(
                mensaje.encode("utf-8")
            )
            return True

        except Exception as e:
            print(f"Error enviando a ESP32: {e}")
            return False

    def cerrar(self):
        if self.serial:
            self.serial.close()
            self.serial = None