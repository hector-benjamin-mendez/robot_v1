import webrtcvad
import numpy as np
class DetectorVoz:
    def __init__(self):
        self.tasa_frecuencia = 16000
        self.duracion_frame = 30
        self.vad = webrtcvad.Vad(2)

    def hay_voz(self, frame_audio):
        audio_int16 = (frame_audio * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        return self.vad.is_speech(audio_bytes, self.tasa_frecuencia)