import base64
import os
from pathlib import Path
from openai import OpenAI  # Usamos la misma librería oficial compatible

class Vision:
    def __init__(self, camara, api_key=None, modelo=None, ruta_imagen="data/foto-capturada.jpg", timeout=60):
        self.camara = camara
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.modelo = modelo or os.getenv("DEEPSEEK_VISION_MODEL", os.getenv("DEEPSEEK_MODEL", "deepseek-flash"))
        self.ruta_imagen = Path(ruta_imagen)
        self.timeout = timeout
        self.cliente = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def describir(self, instruccion="Describí brevemente lo que aparece frente a Tekni."):
        if not self.api_key:
            return {"success": False, "error": "Falta DEEPSEEK_API_KEY para analizar imágenes."}
        try:
            ruta = Path(self.camara.sacar_foto(str(self.ruta_imagen)))
            
            imagen_b64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
            data_url = f"data:image/jpeg;base64,{imagen_b64}"
            
            contexto_sistema = "Sos el sistema visual de Tekni. Describí solamente lo que se ve en la imagen. Diferenciá observaciones de suposiciones y no inventes detalles."
            prompt_final = f"{contexto_sistema}\n\nInstrucción: {instruccion}"

            # 4. Realizar la petición estructurada con el SDK
            respuesta = self.cliente.chat.completions.create(
                model=self.modelo,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_final},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ],
                    }
                ],
                timeout=self.timeout,
                extra_body={"thinking": {"type": "disabled"}},
            )
            texto = respuesta.choices[0].message.content
            return texto.strip() if texto else "No pude describir la imagen."            
        except Exception as exc:
            print("Error en visión multimodal: {}".format(exc))
            return {"success": False, "error": "No pude analizar la imagen: {}".format(exc)}
