from enum import Enum


class Estado(Enum):
    NORMAL = "normal"
    ESCUCHANDO = "escuchando"
    PENSANDO = "pensando"
    MOVIENDOSE = "moviendose"
    VIENDO = "viendo"
    HABLANDO = "hablando"
    ERROR = "error"
    EMERGENCIA = "emergencia"