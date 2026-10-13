import threading
import time

import serial


class ESP32:
    def __init__(self, puerto="/dev/ttyUSB0", baudrate=115200, timeout=1.2):
        self.puerto = puerto
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.lock = threading.Lock()

    def conectar(self):
        try:
            self.serial = serial.Serial(self.puerto, self.baudrate, timeout=self.timeout, write_timeout=self.timeout)
            time.sleep(2)  # La apertura del puerto suele reiniciar la placa.
            self.serial.reset_input_buffer()
            print(f"ESP32 conectada en {self.puerto}")
            return True
        except Exception as exc:
            print(f"No se pudo conectar con ESP32: {exc}")
            self.serial = None
            return False

    def enviar(self, comando):
        if self.serial is None or not self.serial.is_open:
            print("ESP32 no conectada.")
            return False
        esperadas = {"STOP": "STOP_OK", "HEARTBEAT": "HEARTBEAT_OK"}
        if comando.startswith(("MOVE ", "TURN ")):
            esperada = "MOVE_OK"
        else:
            esperada = esperadas.get(comando)
        if esperada is None:
            print(f"Comando serial no permitido: {comando}")
            return False
        try:
            with self.lock:
                self.serial.write((comando + "\n").encode("utf-8"))
                self.serial.flush()
                limite = time.monotonic() + self.timeout
                while time.monotonic() < limite:
                    linea = self.serial.readline().decode("utf-8", errors="replace").strip()
                    if not linea or linea == "ESP32 LISTA":
                        continue
                    if linea == esperada:
                        return True
                    if linea == "COMANDO_DESCONOCIDO":
                        return False
                print(f"Sin confirmación de ESP32 para {comando}.")
                return False
        except (serial.SerialException, OSError) as exc:
            print(f"Error serial con ESP32: {exc}")
            return False

    def heartbeat(self):
        return self.enviar("HEARTBEAT")

    def cerrar(self):
        if self.serial is not None:
            try:
                self.enviar("STOP")
            finally:
                self.serial.close()
                self.serial = None
