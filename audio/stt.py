from faster_whisper import WhisperModel

class ProcesadorSTT:
    def __init__(self,cola_audio):
        self.cola_audio = cola_audio
        print("Cargando modelo whisper...")
        self.modelo_whisper = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("Modelo cargado correctamente.")

    def iniciar_procesamiento(self):    
        while True:
            try:
                # .get() bloquea este hilo/proceso sin consumir CPU hasta que llegue audio
                audio_data = self.cola_audio.get()
                print("Audio recibido desde la cola de memoria. Procesando...") 
                # Transcribir con Faster-Whisper (Filtra el ruido de fondo nativamente)
                segments, info = self.modelo_whisper.transcribe(
                    audio_data, 
                    language="es",  # Forzamos español para evitar que confunda ruidos con inglés
                    beam_size=3     # Balance óptimo entre velocidad y precisión
                )
                # Unimos los segmentos de texto detectados
                frase_final = "".join([segment.text for segment in segments]).strip()
                
                if frase_final:
                    print(f"TEXTO TRANSCRITO: '{frase_final}'\n")
                else:
                    print("Whisper procesó el audio pero no detectó palabras claras (posible ruido falso positivo).\n")                    
            except Exception as e:
                print(f"Error en el procesamiento de STT: {e}")
                