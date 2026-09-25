
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "mover_adelante",
            "description": "Hace que Tekni avance hacia adelante.",
            "parameters": {
                "type": "object",
                "properties": {
                    "velocidad": {
                        "type": "integer",
                        "description": "Velocidad entre 0 y 100."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mover_atras",
            "description": "Hace que Tekni retroceda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "velocidad": {
                        "type": "integer",
                        "description": "Velocidad entre 0 y 100."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "girar_izquierda",
            "description": "Hace que Tekni gire hacia la izquierda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "velocidad": {
                        "type": "integer",
                        "description": "Velocidad entre 0 y 100."
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "girar_derecha",
            "description": "Hace que Tekni gire hacia la derecha.",
            "parameters": {
                "type": "object",
                "properties": {
                    "velocidad": {
                        "type": "integer",
                        "description": "Velocidad entre 0 y 100."
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "detener",
            "description": "Detiene inmediatamente los motores de Tekni.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "guardar_memoria",
            "description": "Guarda información útil sobre una persona.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clave": {
                        "type": "string"
                    },
                    "valor": {
                        "type": "string"
                    }
                },
                "required": [
                    "clave",
                    "valor"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "obtener_memoria",
            "description": "Busca información previamente guardada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clave": {
                        "type": "string"
                    }
                },
                "required": [
                    "clave"
                ]
            }
        }
    }
]


# ==========================================
# CLASE DE HERRAMIENTAS
# ==========================================

class Tools:
    def __init__(self,movement,memory=None,vision=None):
        self.movement = movement
        self.memory = memory
        self.vision = vision

    # --------------------------------------
    # MOVIMIENTO
    # --------------------------------------
    def mover_adelante(self, velocidad=40):
        return self.movement.adelante(
            velocidad
        )

    def mover_atras(self, velocidad=40):
        return self.movement.atras(
            velocidad
        )

    def girar_izquierda(self, velocidad=40):
        return self.movement.izquierda(
            velocidad
        )

    def girar_derecha(self, velocidad=40):
        return self.movement.derecha(
            velocidad
        )

    def detener(self):
        return self.movement.parar()

    # --------------------------------------
    # MEMORIA
    # --------------------------------------
    def guardar_memoria(self,clave,valor):
        if self.memory is None:
            return False

        self.memory.guardar_memoria(
            clave,
            valor
        )

        return True

    def obtener_memoria(self, clave):

        if self.memory is None:
            return []

        return self.memory.obtener_memorias(
            clave
        )

    # --------------------------------------
    # EJECUTAR
    # --------------------------------------

    def ejecutar(self,nombre,argumentos):
        funciones = {

            "mover_adelante":
                self.mover_adelante,

            "mover_atras":
                self.mover_atras,

            "girar_izquierda":
                self.girar_izquierda,

            "girar_derecha":
                self.girar_derecha,

            "detener":
                self.detener,

            "guardar_memoria":
                self.guardar_memoria,

            "obtener_memoria":
                self.obtener_memoria
        }

        funcion = funciones.get(nombre)

        if funcion is None:

            print(
                f"❌ Herramienta desconocida: {nombre}"
            )

            return {
                "success": False,
                "error": "Herramienta desconocida"
            }

        try:

            resultado = funcion(
                **argumentos
            )

            return {
                "success": True,
                "resultado": resultado
            }

        except Exception as e:

            print(
                f"❌ Error ejecutando {nombre}: {e}"
            )

            return {
                "success": False,
                "error": str(e)
            }