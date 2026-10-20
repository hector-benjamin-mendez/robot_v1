from nucleo.estado import Estado


class ControladorPulsador:
    """Traduce 'pulsador presionado / soltado' en acciones del robot.

    No le importa de dónde viene el pulsador: la barra espaciadora (pruebas) o un
    pulsador físico (GPIO o ESP32) llaman a los mismos dos métodos.
    """

    def __init__(self, orquestador, microfono):
        self.orquestador = orquestador
        self.microfono = microfono

    def presionado(self):
        if self.orquestador.estado != Estado.NORMAL:
            print("Pulsador ignorado: Tekni está ocupado ({}).".format(self.orquestador.estado.value))
            return
        if getattr(self.microfono, "stream", None) is None:
            print("Pulsador ignorado: el micrófono no está disponible.")
            return
        self.orquestador.indicar_escucha()
        self.microfono.iniciar_grabacion()

    def soltado(self):
        if not self.microfono.esta_escuchando:
            return
        if self.microfono.detener_grabacion():
            # El audio ya está en la cola: Whisper transcribe y luego se consulta al modelo.
            self.orquestador.cambiar_estado(Estado.PENSANDO)
        else:
            self.orquestador.cambiar_estado(Estado.NORMAL)
