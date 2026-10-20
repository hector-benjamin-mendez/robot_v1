class ESP32Simulada:
    """Reemplazo de ESP32 para pruebas sin hardware: acepta los mismos comandos y los muestra."""

    PERMITIDOS = ("MOVE FORWARD ", "MOVE BACKWARD ", "TURN LEFT ", "TURN RIGHT ")

    def __init__(self):
        self.serial = None
        self.comandos = []

    def conectar(self):
        print("ESP32 SIMULADA activa: los comandos se muestran en consola, no se mueve nada.")
        return True

    def enviar(self, comando):
        if comando in ("STOP", "HEARTBEAT") or comando.startswith(self.PERMITIDOS):
            if comando != "HEARTBEAT":
                print("[ESP32 simulada] {}".format(comando))
                self.comandos.append(comando)
            return True
        print("[ESP32 simulada] comando no permitido: {}".format(comando))
        return False

    def heartbeat(self):
        return self.enviar("HEARTBEAT")

    def cerrar(self):
        pass
