import ollama

class Vision:
    def __init__(self):
        self.ruta_imagen = "foto-capturada.jpg"
        self.modelo = 'gemma4:e4b'

    def describir(self):
        try:
            respuesta = ollama.chat(
            model=self.modelo,
            messages= [{
                'role' : 'user',
                'content' : '¿Que puedes ver en la imagen? Analiza y describi detalladamente.',
                'images' : [self.ruta_imagen]
            }])
            respuesta_modelo = respuesta['message']['content']
            return respuesta_modelo
        except Exception as e:
            print(f"Ocurrio un error: {e}")
            return None