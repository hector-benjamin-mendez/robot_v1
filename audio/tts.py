import subprocess
import os


class TTS:
    def __init__(self, modelo, salida_audio="voz.wav"):
        self.modelo = modelo
        self.salida_audio = salida_audio

    def hablar(self, texto):
        if not texto:
            return
        try:
            print(f"Tekni: {texto}")
            subprocess.run(
                [
                    "piper",
                    "--model", self.modelo,
                    "--output_file", self.salida_audio
                ],
                input=texto,
                text=True,
                check=True
            )

            self.reproducir()
        except Exception as e:
            print(f"Error en TTS: {e}")

    def reproducir(self):
        try:
            subprocess.run(
                ["aplay", self.salida_audio],
                check=True
            )
        except Exception as e:
            print(f"Error reproduciendo audio: {e}")