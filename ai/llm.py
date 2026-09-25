import requests
from pathlib import Path


class LLM:
    def __init__(self,modelo="qwen3:4b",url="http://localhost:11434/api/chat",prompt_path=None):
        self.modelo = modelo
        self.url = url
        if prompt_path:
            self.system_prompt = self.cargar_prompt(prompt_path)
        else:
            self.system_prompt = ""

    def cargar_prompt(self, ruta):
        ruta = Path(ruta)
        try:
            return ruta.read_text(encoding="utf-8")
        except Exception as e:
            print(f"No se pudo cargar el prompt: {e}")
            return ""

    def preguntar(self, mensajes, tools=None):
        mensajes_completos = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]
        mensajes_completos.extend(mensajes)
        datos = {
            "model": self.modelo,
            "messages": mensajes_completos,
            "stream": False
        }
        if tools:
            datos["tools"] = tools
        try:
            respuesta = requests.post(
                self.url,
                json=datos,
                timeout=120
            )
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.exceptions.RequestException as e:
            print(f" Error conectando con Ollama: {e}")
            return None