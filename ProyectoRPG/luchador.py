import pygame
import sys

# -----------------------------
# FUNCIÓN PARA CARGAR IMÁGENES
# -----------------------------

def cargar_imagen(ruta, tamaño):
    try:
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.scale(img, tamaño)
    except Exception as e:
        print(f"[AVISO] No se pudo cargar '{ruta}': {e}")
        return None


# -----------------------------
# CLASE LUCHADOR (LÓGICA)
# -----------------------------

class Luchador:
    def __init__(self, nombre="Luchador"):
        # Atributos base según documento:
        # +5 Fuerza, +10 Agilidad, +5 Vitalidad
        self.nombre = nombre
        self.nivel = 1
        self.fuerza = 5
        self.inteligencia = 0
        self.agilidad = 10
        self.vitalidad = 5
        self.hp = max(1, self.vitalidad // 2)

    def recibir_daño(self, cantidad):
        self.hp = max(0, self.hp - cantidad)

    def ataque_basico(self, objetivo):
        daño = max(1, self.fuerza // 20)
        objetivo.recibir_daño(daño)
        return f"{self.nombre} golpea a {objetivo.nombre} causando {daño} de daño."

    def ataque_rapido(self, objetivo):
        daño = max(1, (self.fuerza // 20) + 1)
        objetivo.recibir_daño(daño)
        return f"{self.nombre} realiza un ataque rápido sobre {objetivo.nombre}, causando {daño} de daño."

    def __repr__(self):
        return (f"{self.nombre} (Nv {self.nivel}) | "
                f"F:{self.fuerza} Int:{self.inteligencia} "
                f"Agi:{self.agilidad} Vit:{self.vitalidad} HP:{self.hp}")


# -----------------------------
# INTERFAZ PYGAME DEL LUCHADOR
# -----------------------------

def main_luchador():
    pygame.init()

    # ===================== DIMENSIONES VENTANA =====================
    # Puedes cambiar ANCHO y ALTO si quieres otra resolución.
    ANCHO, ALTO = 600, 800
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Clase Luchador - Grupo 5")

    # ===================== COLORES =====================
    BLANCO = (255, 255, 255)
    NEGRO = (10, 10, 10)
    AZUL = (0, 100, 255)
    AZUL_CLARO = (100, 150, 255)
    GRIS_OSCURO = (25, 25, 25)

    # ===================== FUENTES =====================
    fuente_titulo = pygame.font.Font(None, 72)
    fuente_subtitulo = pygame.font.Font(None, 40)
    fuente_texto = pygame.font.Font(None, 26)
    fuente_peque = pygame.font.Font(None, 22)

    reloj = pygame.time.Clock()
    FPS = 60

    luchador = Luchador()

    # ========== CARGA DE IMÁGENES ==========
    # Ajusta los nombres/paths si tu carpeta se llama distinto.
    IMAGENES = {
        "luchador":    cargar_imagen("imagenes/Luchador.png",        (230, 280)),
        "monje":       cargar_imagen("imagenes/Monje.png",           (150, 150)),
        "puno_divino": cargar_imagen("imagenes/Puno_divino.png",     (150, 150)),
        "monje_veng":  cargar_imagen("imagenes/Monje_vengador.png",  (150, 150)),
        "berserker":   cargar_imagen("imagenes/Berserker.png",       (150, 150)),
        "derviche":    cargar_imagen("imagenes/Derviche.png",        (150, 150)),
        "puno_mortal": cargar_imagen("imagenes/Puno_mortal.png",     (150, 150)),
    }

    # ---------- ATRIBUTOS BASE PARA LA PANTALLA PRINCIPAL ----------
    atributos_ui = [
        ("Fuerza", luchador.fuerza),
        ("Agilidad", luchador.agilidad),
        ("Vitalidad", luchador.vitalidad),
    ]

    descripcion_lineas = [
        "El Luchador es una clase física ágil,",
        "experta en combate cuerpo a cuerpo.",
        "Sus evoluciones siguen caminos de Luz",
        "u Oscuridad, que modifican sus atributos base."
    ]

    # ===================== BOTONES =====================

    class Boton:
        def __init__(self, x, y, ancho, alto, texto):
            # x, y, ancho, alto -> POSICIÓN Y TAMAÑO DEL BOTÓN
            self.rect = pygame.Rect(x, y, ancho, alto)
            self.texto = texto
            self.color_base = AZUL
            self.color_hover = AZUL_CLARO
            self.color_actual = self.color_base

        def dibujar(self, superficie):
            pygame.draw.rect(superficie, self.color_actual, self.rect, border_radius=8)
            pygame.draw.rect(superficie, BLANCO, self.rect, 2, border_radius=8)
            txt = fuente_subtitulo.render(self.texto, True, BLANCO)
            txt_rect = txt.get_rect(center=self.rect.center)
            superficie.blit(txt, txt_rect)

        def actualizar(self, pos_mouse):
            self.color_actual = self.color_hover if self.rect.collidepoint(pos_mouse) else self.color_base

        def fue_clickeado(self, pos_mouse):
            return self.rect.collidepoint(pos_mouse)

    # ---------- POSICIONES CLAVE (MODIFICA AQUÍ PARA MOVER COSAS) ----------

    # Panel de imagen de la clase
    IMG_PANEL = pygame.Rect(40, 130, 230, 280)        # <--- Imagen Luchador

    # Atributos (bloque completo)
    ATRIB_X = 280                                      # <--- X de “Fuerza/Agilidad/Vitalidad”
    ATRIB_Y = 170                                      # <--- Y inicial de atributos

    # Caja de descripción
    DESC_BOX = pygame.Rect(40, 430, ANCHO - 80, 110)  # <--- Descripción general

    # Zona base para los títulos y botones Luz/Oscuridad
    BASE_BOTONES_Y = 580                               # <--- Altura del bloque de botones

    boton_luz = Boton(ANCHO//2 - 220, BASE_BOTONES_Y + 40, 180, 80, "Luz")
    boton_oscuridad = Boton(ANCHO//2 + 40,  BASE_BOTONES_Y + 40, 180, 80, "Oscuridad")
    boton_volver = Boton(ANCHO//2 - 150, BASE_BOTONES_Y + 150, 300, 55, "Volver atrás")

    # ---------- ESTADOS DE PANTALLA ----------
    ESTADO_CLASE = "clase"
    ESTADO_LUZ = "luz"
    ESTADO_OSCURIDAD = "oscuridad"

    estado_pantalla = ESTADO_CLASE

    # ---------- FUNCIONES DE DIBUJO REUTILIZABLES ----------

    def dibujar_barras_atributos(atributos, x_texto, y_texto, ancho_barra=190):
        """Barras de la pantalla principal (clase luchador)."""
        alto_barra = 18
        espacio_y = 40
        for nombre, valor in atributos:
            # Texto del atributo
            txt = fuente_texto.render(nombre, True, BLANCO)
            pantalla.blit(txt, (x_texto, y_texto))

            # Distancia entre el texto y la barra -> x_texto + 80
            rect_barra = pygame.Rect(x_texto + 80, y_texto + 2, ancho_barra, alto_barra)
            pygame.draw.rect(pantalla, BLANCO, rect_barra, 2)

            # Relleno proporcional
            v = max(0, min(100, valor))
            relleno = int((ancho_barra - 4) * v / 100)
            rect_relleno = pygame.Rect(rect_barra.x + 2, rect_barra.y + 2,
                                       relleno, alto_barra - 4)
            pygame.draw.rect(pantalla, AZUL_CLARO, rect_relleno)

            # Valor numérico
            txt_valor = fuente_texto.render(str(valor), True, BLANCO)
            pantalla.blit(txt_valor, (rect_barra.right + 8, y_texto))

            y_texto += espacio_y

    def dibujar_barra_bonus(x, y, texto, valor):
        """Barra pequeña usada en las pantallas de evoluciones."""
        txt = fuente_texto.render(texto, True, BLANCO)
        pantalla.blit(txt, (x, y))

        ancho_barra = 140
        alto_barra = 16
        rect_barra = pygame.Rect(x + 130, y + 3, ancho_barra, alto_barra)
        pygame.draw.rect(pantalla, BLANCO, rect_barra, 2)

        v = max(0, min(100, valor))
        relleno = int((ancho_barra - 4) * v / 100)
        rect_relleno = pygame.Rect(rect_barra.x + 2, rect_barra.y + 2,
                                   relleno, alto_barra - 4)
        pygame.draw.rect(pantalla, AZUL_CLARO, rect_relleno)

    # ==================== BUCLE PRINCIPAL ====================
    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)
        pos_mouse = pygame.mouse.get_pos()

        # -------- MANEJO DE EVENTOS --------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # ---- LÓGICA DE CLIC SEGÚN LA PANTALLA ACTUAL ----
                if estado_pantalla == ESTADO_CLASE:
                    if boton_volver.fue_clickeado(pos_mouse):
                        # Desde la pantalla principal: salir
                        ejecutando = False
                    elif boton_luz.fue_clickeado(pos_mouse):
                        estado_pantalla = ESTADO_LUZ
                    elif boton_oscuridad.fue_clickeado(pos_mouse):
                        estado_pantalla = ESTADO_OSCURIDAD

                elif estado_pantalla in (ESTADO_LUZ, ESTADO_OSCURIDAD):
                    # En cualquiera de las pantallas de evoluciones,
                    # el botón Volver atrás regresa a la pantalla de clase
                    if boton_volver.fue_clickeado(pos_mouse):
                        estado_pantalla = ESTADO_CLASE

        # Hovers
        boton_luz.actualizar(pos_mouse)
        boton_oscuridad.actualizar(pos_mouse)
        boton_volver.actualizar(pos_mouse)

        # -------- DIBUJO SEGÚN ESTADO --------
        pantalla.fill(NEGRO)

        # ========== PANTALLA PRINCIPAL: CLASE LUCHADOR ==========
        if estado_pantalla == ESTADO_CLASE:
            titulo = fuente_titulo.render("Luchador", True, BLANCO)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 70)))

            # Panel de imagen
            pygame.draw.rect(pantalla, BLANCO, IMG_PANEL, 2)

            imagen = IMAGENES["luchador"]
            if imagen:
                pantalla.blit(imagen, (IMG_PANEL.x, IMG_PANEL.y))
            else:
                txt1 = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt1, txt1.get_rect(center=IMG_PANEL.center))

            # Atributos base
            dibujar_barras_atributos(atributos_ui, ATRIB_X, ATRIB_Y)

            # Descripción
            pygame.draw.rect(pantalla, GRIS_OSCURO, DESC_BOX)
            pygame.draw.rect(pantalla, BLANCO, DESC_BOX, 1)
            y_desc = DESC_BOX.y + 10
            for linea in descripcion_lineas:
                txt = fuente_peque.render(linea, True, BLANCO)
                pantalla.blit(txt, (DESC_BOX.x + 10, y_desc))
                y_desc += 20

            # Textos Luz / Oscuridad
            txt_luz = fuente_subtitulo.render("Luz", True, BLANCO)
            pantalla.blit(txt_luz, (ANCHO//2 - 190, BASE_BOTONES_Y))

            txt_osc = fuente_subtitulo.render("Oscuridad", True, BLANCO)
            pantalla.blit(txt_osc, (ANCHO//2 + 40, BASE_BOTONES_Y))

            # Botones
            boton_luz.dibujar(pantalla)
            boton_oscuridad.dibujar(pantalla)
            boton_volver.dibujar(pantalla)

        # ========== PANTALLA CAMINO DE LA LUZ ==========
        elif estado_pantalla == ESTADO_LUZ:
            titulo = fuente_titulo.render("Luz", True, BLANCO)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 60)))

            subt = fuente_subtitulo.render("Evoluciones del Luchador", True, BLANCO)
            pantalla.blit(subt, subt.get_rect(center=(ANCHO//2, 110)))

            # ---- Primera evolución (nivel 10) ----
            txt_prim = fuente_texto.render("Primera evolución (nivel 10)", True, BLANCO)
            pantalla.blit(txt_prim, (40, 170))

            rect_img1 = pygame.Rect(40, 190, 150, 150)  # Imagen Monje
            pygame.draw.rect(pantalla, BLANCO, rect_img1, 2)
            img = IMAGENES["monje"]
            if img:
                pantalla.blit(img, rect_img1.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img1.center))

            txt_monje = fuente_texto.render("Monje", True, BLANCO)
            pantalla.blit(txt_monje, (220, 200))
            dibujar_barra_bonus(220, 230, "+10 Agilidad", 10)

            desc_monje = fuente_peque.render("Especialista en movilidad y golpes rápidos.", True, BLANCO)
            pantalla.blit(desc_monje, (220, 260))

            # ---- Segunda evolución (nivel 20) ----
            txt_seg = fuente_texto.render("Segunda evolución (nivel 20)", True, BLANCO)
            pantalla.blit(txt_seg, (40, 350))

            # Izquierda: Puño Divino (Luz / Luz)
            rect_img2 = pygame.Rect(40, 370, 150, 150)
            pygame.draw.rect(pantalla, BLANCO, rect_img2, 2)
            img2 = IMAGENES["puno_divino"]
            if img2:
                pantalla.blit(img2, rect_img2.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img2.center))

            txt_pd = fuente_texto.render("Puño Divino (Luz/Luz)", True, BLANCO)
            pantalla.blit(txt_pd, (210, 380))
            dibujar_barra_bonus(210, 410, "+10 Agilidad", 10)
            dibujar_barra_bonus(210, 440, "+5 Vitalidad", 5)

            # Derecha: Monje Vengador (Luz / Oscuridad)
            rect_img3 = pygame.Rect(40, 540, 150, 150)
            pygame.draw.rect(pantalla, BLANCO, rect_img3, 2)
            img3 = IMAGENES["monje_veng"]
            if img3:
                pantalla.blit(img3, rect_img3.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img3.center))

            txt_mv = fuente_texto.render("Monje Vengador (Luz/Osc)", True, BLANCO)
            pantalla.blit(txt_mv, (210, 550))
            dibujar_barra_bonus(210, 580, "+10 Fuerza", 10)
            dibujar_barra_bonus(210, 610, "+5 Agilidad", 5)

            # Botón Volver
            boton_volver.dibujar(pantalla)

        # ========== PANTALLA CAMINO DE LA OSCURIDAD ==========
        elif estado_pantalla == ESTADO_OSCURIDAD:
            titulo = fuente_titulo.render("Oscuridad", True, BLANCO)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 60)))

            subt = fuente_subtitulo.render("Evoluciones del Luchador", True, BLANCO)
            pantalla.blit(subt, subt.get_rect(center=(ANCHO//2, 110)))

            # ---- Primera evolución (nivel 10) ----
            txt_prim = fuente_texto.render("Primera evolución (nivel 10)", True, BLANCO)
            pantalla.blit(txt_prim, (40, 170))

            rect_img1 = pygame.Rect(40, 190, 150, 150)  # Imagen Berserker
            pygame.draw.rect(pantalla, BLANCO, rect_img1, 2)
            img1 = IMAGENES["berserker"]
            if img1:
                pantalla.blit(img1, rect_img1.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img1.center))

            txt_ber = fuente_texto.render("Berserker", True, BLANCO)
            pantalla.blit(txt_ber, (220, 200))
            dibujar_barra_bonus(220, 230, "+10 Vitalidad", 10)

            desc_ber = fuente_peque.render("Guerrero desatado con gran resistencia.", True, BLANCO)
            pantalla.blit(desc_ber, (220, 260))

            # ---- Segunda evolución (nivel 20) ----
            txt_seg = fuente_texto.render("Segunda evolución (nivel 20)", True, BLANCO)
            pantalla.blit(txt_seg, (40, 350))

            # Izquierda: Derviche (Oscuridad / Luz)
            rect_img2 = pygame.Rect(40, 370, 150, 150)
            pygame.draw.rect(pantalla, BLANCO, rect_img2, 2)
            img2 = IMAGENES["derviche"]
            if img2:
                pantalla.blit(img2, rect_img2.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img2.center))

            txt_der = fuente_texto.render("Derviche (Osc/Luz)", True, BLANCO)
            pantalla.blit(txt_der, (210, 380))
            dibujar_barra_bonus(210, 410, "+5 Agilidad", 5)
            dibujar_barra_bonus(210, 440, "+10 Vitalidad", 10)

            # Derecha: Puño Mortal (Oscuridad / Oscuridad)
            rect_img3 = pygame.Rect(40, 540, 150, 150)
            pygame.draw.rect(pantalla, BLANCO, rect_img3, 2)
            img3 = IMAGENES["puno_mortal"]
            if img3:
                pantalla.blit(img3, rect_img3.topleft)
            else:
                txt = fuente_peque.render("Sin imagen", True, BLANCO)
                pantalla.blit(txt, txt.get_rect(center=rect_img3.center))

            txt_pm = fuente_texto.render("Puño Mortal (Osc/Osc)", True, BLANCO)
            pantalla.blit(txt_pm, (210, 550))
            dibujar_barra_bonus(210, 580, "+5 Fuerza", 5)
            dibujar_barra_bonus(210, 610, "+10 Agilidad", 10)

            # Botón Volver
            boton_volver.dibujar(pantalla)

        # ------------ ACTUALIZA PANTALLA ------------
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_luchador()
