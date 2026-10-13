import os

from faster_whisper import WhisperModel


class ProcesadorSTT:
    def __init__(self, cola_audio, callback_texto=None, modelo=None):
        self.cola_audio = cola_audio
        self.callback_texto = callback_texto
        nombre_modelo = modelo or os.getenv("WHISPER_MODEL", "tiny")
        print(f"Cargando Faster-Whisper ({nombre_modelo}, CPU int8)...")
        self.modelo_whisper = WhisperModel(nombre_modelo, device="cpu", compute_type="int8", cpu_threads=2)
        print("Whisper listo.")

    def transcribir(self, audio_data):
        segmentos, _ = self.modelo_whisper.transcribe(audio_data, language="es", beam_size=1, vad_filter=True)
        texto = " ".join(segmento.text.strip() for segmento in segmentos).strip()
        return texto

    def iniciar_procesamiento(self):
        while True:
            audio_data = self.cola_audio.get()
            if audio_data is None:
                return
            try:
                texto = self.transcribir(audio_data)
                if texto:
                    print(f"Texto transcripto: {texto}")
                    if self.callback_texto:
                        self.callback_texto(texto)
                else:
                    print("Whisper no detectó palabras claras.")
            except Exception as exc:
                print(f"Error procesando audio con Whisper: {exc}")
