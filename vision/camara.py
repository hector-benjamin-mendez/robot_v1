import cv2

class Camara():
    def __init__(self):
        self.camara = cv2.VideoCapture(0)
        if not self.camara.isOpened():
            print("No se pudo cargar la camara.")
            exit()

    def sacar_foto(self):
        ret, fotograma = self.camara.read()
        if not ret:
            print("No se pudo leer fotograma de la camara.")
            return
        cv2.imwrite('foto-capturada.jpg', fotograma)
        print("Foto guardada como 'foto-capturada.jpg'")
        self.camara.release()
        cv2.destroyAllWindows()
        return
        