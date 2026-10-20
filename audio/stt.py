import queue
import numpy as np
import sounddevice as sd

class Microfono:
    def __init__(self, cola_audio):
        self.tasa_frecuencia = 16000
        self.tamano_chunk = 480  # 30 ms a 16 kHz
        self.cola_audio = cola_audio
        self.esta_escuchando = False
        self.buffer_audio = []
        self.stream = None  # Guardamos el stream para poder controlarlo

    def iniciar_grabacion(self):
        """Llamar a este método cuando se presione el pulsador."""
        if not self.esta_escuchando:
            print("Pulsador presionado. Grabando...")
            self.buffer_audio = []
            self.esta_escuchando = True

    def detener_grabacion(self):
        """Llamar a este método cuando se suelte el pulsador."""
        if self.esta_escuchando:
            print("Pulsador soltado. Procesando audio...")
            self.esta_escuchando = False  
            audio_completo = np.concatenate(self.buffer_audio).astype(np.float32) if self.buffer_audio else None
            self.buffer_audio = []
            
            if audio_completo is not None and audio_completo.size >= self.tasa_frecuencia // 4:
                try:
                    self.cola_audio.put_nowait(audio_completo)
                    print("Audio enviado a Whisper.")
                except queue.Full:
                    print("Cola de audio llena; se descarta esta captura.")
            else:
                print("Grabación demasiado corta o vacía.")

    def grabar_audio(self, indata, frames, tiempo, estado):
        """Callback continuo de sounddevice."""
        if estado:
            print(f"Aviso de audio: {estado}")
            
        if self.esta_escuchando:
            audio = indata.copy().reshape(-1).astype(np.float32)
            self.buffer_audio.append(audio)

    def iniciar_escucha(self):
        """Inicia el stream de audio de fondo listo para capturar."""
        print("Micrófono en espera del pulsador...")
        self.stream = sd.InputStream(
            samplerate=self.tasa_frecuencia, 
            channels=1, 
            callback=self.grabar_audio, 
            blocksize=self.tamano_chunk, 
            dtype="float32"
        )
        self.stream.start()

    def detener_escucha(self):
        """Cierra el stream de audio por completo."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
