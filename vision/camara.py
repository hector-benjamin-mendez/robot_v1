import cv2

class Camara:
    def __init__(self):
        self.camara = cv2.VideoCapture(0)
        if not self.camara.isOpened():
            raise RuntimeError("No se pudo cargar la cámara.")

    def sacar_foto(self, ruta="foto-capturada.jpg"):
        ret, fotograma = self.camara.read()
        if not ret:
            print("No se pudo leer fotograma de la cámara.")
            return False
        cv2.imwrite(ruta, fotograma)
        print(f"Foto guardada como '{ruta}'")
        return True

    def cerrar(self):
        if self.camara.isOpened():
            self.camara.release()
        cv2.destroyAllWindows()