import os
import queue

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from audio.vad import DetectorVoz


class Microfono:
    def __init__(self, cola_audio, wake_word=None):
        self.tasa_frecuencia = 16000
        self.tamano_chunk = 480  # 30 ms a 16 kHz: compatible con WebRTC VAD.
        self.cola_audio = cola_audio
        #self.wake_word = wake_word or os.getenv("WAKE_WORD", "alexa")
        #self.modelo_wake_word = Model(wakeword_models=[self.wake_word], inference_framework="onnx")
        self.detector_voz = DetectorVoz()
        self.esta_escuchando = False
        self.buffer_audio = []
        self.contador_silencio = 0
        self.limite_silencio = 33  # ~1 segundo de silencio.
        self._wake_buffer = np.empty(0, dtype=np.int16)

    def grabar_audio(self, indata, frames, tiempo, estado):
        if estado:
            print(f"Aviso de audio: {estado}")
        audio = indata.copy().reshape(-1).astype(np.float32)
        if not self.esta_escuchando:
            # openWakeWord espera audio PCM int16; Whisper recibe float32 normalizado.
            audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
            self._wake_buffer = np.concatenate((self._wake_buffer, audio_int16))
            # openWakeWord suele trabajar con bloques de 80 ms (1280 muestras a 16 kHz).
            while self._wake_buffer.size >= 1280:
                bloque = self._wake_buffer[:1280]
                self._wake_buffer = self._wake_buffer[1280:]
                self.modelo_wake_word.predict(bloque)
                predicciones = self.modelo_wake_word.prediction_buffer
                if any(float(scores[-1]) > 0.5 for scores in predicciones.values() if len(scores)):
                    print("Palabra de activación detectada. Te escucho...")
                    self.esta_escuchando = True
                    self.buffer_audio = []
                    self.contador_silencio = 0
                    break
            return

        self.buffer_audio.append(audio)
        if self.detector_voz.hay_voz(audio):
            self.contador_silencio = 0
        else:
            self.contador_silencio += 1
        if self.contador_silencio >= self.limite_silencio:
            self.esta_escuchando = False
            audio_completo = np.concatenate(self.buffer_audio).astype(np.float32) if self.buffer_audio else None
            self.buffer_audio = []
            self.contador_silencio = 0
            if audio_completo is not None and audio_completo.size >= self.tasa_frecuencia // 4:
                try:
                    self.cola_audio.put_nowait(audio_completo)
                    print("Audio enviado a Whisper.")
                except queue.Full:
                    print("Cola de audio llena; se descarta esta captura.")

    def iniciar_escucha(self):
        print("Micrófono activo. Decí la palabra de activación.")
        with sd.InputStream(samplerate=self.tasa_frecuencia, channels=1, callback=self.grabar_audio, blocksize=self.tamano_chunk, dtype="float32"):
            while True:
                sd.sleep(1000)
