import os
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
        self.stream = None  # Guardamos el stream para poder controlarlo de fondo

    def iniciar_grabacion(self):
        """Llamar a este método exactamente cuando se PRESIONE el pulsador."""
        if not self.esta_escuchando:
            print("Pulsador detectado: Grabando audio...")
            self.buffer_audio = []
            self.esta_escuchando = True

    def detener_grabacion(self):
        """Llamar a este método exactamente cuando se SUELTE el pulsador."""
        if self.esta_escuchando:
            print("Pulsador liberado: Deteniendo grabación...")
            self.esta_escuchando = False
            
            # Consolidamos todo el audio acumulado en el buffer
            audio_completo = np.concatenate(self.buffer_audio).astype(np.float32) if self.buffer_audio else None
            self.buffer_audio = []
            
            # Validación: Que dure al menos 250ms (tasa_frecuencia // 4) para descartar clicks accidentales
            if audio_completo is not None and audio_completo.size >= self.tasa_frecuencia // 4:
                try:
                    self.cola_audio.put_nowait(audio_completo)
                    print("Audio enviado a la cola de Whisper.")
                except queue.Full:
                    print("Cola de audio llena; se descarta esta captura.")
            else:
                print("Grabación demasiado corta o vacía; se ignora.")

    def grabar_audio(self, indata, frames, tiempo, estado):
        """Callback continuo de sounddevice. Solo acumula si el pulsador está activo."""
        if estado:
            print(f"Aviso de audio: {estado}")
            
        if self.esta_escuchando:
            audio = indata.copy().reshape(-1).astype(np.float32)
            self.buffer_audio.append(audio)

    def iniciar_escucha(self):
        """Enciende el hardware del micrófono en segundo plano sin bloquear el hilo principal."""
        print("Micrófono inicializado en segundo plano. Esperando interacción con el pulsador...")
        self.stream = sd.InputStream(
            samplerate=self.tasa_frecuencia, 
            channels=1, 
            callback=self.grabar_audio, 
            blocksize=self.tamano_chunk, 
            dtype="float32"
        )
        self.stream.start()

    def detener_escucha(self):
        """Apaga el stream por completo al cerrar la aplicación."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
