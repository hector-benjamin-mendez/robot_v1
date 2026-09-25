from dataclasses import dataclass

@dataclass
class MemoriaItem:
    clave: str
    valor: str


@dataclass
class Recordatorio:
    texto: str
    fecha: str
    completado: bool = False