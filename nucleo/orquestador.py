import json

from nucleo.estado import Estado
from ai.tools import TOOL_DEFINITIONS


class Orquestador:

    def __init__(self, llm, tools, tts=None, memoria=None, pantalla=None):
        self.llm = llm
        self.tools = tools
        self.tts = tts
        self.memoria = memoria
        self.pantalla = pantalla

        self.estado = Estado.NORMAL

        # Historial de conversación.
        # El system prompt NO está acá.
        # Lo agrega LLM automáticamente.
        self.historial = []

    # ==========================================
    # ESTADO
    # ==========================================

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

        print(f"🤖 Estado: {nuevo_estado.value}")

    # ==========================================
    # PROCESAR TEXTO
    # ==========================================

    def procesar_texto(self, texto):
        if not texto:
            return

        texto = texto.strip()

        if not texto:
            return

        print(f"\n👤 Usuario: {texto}")

        self.cambiar_estado(Estado.PENSANDO)

        self.historial.append({
            "role": "user",
            "content": texto
        })

        respuesta = self.llm.preguntar(
            self.historial,
            tools=TOOL_DEFINITIONS
        )

        if respuesta is None:
            self.error("No pude comunicarme con el modelo.")
            return

        self.procesar_respuesta(respuesta)

    # ==========================================
    # PROCESAR RESPUESTA DEL LLM
    # ==========================================

    def procesar_respuesta(self, respuesta):
        mensaje = respuesta.get("message", {})

        # Guardamos la respuesta del modelo
        self.historial.append(mensaje)

        tool_calls = mensaje.get("tool_calls")

        # ======================================
        # HERRAMIENTAS
        # ======================================

        if tool_calls:
            for tool_call in tool_calls:
                self.ejecutar_tool(tool_call)

            return

        # ======================================
        # RESPUESTA NORMAL
        # ======================================

        texto = mensaje.get("content", "")

        if texto:
            self.hablar(texto)
        else:
            self.cambiar_estado(Estado.NORMAL)

    # ==========================================
    # EJECUTAR TOOL
    # ==========================================

    def ejecutar_tool(self, tool_call):
        funcion = tool_call.get("function", {})

        nombre = funcion.get("name")
        argumentos = funcion.get("arguments", {})

        print(f"🔧 Herramienta: {nombre}")
        print(f"📦 Argumentos: {argumentos}")

        # Ollama puede devolver los argumentos
        # como JSON string.
        if isinstance(argumentos, str):
            try:
                argumentos = json.loads(argumentos)

            except json.JSONDecodeError:
                resultado = {
                    "success": False,
                    "error": "Argumentos JSON inválidos"
                }

                self.agregar_resultado_tool(
                    tool_call,
                    resultado
                )

                return

        # ======================================
        # SEGURIDAD
        # ======================================

        if not self.tool_permitida(nombre):
            print(f"🚨 Herramienta bloqueada: {nombre}")

            resultado = {
                "success": False,
                "error": "Herramienta no permitida"
            }

            self.agregar_resultado_tool(tool_call,resultado)

            return

        # ======================================
        # ESTADO
        # ======================================

        herramientas_movimiento = {
            "mover_adelante",
            "mover_atras",
            "girar_izquierda",
            "girar_derecha",
            "detener"
        }

        if nombre in herramientas_movimiento:
            self.cambiar_estado(Estado.MOVIENDOSE)
        else:
            self.cambiar_estado(Estado.PENSANDO)

        # ======================================
        # EJECUTAR
        # ======================================

        try:
            resultado = self.tools.ejecutar(
                nombre,
                argumentos
            )

        except Exception as e:
            print(f"❌ Error ejecutando herramienta: {e}")

            resultado = {
                "success": False,
                "error": str(e)
            }

        # ======================================
        # DEVOLVER RESULTADO AL LLM
        # ======================================

        self.agregar_resultado_tool(
            tool_call,
            resultado
        )

        # ======================================
        # SEGUNDA CONSULTA
        # ======================================

        respuesta = self.llm.preguntar(
            self.historial,
            tools=TOOL_DEFINITIONS
        )

        if respuesta is None:
            self.error(
                "La herramienta se ejecutó, "
                "pero no pude obtener una respuesta."
            )

            return

        self.procesar_respuesta(respuesta)

    # ==========================================
    # RESULTADO DE TOOL
    # ==========================================

    def agregar_resultado_tool(self, tool_call, resultado):
        self.historial.append({
            "role": "tool",
            "content": json.dumps(
                resultado,
                ensure_ascii=False
            ),
            "tool_call_id": tool_call.get("id")
        })

    # ==========================================
    # SEGURIDAD DE HERRAMIENTAS
    # ==========================================

    def tool_permitida(self, nombre):
        herramientas = {
            "mover_adelante",
            "mover_atras",
            "girar_izquierda",
            "girar_derecha",
            "detener",
            "guardar_memoria",
            "obtener_memoria"
        }

        return nombre in herramientas

    # ==========================================
    # HABLAR
    # ==========================================

    def hablar(self, texto):
        print(f"🤖 Tekni: {texto}")

        self.cambiar_estado(Estado.HABLANDO)

        if self.tts:
            self.tts.hablar(texto)

        self.cambiar_estado(Estado.NORMAL)

    # ==========================================
    # ERROR
    # ==========================================

    def error(self, mensaje):
        print(f"❌ {mensaje}")

        self.cambiar_estado(Estado.ERROR)

        self.hablar(mensaje)