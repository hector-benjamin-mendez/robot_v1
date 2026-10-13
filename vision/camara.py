import os
from pathlib import Path

import cv2


class Camara:
    def __init__(self, fuente=None):
        fuente = str(fuente if fuente is not None else os.getenv("CAMERA_SOURCE", "0"))
        if fuente.isdigit():
            self.camara = cv2.VideoCapture(int(fuente))
        elif "nvarguscamerasrc" in fuente or "!" in fuente:
            self.camara = cv2.VideoCapture(fuente, cv2.CAP_GSTREAMER)
        else:
            self.camara = cv2.VideoCapture(fuente)
        if not self.camara.isOpened():
            raise RuntimeError("No se pudo abrir la cámara. Revisá CAMERA_SOURCE y el pipeline CSI de la IMX219.")

    def sacar_foto(self, ruta="data/foto-capturada.jpg"):
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        ret, fotograma = self.camara.read()
        if not ret or fotograma is None:
            raise RuntimeError("La cámara está abierta, pero no entregó un fotograma.")
        if not cv2.imwrite(str(destino), fotograma):
            raise RuntimeError(f"No se pudo guardar la imagen en {destino}.")
        return str(destino)

    def cerrar(self):
        if getattr(self, "camara", None) is not None:
            self.camara.release()
        cv2.destroyAllWindows()
