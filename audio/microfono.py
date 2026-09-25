from openwakeword.model import Model
import sounddevice as sd
import numpy as np
from audio.vad import DetectorVoz

class Microfono:
    def __init__(self,cola_audio):
        self.TASA_FRECUENCIA = 16000
        self.TAMAÑO_CHUNK = 480
        self.modelo_wake_word = Model(wakeword_models=["alexa"], inference_framework="onnx")
        self.detector_voz = DetectorVoz()
        self.esta_escuchando = False
        self.hablando = False
        self.buffer_audio = []
        self.contador_silencio = 0
        self.LIMITE_SILENCIO = 40
        self.cola_audio = cola_audio

    def grabar_audio(self, indata, frames, tiempo, estado):
        # Clonamos y aplanamos el array de audio recibido
        audio_frame = indata.copy().flatten()        
        if not self.esta_escuchando:
            # El robot está en modo de espera, buscando su nombre ("alexa")
            self.modelo_wake_word.predict(audio_frame)

            for wakeword, score in self.modelo_wake_word.prediction_buffer.items():
                if score[-1] > 0.5: # Umbral de confianza
                    print(f"✨ ¡Nombre detectado! ({wakeword}). Escuchando orden...")
                    self.esta_escuchando = True
                    self.buffer_audio = [audio_frame]
                    self.contador_silencio = 0
        else:
            hay_voz = self.detector_voz.hay_voz(audio_frame)
            if hay_voz:
            # La persona está hablando
                self.hablando = True
                self.contador_silencio = 0
                self.buffer_audio.append(audio_frame)

            elif self.hablando:
                # Había voz antes, pero ahora apareció silencio
                self.buffer_audio.append(audio_frame)
                self.contador_silencio += 1
                if self.contador_silencio >= self.LIMITE_SILENCIO:
                    # Terminó de hablar
                    self.esta_escuchando = False
                    self.hablando = False
                    self.contador_silencio = 0
                    audio_completo = np.concatenate(
                        self.buffer_audio,
                        axis=0
                    )
                    self.cola_audio.put(audio_completo)
                    print("🎤 Audio enviado al cerebro.")
                    self.buffer_audio = []
            else:
            # Estamos escuchando pero todavía no empezó a hablar
                pass
    def iniciar_escucha(self):
        print(" Oído del robot activo. Escuchando...")
        with sd.InputStream(
            samplerate=self.TASA_FRECUENCIA, 
            channels=1, 
            callback=self.grabar_audio, # Pasamos nuestro método como callback
            blocksize=self.TAMAÑO_CHUNK, 
            dtype='float32'
        ):
            while True:
                sd.sleep(1000) # Mantiene el flujo abierto sin consumir CPU