import base64
import json
import os
from pathlib import Path

import requests


class Vision:
    def __init__(self, camara, api_key=None, modelo=None, ruta_imagen="data/foto-capturada.jpg", timeout=60):
        self.camara = camara
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.modelo = modelo or os.getenv("OPENAI_VISION_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
        self.ruta_imagen = Path(ruta_imagen)
        self.timeout = timeout

    def describir(self, instruccion="Describí brevemente lo que aparece frente a Tekni."):
        if not self.api_key:
            return {"success": False, "error": "Falta OPENAI_API_KEY para analizar imágenes."}
        try:
            ruta = Path(self.camara.sacar_foto(str(self.ruta_imagen)))
            imagen_b64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
            data_url = "data:image/jpeg;base64," + imagen_b64
            datos = {
                "model": self.modelo,
                "messages": [
                    {"role": "system", "content": "Sos el sistema visual de Tekni. Describí solamente lo que se ve en la imagen. Diferenciá observaciones de suposiciones y no inventes detalles."},
                    {"role": "user", "content": [
                        {"type": "text", "text": instruccion},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "auto"}},
                    ]},
                ],
            }
            respuesta = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"},
                data=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
                timeout=self.timeout,
            )
            respuesta.raise_for_status()
            payload = respuesta.json()
            texto = payload["choices"][0]["message"].get("content", "")
            return texto.strip() if texto else "No pude describir la imagen."
        except Exception as exc:
            print("Error en visión multimodal: {}".format(exc))
            return {"success": False, "error": "No pude analizar la imagen: {}".format(exc)}
