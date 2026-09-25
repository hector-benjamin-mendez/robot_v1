class Movimiento:
    def __init__(self, esp32):
        self.esp32 = esp32

    def adelante(self, velocidad=50):
        comando = f"MOVE FORWARD {velocidad}"
        return self.esp32.enviar(comando)

    def atras(self, velocidad=50):
        comando = f"MOVE BACKWARD {velocidad}"
        return self.esp32.enviar(comando)

    def izquierda(self, velocidad=50):
        comando = f"TURN LEFT {velocidad}"
        return self.esp32.enviar(comando)

    def derecha(self, velocidad=50):
        comando = f"TURN RIGHT {velocidad}"
        return self.esp32.enviar(comando)

    def parar(self):
        return self.esp32.enviar("STOP")