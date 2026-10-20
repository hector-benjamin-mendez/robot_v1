import os
from pathlib import Path
from openai import OpenAI

class LLM:
    def __init__(self, modelo=None, prompt_path=None, api_key=None, timeout=45):
        self.modelo = modelo or os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
        self.api_keyy = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.cliente = OpenAI(api_key=self.api_keyy,base_url="https://api.deepseek.com")
        self.timeout = timeout
        ruta_prompt = Path(prompt_path) if prompt_path else Path(__file__).with_name("tekni.md")
        self.system_prompt = self.cargar_prompt(ruta_prompt)

    @staticmethod
    def cargar_prompt(ruta):
        try:
            return Path(ruta).read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError("No se pudo cargar el prompt {}: {}".format(ruta, exc))

    def preguntar(self, mensajes, tools=None):
        if not self.api_keyy:
            print("Falta DEEPSEEK_API_KEY en las variables de entorno.")
            return None
            
        # 1. Construir la lista de mensajes incluyendo el system prompt
        mensajes_completos = [{"role": "system", "content": self.system_prompt}]
        mensajes_completos.extend(mensajes)
        
        # 2. Estructurar los datos de la petición básica
        datos = {
            "model": self.modelo, 
            "messages": mensajes_completos,
            "timeout": self.timeout,
            # El modo "thinking" viene activado por defecto y agrega latencia: lo apagamos.
            "extra_body": {"thinking": {"type": "disabled"}},
        }
        if tools:
            datos["tools"] = tools
            datos["tool_choice"] = "auto"           
        try:
            respuesta = self.cliente.chat.completions.create(**datos)
            # Convertimos el objeto del SDK a diccionario para que el orquestador use .get().
            mensaje = respuesta.choices[0].message.model_dump(exclude_none=True)
            mensaje.setdefault("content", "")
            return {"message": mensaje}
            
        except Exception as exc: 
            print("Error consultando DeepSeek: {}".format(exc))
            return None
