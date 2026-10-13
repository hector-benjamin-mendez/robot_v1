TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "mover_adelante", "description": "Hace que Tekni avance en línea recta.", "parameters": {"type": "object", "properties": {"velocidad": {"type": "integer", "minimum": 0, "maximum": 50, "description": "Velocidad conservadora entre 0 y 50."}, "duracion_ms": {"type": "integer", "minimum": 100, "maximum": 1000, "description": "Duración del movimiento, entre 100 y 1000 milisegundos."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "mover_atras", "description": "Hace que Tekni retroceda.", "parameters": {"type": "object", "properties": {"velocidad": {"type": "integer", "minimum": 0, "maximum": 50}, "duracion_ms": {"type": "integer", "minimum": 100, "maximum": 1000}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "girar_izquierda", "description": "Hace que Tekni gire a la izquierda.", "parameters": {"type": "object", "properties": {"velocidad": {"type": "integer", "minimum": 0, "maximum": 50}, "duracion_ms": {"type": "integer", "minimum": 100, "maximum": 1000}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "girar_derecha", "description": "Hace que Tekni gire a la derecha.", "parameters": {"type": "object", "properties": {"velocidad": {"type": "integer", "minimum": 0, "maximum": 50}, "duracion_ms": {"type": "integer", "minimum": 100, "maximum": 1000}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "detener", "description": "Detiene los motores de Tekni.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "ver_que_hay", "description": "Captura una imagen y describe lo que aparece en la cámara.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "guardar_memoria", "description": "Guarda un dato no sensible para futuras conversaciones.", "parameters": {"type": "object", "properties": {"clave": {"type": "string", "minLength": 1}, "valor": {"type": "string", "minLength": 1}}, "required": ["clave", "valor"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "obtener_memoria", "description": "Busca datos guardados anteriormente con una clave.", "parameters": {"type": "object", "properties": {"clave": {"type": "string", "minLength": 1}}, "required": ["clave"], "additionalProperties": False}}},
]


class Tools:
    def __init__(self, movement, memory=None, vision=None):
        self.movement = movement
        self.memory = memory
        self.vision = vision

    @staticmethod
    def _validar_velocidad(argumentos):
        velocidad = argumentos.get("velocidad", 30)
        if isinstance(velocidad, bool) or not isinstance(velocidad, int) or not 0 <= velocidad <= 50:
            raise ValueError("La velocidad debe ser un entero entre 0 y 50.")
        return velocidad

    def mover_adelante(self, velocidad=30, duracion_ms=500):
        return self.movement.adelante(self._validar_velocidad({"velocidad": velocidad}), duracion_ms)

    def mover_atras(self, velocidad=30, duracion_ms=500):
        return self.movement.atras(self._validar_velocidad({"velocidad": velocidad}), duracion_ms)

    def girar_izquierda(self, velocidad=30, duracion_ms=500):
        return self.movement.izquierda(self._validar_velocidad({"velocidad": velocidad}), duracion_ms)

    def girar_derecha(self, velocidad=30, duracion_ms=500):
        return self.movement.derecha(self._validar_velocidad({"velocidad": velocidad}), duracion_ms)

    def detener(self):
        return self.movement.parar()

    def ver_que_hay(self):
        if self.vision is None:
            return {"success": False, "error": "La cámara o el servicio de visión no están disponibles."}
        return self.vision.describir()

    def guardar_memoria(self, clave, valor):
        if self.memory is None:
            return {"success": False, "error": "La memoria no está disponible."}
        self.memory.guardar_memoria(clave, valor)
        return True

    def obtener_memoria(self, clave):
        if self.memory is None:
            return {"success": False, "error": "La memoria no está disponible."}
        return self.memory.obtener_memorias(clave)

    def ejecutar(self, nombre, argumentos):
        funciones = {
            "mover_adelante": self.mover_adelante,
            "mover_atras": self.mover_atras,
            "girar_izquierda": self.girar_izquierda,
            "girar_derecha": self.girar_derecha,
            "detener": self.detener,
            "ver_que_hay": self.ver_que_hay,
            "guardar_memoria": self.guardar_memoria,
            "obtener_memoria": self.obtener_memoria,
        }
        funcion = funciones.get(nombre)
        if funcion is None:
            return {"success": False, "error": "Herramienta desconocida."}
        if not isinstance(argumentos, dict):
            return {"success": False, "error": "Los argumentos deben ser un objeto JSON."}
        try:
            resultado = funcion(**argumentos)
            if isinstance(resultado, dict) and resultado.get("success") is False:
                return resultado
            if resultado is False:
                return {"success": False, "error": "El dispositivo no confirmó la acción."}
            return {"success": True, "resultado": resultado}
        except Exception as exc:
            print(f"Error ejecutando {nombre}: {exc}")
            return {"success": False, "error": str(exc)}
