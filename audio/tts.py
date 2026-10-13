import os

import numpy as np
import requests
import sounddevice as sd


class TTS:
    """Síntesis de voz por ElevenLabs; el audio PCM se reproduce localmente."""

    def __init__(self, api_key=None, voice_id=None, modelo=None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")
        self.modelo = modelo or os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
        self.tasa_frecuencia = 22050

    def hablar(self, texto):
        if not texto:
            return False
        if not self.api_key or not self.voice_id:
            print("ElevenLabs no está configurado; texto solamente: " + texto)
            return False
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?output_format=pcm_22050"
        try:
            respuesta = requests.post(
                url,
                headers={"xi-api-key": self.api_key, "Content-Type": "application/json", "Accept": "audio/pcm"},
                json={"text": texto, "model_id": self.modelo},
                timeout=45,
            )
            respuesta.raise_for_status()
            audio = np.frombuffer(respuesta.content, dtype=np.int16)
            if audio.size == 0:
                raise RuntimeError("ElevenLabs devolvió audio vacío.")
            sd.play(audio, samplerate=self.tasa_frecuencia)
            sd.wait()
            return True
        except Exception as exc:
            print(f"Error de TTS ElevenLabs: {exc}")
            return False
