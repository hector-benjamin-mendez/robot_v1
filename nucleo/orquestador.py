import json
from ai.tools import TOOL_DEFINITIONS
from nucleo.estado import Estado


class Orquestador:
    def __init__(self, llm, tools, tts=None, memoria=None, pantalla=None, max_rondas_herramientas=4):
        self.llm = llm
        self.tools = tools
        self.tts = tts
        self.memoria = memoria
        self.pantalla = pantalla
        self.estado = Estado.NORMAL
        self.historial = []
        self.max_rondas_herramientas = max_rondas_herramientas

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        print(f"Tekni estado: {nuevo_estado.value}")
        if self.pantalla:
            self.pantalla.actualizar_segon_estado(nuevo_estado)

    def indicar_escucha(self):
        """Llamar a esto inmediatamente cuando el usuario presiona el pulsador físico."""
        self.cambiar_estado(Estado.ESCUCHANDO)

    def procesar_texto(self, texto):
        if not isinstance(texto, str) or not texto.strip():
            self.cambiar_estado(Estado.NORMAL)
            return
        texto = texto.strip()
        print(f"\nUsuario: {texto}")
        self.cambiar_estado(Estado.PENSANDO)
        self.historial.append({"role": "user", "content": texto})
        self._consultar_modelo()

    def _consultar_modelo(self):
        for _ in range(self.max_rondas_herramientas):
            respuesta = self.llm.preguntar(self.historial, tools=TOOL_DEFINITIONS)
            if respuesta is None:
                self.error("No pude comunicarme con el modelo. Revisá la conexión a Internet y la API.")
                return
            mensaje = respuesta.get("message", {})
            if not mensaje:
                self.error("El modelo devolvió una respuesta vacía.")
                return
            self.historial.append(mensaje)
            tool_calls = mensaje.get("tool_calls") or []
            if not tool_calls:
                texto = mensaje.get("content") or "No tengo una respuesta para eso ahora."
                self.hablar(texto)
                return
            
            for tool_call in tool_calls:
                resultado = self._ejecutar_tool(tool_call)
                self.historial.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "content": json.dumps(resultado, ensure_ascii=False),
                })
        self.hablar("Hice varias operaciones seguidas y voy a frenar acá para evitar un bucle.")

    def _ejecutar_tool(self, tool_call):
        funcion = tool_call.get("function", {})
        nombre = funcion.get("name", "")
        argumentos = funcion.get("arguments", "{}")
        print(f"Herramienta solicitada: {nombre} {argumentos}")
        if nombre not in {item["function"]["name"] for item in TOOL_DEFINITIONS}:
            return {"success": False, "error": "Herramienta no permitida."}
        if isinstance(argumentos, str):
            try:
                argumentos = json.loads(argumentos or "{}")
            except json.JSONDecodeError:
                return {"success": False, "error": "Argumentos JSON inválidos."}
        if not isinstance(argumentos, dict):
            return {"success": False, "error": "Los argumentos deben ser un objeto."}
        
        movimiento = nombre in {"mover_adelante", "mover_atras", "girar_izquierda", "girar_derecha", "detener"}
        self.cambiar_estado(Estado.MOVIENDOSE if movimiento else Estado.VIENDO if nombre == "ver_que_hay" else Estado.PENSANDO)
        resultado = self.tools.ejecutar(nombre, argumentos)
        if movimiento and not resultado.get("success"):
            self.cambiar_estado(Estado.EMERGENCIA)
            print("Aviso: la acción de movimiento no fue confirmada por la ESP32.")
        return resultado

    def hablar(self, texto):
        print(f"Tekni: {texto}")
        self.cambiar_estado(Estado.HABLANDO)
        if self.tts:
            self.tts.hablar(texto)
        self.cambiar_estado(Estado.NORMAL)

    def error(self, mensaje):
        print(f"Error: {mensaje}")
        self.cambiar_estado(Estado.ERROR)
        self.hablar(mensaje)
