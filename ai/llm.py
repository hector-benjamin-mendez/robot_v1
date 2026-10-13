import json
import os
from pathlib import Path

import requests


class LLM:
    """Cliente REST para OpenAI; evita depender del SDK oficial en el Jetson."""

    def __init__(self, modelo=None, prompt_path=None, api_key=None, timeout=45):
        self.modelo = modelo or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.timeout = timeout
        ruta_prompt = Path(prompt_path) if prompt_path else Path(__file__).with_name("prompts.md")
        self.system_prompt = self.cargar_prompt(ruta_prompt)

    @staticmethod
    def cargar_prompt(ruta):
        try:
            return Path(ruta).read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError("No se pudo cargar el prompt {}: {}".format(ruta, exc))

    def preguntar(self, mensajes, tools=None):
        if not self.api_key:
            print("Falta OPENAI_API_KEY en las variables de entorno.")
            return None
        mensajes_completos = [{"role": "system", "content": self.system_prompt}]
        mensajes_completos.extend(mensajes)
        datos = {"model": self.modelo, "messages": mensajes_completos}
        if tools:
            datos["tools"] = tools
            datos["tool_choice"] = "auto"
        try:
            respuesta = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"},
                data=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
                timeout=self.timeout,
            )
            respuesta.raise_for_status()
            payload = respuesta.json()
            return {"message": payload["choices"][0]["message"]}
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            print("Error consultando OpenAI: {}".format(exc))
            return None
