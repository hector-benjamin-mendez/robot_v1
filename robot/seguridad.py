import time

class Seguridad:
    def __init__(self, movimiento):
        self.movimiento = movimiento
        self.ultima_comunicacion = time.time()
        self.timeout = 2.0

    def actualizar(self):
        self.ultima_comunicacion = time.time()

    def verificar(self):
        tiempo = time.time() - self.ultima_comunicacion

        if tiempo > self.timeout:
            self.emergency_stop()

    def emergency_stop(self):
        print("STOP EMERGENCIA")
        self.movimiento.parar()