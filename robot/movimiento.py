class Movimiento:
    """Cada orden de movimiento tiene duración limitada en la propia ESP32."""

    def __init__(self, esp32, duracion_ms=500):
        self.esp32 = esp32
        self.duracion_ms = max(100, min(int(duracion_ms), 1000))

    def _mover(self, direccion, velocidad=30, duracion_ms=None):
        if isinstance(velocidad, bool) or not isinstance(velocidad, int) or not 0 <= velocidad <= 50:
            raise ValueError("La velocidad debe ser un entero entre 0 y 50.")
        duracion = self.duracion_ms if duracion_ms is None else max(100, min(int(duracion_ms), 1000))
        return self.esp32.enviar("{} {} {}".format(direccion, velocidad, duracion))

    def adelante(self, velocidad=30, duracion_ms=None):
        return self._mover("MOVE FORWARD", velocidad, duracion_ms)

    def atras(self, velocidad=30, duracion_ms=None):
        return self._mover("MOVE BACKWARD", velocidad, duracion_ms)

    def izquierda(self, velocidad=30, duracion_ms=None):
        return self._mover("TURN LEFT", velocidad, duracion_ms)

    def derecha(self, velocidad=30, duracion_ms=None):
        return self._mover("TURN RIGHT", velocidad, duracion_ms)

    def parar(self):
        return self.esp32.enviar("STOP")
