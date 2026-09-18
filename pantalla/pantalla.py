import pygame
import sys
import random
import math


class Display:

    def __init__(self):
        # =========================
        # PYGAME
        # =========================

        pygame.init()

        info_pantalla = pygame.display.Info()

        self.ancho = info_pantalla.current_w
        self.alto = info_pantalla.current_h

        self.pantalla = pygame.display.set_mode(
            (self.ancho, self.alto),
            pygame.FULLSCREEN | pygame.NOFRAME
        )

        pygame.mouse.set_visible(False)
        pygame.display.set_caption("Tekni")

        self.reloj = pygame.time.Clock()

        # =========================
        # COLORES
        # =========================

        self.NEGRO = (12, 12, 16)
        self.CELESTE_NEON = (0, 230, 255)
        self.CELESTE_PUPILA = (0, 100, 130)
        self.BLANCO = (255, 255, 255)
        self.AZUL_LAGRIMA = (0, 150, 255)

        # =========================
        # ESTADO
        # =========================

        self.animacion_actual = "normal"

        self.parpadeando = False
        self.contador_parpadeo = 0

        self.tiempo = 0

        # =========================
        # INTERPOLACIÓN
        # =========================

        self.ancho_ojo = [140.0, 140.0]
        self.alto_ojo = [140.0, 140.0]

        self.y_cejas = [0.0, 0.0]
        self.angulo_cejas = [0.0, 0.0]

        self.boca_estado = [0.0, 0.0]

        # =========================
        # LÁGRIMAS
        # =========================

        self.lagrimas = []

        # =========================
        # ANIMACIONES
        # =========================

        self.animaciones = {
            "normal": {
                "ancho_ojo": 140,
                "alto_ojo": 140,
                "y_cejas": 0,
                "angulo_cejas": 0,
                "boca": 0
            },

            "feliz": {
                "ancho_ojo": 150,
                "alto_ojo": 110,
                "y_cejas": -15,
                "angulo_cejas": -0.15,
                "boca": 1
            },

            "enojado": {
                "ancho_ojo": 130,
                "alto_ojo": 130,
                "y_cejas": 20,
                "angulo_cejas": 0.4,
                "boca": -0.6
            },

            "sorprendido": {
                "ancho_ojo": 130,
                "alto_ojo": 190,
                "y_cejas": -35,
                "angulo_cejas": -0.1,
                "boca": 2
            },

            "llorando": {
                "ancho_ojo": 140,
                "alto_ojo": 100,
                "y_cejas": -5,
                "angulo_cejas": -0.35,
                "boca": -1.5
            }
        }

    # ==========================================================
    # API PÚBLICA
    # ==========================================================

    def cambiar_animacion(self, nombre):

        nombre = nombre.lower()

        if nombre not in self.animaciones:
            print(f"⚠️ Animación '{nombre}' no existe.")
            return False

        if nombre == self.animacion_actual:
            return True

        self.animacion_actual = nombre

        # Reiniciamos lágrimas cuando salimos de llorando
        if nombre != "llorando":
            self.lagrimas.clear()

        return True

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def suavizar(self, actual, objetivo, velocidad=0.15):
        return actual + (objetivo - actual) * velocidad

    # ==========================================================
    # PARPADEO
    # ==========================================================

    def actualizar_parpadeo(self):

        if self.animacion_actual in [
            "normal",
            "feliz",
            "enojado"
        ]:

            if (
                not self.parpadeando
                and random.randint(0, 180) == 1
            ):
                self.parpadeando = True
                self.contador_parpadeo = 0

    # ==========================================================
    # OBJETIVOS DE ANIMACIÓN
    # ==========================================================

    def actualizar_objetivos(self):

        animacion = self.animaciones[self.animacion_actual]

        respiracion = math.sin(self.tiempo) * 3

        self.ancho_ojo[1] = animacion["ancho_ojo"]
        self.alto_ojo[1] = animacion["alto_ojo"]

        self.y_cejas[1] = animacion["y_cejas"] + respiracion

        # Llorando tiene un movimiento un poco diferente
        if self.animacion_actual == "llorando":
            self.y_cejas[1] = (
                animacion["y_cejas"]
                + respiracion * 1.5
            )

        self.angulo_cejas[1] = animacion["angulo_cejas"]
        self.boca_estado[1] = animacion["boca"]

    # ==========================================================
    # INTERPOLACIÓN
    # ==========================================================

    def actualizar_interpolacion(self):

        self.ancho_ojo[0] = self.suavizar(
            self.ancho_ojo[0],
            self.ancho_ojo[1]
        )

        self.alto_ojo[0] = self.suavizar(
            self.alto_ojo[0],
            self.alto_ojo[1]
        )

        self.y_cejas[0] = self.suavizar(
            self.y_cejas[0],
            self.y_cejas[1]
        )

        self.angulo_cejas[0] = self.suavizar(
            self.angulo_cejas[0],
            self.angulo_cejas[1]
        )

        self.boca_estado[0] = self.suavizar(
            self.boca_estado[0],
            self.boca_estado[1]
        )

    # ==========================================================
    # LÁGRIMAS
    # ==========================================================

    def actualizar_lagrimas(self, izq_x, der_x, y_origen):

        if (
            self.animacion_actual == "llorando"
            and random.randint(0, 3) == 1
        ):

            self.lagrimas.append([
                izq_x + random.randint(-40, 40),
                y_origen,
                random.uniform(3, 6),
                random.randint(6, 10)
            ])

            self.lagrimas.append([
                der_x + random.randint(-40, 40),
                y_origen,
                random.uniform(3, 6),
                random.randint(6, 10)
            ])

        for lagrima in self.lagrimas[:]:

            lagrima[1] += lagrima[2]

            if lagrima[1] > self.alto - 40:
                self.lagrimas.remove(lagrima)

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def procesar_eventos(self):

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    return False

                elif evento.key == pygame.K_1:
                    self.cambiar_animacion("normal")

                elif evento.key == pygame.K_2:
                    self.cambiar_animacion("feliz")

                elif evento.key == pygame.K_3:
                    self.cambiar_animacion("enojado")

                elif evento.key == pygame.K_4:
                    self.cambiar_animacion("sorprendido")

                elif evento.key == pygame.K_5:
                    self.cambiar_animacion("llorando")

        return True

    # ==========================================================
    # OJOS
    # ==========================================================

    def dibujar_ojos(self, izq_x, izq_y, der_x, der_y):

        if (
            self.parpadeando
            and self.animacion_actual != "llorando"
        ):

            pygame.draw.rect(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    izq_x - 70,
                    izq_y - 4,
                    140,
                    8
                ),
                border_radius=4
            )

            pygame.draw.rect(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    der_x - 70,
                    der_y - 4,
                    140,
                    8
                ),
                border_radius=4
            )

            self.contador_parpadeo += 1

            if self.contador_parpadeo > 4:
                self.parpadeando = False

            return

        ancho = self.ancho_ojo[0]
        alto = self.alto_ojo[0]

        rect_izq = (
            int(izq_x - ancho / 2),
            int(izq_y - alto / 2),
            int(ancho),
            int(alto)
        )

        rect_der = (
            int(der_x - ancho / 2),
            int(der_y - alto / 2),
            int(ancho),
            int(alto)
        )

        # Ojos
        pygame.draw.ellipse(
            self.pantalla,
            self.CELESTE_NEON,
            rect_izq
        )

        pygame.draw.ellipse(
            self.pantalla,
            self.CELESTE_NEON,
            rect_der
        )

        # Pupilas
        p_ancho = ancho * 0.7
        p_alto = alto * 0.7

        pygame.draw.ellipse(
            self.pantalla,
            self.CELESTE_PUPILA,
            (
                int(izq_x - p_ancho / 2),
                int(izq_y - p_alto / 2),
                int(p_ancho),
                int(p_alto)
            )
        )

        pygame.draw.ellipse(
            self.pantalla,
            self.CELESTE_PUPILA,
            (
                int(der_x - p_ancho / 2),
                int(der_y - p_alto / 2),
                int(p_ancho),
                int(p_alto)
            )
        )

        # Brillo
        brillo_x = ancho * 0.15
        brillo_y = -alto * 0.15

        pygame.draw.circle(
            self.pantalla,
            self.BLANCO,
            (
                int(izq_x + brillo_x),
                int(izq_y + brillo_y)
            ),
            int(ancho * 0.08)
        )

        pygame.draw.circle(
            self.pantalla,
            self.BLANCO,
            (
                int(der_x + brillo_x),
                int(der_y + brillo_y)
            ),
            int(ancho * 0.08)
        )

        # Párpados / expresión
        if self.animacion_actual == "feliz":

            pygame.draw.rect(
                self.pantalla,
                self.NEGRO,
                (
                    izq_x - 90,
                    izq_y + int(alto / 2) - 15,
                    180,
                    100
                )
            )

            pygame.draw.rect(
                self.pantalla,
                self.NEGRO,
                (
                    der_x - 90,
                    der_y + int(alto / 2) - 15,
                    180,
                    100
                )
            )

        elif self.animacion_actual == "llorando":

            pygame.draw.rect(
                self.pantalla,
                self.NEGRO,
                (
                    izq_x - 90,
                    izq_y + int(alto / 2) - 5,
                    180,
                    100
                )
            )

            pygame.draw.rect(
                self.pantalla,
                self.NEGRO,
                (
                    der_x - 90,
                    der_y + int(alto / 2) - 5,
                    180,
                    100
                )
            )

    # ==========================================================
    # CEJAS
    # ==========================================================

    def dibujar_ceja(
        self,
        x_centro,
        y_centro,
        angulo,
        es_izquierda
    ):

        largo = 140
        grosor = 16

        if not es_izquierda:
            angulo = -angulo

        dx = math.cos(angulo) * (largo / 2)
        dy = math.sin(angulo) * (largo / 2)

        pygame.draw.line(
            self.pantalla,
            self.CELESTE_NEON,
            (
                int(x_centro - dx),
                int(y_centro - dy)
            ),
            (
                int(x_centro + dx),
                int(y_centro + dy)
            ),
            grosor
        )

    def dibujar_cejas(self, izq_x, der_x):

        ceja_base_y = self.alto // 2 - 120

        self.dibujar_ceja(
            izq_x,
            ceja_base_y + self.y_cejas[0],
            self.angulo_cejas[0],
            True
        )

        self.dibujar_ceja(
            der_x,
            ceja_base_y + self.y_cejas[0],
            self.angulo_cejas[0],
            False
        )

    # ==========================================================
    # BOCA
    # ==========================================================

    def dibujar_boca(self):

        boca_x = self.ancho // 2
        boca_y = self.alto // 2 + 130

        estado = self.boca_estado[0]

        if (
            estado > 0.1
            and self.animacion_actual != "sorprendido"
        ):

            ancho_boca = 240
            alto_boca = 30 + (estado * 50)

            pygame.draw.arc(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    int(boca_x - ancho_boca / 2),
                    int(boca_y - alto_boca / 2),
                    int(ancho_boca),
                    int(alto_boca)
                ),
                math.pi,
                2 * math.pi,
                16
            )

        elif self.animacion_actual == "sorprendido":

            pygame.draw.ellipse(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    int(boca_x - 45),
                    int(boca_y - 30),
                    90,
                    110
                ),
                12
            )

        elif estado < -0.1:

            ancho_boca = 220
            alto_boca = 20 + (abs(estado) * 45)

            pygame.draw.arc(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    int(boca_x - ancho_boca / 2),
                    int(boca_y + 10),
                    int(ancho_boca),
                    int(alto_boca)
                ),
                0,
                math.pi,
                14
            )

        else:

            ancho_boca = 220

            pygame.draw.line(
                self.pantalla,
                self.CELESTE_NEON,
                (
                    int(boca_x - ancho_boca / 2),
                    int(boca_y)
                ),
                (
                    int(boca_x + ancho_boca / 2),
                    int(boca_y)
                ),
                14
            )

    # ==========================================================
    # RENDER
    # ==========================================================

    def dibujar(self):

        self.pantalla.fill(self.NEGRO)

        separacion_ojos = int(self.ancho * 0.21)

        izq_x = (self.ancho // 2) - separacion_ojos
        der_x = (self.ancho // 2) + separacion_ojos

        izq_y = (self.alto // 2) - 20
        der_y = (self.alto // 2) - 20

        # Lágrimas
        self.actualizar_lagrimas(
            izq_x,
            der_x,
            izq_y + 30
        )

        # Ojos
        self.dibujar_ojos(
            izq_x,
            izq_y,
            der_x,
            der_y
        )

        # Lágrimas
        for lagrima in self.lagrimas:

            pygame.draw.ellipse(
                self.pantalla,
                self.AZUL_LAGRIMA,
                (
                    int(lagrima[0]),
                    int(lagrima[1]),
                    int(lagrima[3]),
                    int(lagrima[3] * 1.6)
                )
            )

        # Cejas
        self.dibujar_cejas(
            izq_x,
            der_x
        )

        # Boca
        self.dibujar_boca()

        pygame.display.flip()

    # ==========================================================
    # ACTUALIZACIÓN
    # ==========================================================

    def actualizar(self):
        self.tiempo += 0.05
        self.actualizar_parpadeo()
        self.actualizar_objetivos()
        self.actualizar_interpolacion()

    # ==========================================================
    # LOOP PRINCIPAL
    # ==========================================================

    def iniciar(self):
        print("Pantalla robot iniciado.")
        try:
            ejecutando = True
            while ejecutando:
                ejecutando = self.procesar_eventos()
                self.actualizar()
                self.dibujar()
                self.reloj.tick(60)
        except KeyboardInterrupt:
            print("\nSaliendo del display...")
        finally:
            pygame.quit()