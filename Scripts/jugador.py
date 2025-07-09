# Miguel Ángel Jiménez 23-EISN-2-010
import pygame, Scripts.spritesheet as spritesheet, random
from pygame.locals import *
from Scripts.constantes import *
from Scripts.animateobj import *
from Scripts.disparos import *

"""
Diccionario de movimientos y disparos del jugador.
Cada valor indica el desplazamiento en x, y y el patrón de animación.
"""

MOV_DICT = {0x00: (0,  0, "still"),
            0x01: (-1,  0, "W"),     # LEFT
            0x02: (1,  0, "E"),      # RIGHT
            0x03: (0,  0, "still"),  # LEFT/RIGHT CANCEL
            0x04: (0, -1, "N"),      # UP
            0x05: (-1, -1, "W"),     # UP & LEFT
            0x06: (1, -1, "E"),      # UP & RIGHT
            0x07: (0, -1, "N"),      # UP LEFT/RIGHT CANCEL
            0x08: (0,  1, "S"),      # DOWN
            0x09: (-1,  1, "W"),     # DOWN & LEFT
            0x0A: (1,  1, "E"),      # DOWN & RIGHT
            0x0B: (0,  1, "S"),      # DOWN LEFT/RIGHT CANCEL
            0x0C: (0,  0, "still"),  # UP/DOWN CANCEL
            0x0D: (-1,  0, "W"),     # LEFT UP/DOWN CANCEL
            0x0E: (1,  0, "E"),      # RIGHT UP/DOWN CANCEL
            0x0F: (0,  0, "still"),  # UP/DOWN LEFT/RIGHT CANCEL
            0x10: (0,  0, "still"),
            0x11: (0,  0, "WW"),     # FACE-LEFT SHOOT-LEFT
            0x12: (0,  0, "EE"),     # FACE-RIGHT SHO0T-RIGHT
            0x13: (0,  0, "still"),
            0x14: (0,  0, "?N"),     # SHOOT-UP
            0x15: (0,  0, "WNW"),    # FACE-LEFT SHOOT-UP/LEFT
            0x16: (0,  0, "ENE"),    # FACE-RIGHT  SHOOT-UP/RIGHT
            0x17: (0,  0, "?N"),     # FACE-???  SHOOT-UP
            0x18: (0,  0, "?S"),     # FACE-???  SHOOT-DOWN
            0x19: (0,  0, "WSW"),    # FACE-LEFT SHOOT-DOWN/LEFT
            0x1A: (0,  0, "ESE"),    # FACE-RIGHT SHOOT-DOWN/RIGHT
            0x1B: (0,  0, "?S"),     # FACE-??? SHOOT-DOWN
            0x1C: (0,  0, "still"),
            0x1D: (0,  0, "WW"),     # FACE-LEFT SHOOT-LEFT
            0x1E: (0,  0, "EE"),     # FACE-RIGHT SHOOT-RIGHT
            0x1F: (0,  0, "still")}


# Clase Player, representa al jugador
class Player(AnimateObj):
    def __init__(self, door, color, filename, rect, count, colorkey=BLACK, scale=2):
        # Inicializa la clase base y carga los sprites del jugador
        super().__init__()
        ss = spritesheet.spritesheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.prvdir = "still"

        self.setcolor(color)

        # Escala y recorta las imágenes del jugador
        for i in range(count):
            image = self.images[i]
            image.set_colorkey(colorkey, RLEACCEL)
            w, h = image.get_size()
            cropped_image = image.subsurface(0, 0, w, h)
            scale_image = pygame.transform.scale(cropped_image, (scale*w, scale*h))
            self.images[i] = scale_image

        self.rect = self.images[0].get_rect()

        # Define los patrones de animación del jugador
        self.addpattern("still", [0])
        self.addpattern("E", [1, 2, 3, 2])  # corriendo hacia la derecha
        self.addpattern("W", [7, 6, 5, 6])
        self.addpattern("N", [1, 2, 3, 2])
        self.addpattern("S", [1, 2, 3, 2])
        self.addpattern("EE", [14])         # disparando hacia la derecha
        self.addpattern("EN", [15])         # disparando hacia arriba derecha
        self.addpattern("ES", [16])         # disparando hacia abajo derecha
        self.addpattern("ESE", [17])        # disparando hacia abajo derecha
        self.addpattern("ENE", [18])        # disparando hacia arriba derecha
        self.addpattern("WW", [19])         # disparando hacia la izquierda
        self.addpattern("WN", [20])         # disparando hacia arriba izquierda
        self.addpattern("WS", [21])         # disparando hacia abajo izquierda
        self.addpattern("WSW", [22])        # disparando hacia abajo izquierda
        self.addpattern("WNW", [23])        # disparando hacia arriba izquierda
        self.addpattern("electrocuting", [10, 11, 12, 13])

        self.setpattern("still")
        self.startposition(door)

    # Establece la posición inicial del jugador según la puerta de entrada
    def startposition(self, door):
        x,y = {"N": (SCREEN_WIDTH//2 - self.rect.width//2, MAZE_YMIN + WALLTHICKNESS*2),
               "S": (SCREEN_WIDTH//2 - self.rect.width//2, MAZE_YMAX - self.rect.height - BORDERTHICKNESS - WALLTHICKNESS*2),
               "E": (MAZE_XMAX - WALLTHICKNESS - self.rect.width*2, MAZE_YMIN + MAZE_HEIGHT//2 - self.rect.height//2),
               "W": (MAZE_XMIN + WALLTHICKNESS + self.rect.width//2, MAZE_YMIN + MAZE_HEIGHT//2 - self.rect.height//2)}[door]

        self.start_x = self.rect.x = x
        self.start_y = self.rect.y = y

    # Actualiza la animación del jugador
    def update(self):
        super().update()

    def draw(self):
        # Método de dibujo (no implementado)
        pass

    # Cambia el patrón de animación a electrocutado
    def electrocute(self):
        self.setpattern("electrocuting")

    # Mueve al jugador según la dirección recibida
    def mov(self, direction):
        x, y, pattern = MOV_DICT[direction]
        self.rect.x += x*2
        self.rect.y += y*2

        event = None
        # Detecta si el jugador sale del laberinto y genera el evento correspondiente
        if self.rect.left <= MAZE_XMIN - WALLTHICKNESS:
            event = pygame.event.Event(PLAYER_EXIT, mazeexit="W")
        elif self.rect.right >= MAZE_XMAX + WALLTHICKNESS:
            event = pygame.event.Event(PLAYER_EXIT, mazeexit="E")
        elif self.rect.top <= MAZE_YMIN - WALLTHICKNESS:
            event = pygame.event.Event(PLAYER_EXIT, mazeexit="N")
        elif self.rect.bottom >= MAZE_YMAX + WALLTHICKNESS:
            event = pygame.event.Event(PLAYER_EXIT, mazeexit="S")

        if event is not None:
            pygame.event.post(event)

        if direction & 0x10:
            pass

        # Determina el patrón de animación según la dirección
        if pattern[0:1] == "?":
            if self.prvdir == "still":
                if random.randrange(0, 1) == 0:
                    pattern = "E" + pattern[1:2]
                else:
                    pattern = "W" + pattern[1:2]
            else:
                pattern = self.prvdir[0:1] + pattern[1:2]

            if pattern in ["NN","SS"]:
                pattern = pattern[-1:]

        self.setpattern(pattern)
        tmpdir = pattern[0:1]
        if tmpdir in ["E","W"]:
            self.prvdir = tmpdir

    # Dispara una bala según el patrón de animación actual
    def fire(self, color, filename):
        FIRE_DICT = {"WN": (0, 0, -1), "EN": (16, 0, -1), "ENE": (4, 0, -2), "EE": (6, 6, -1), "ESE": (0, 0, -2),
                     "ES": (12, 0, -1), "WS": (0, 0, -1), "WSW": (0, 0, -2), "WW": (-2, 6, -1), "WNW": (0, 0, -2)}

        bullet = None
        if self.patternkey != "still":
            if self.patternkey in FIRE_DICT:
                x, y, idx = FIRE_DICT[self.patternkey]
                bullet = PlayerBullet(color, self.patternkey[idx:], self.rect.x + x, self.rect.y + y, filename)
        return bullet

# Clase PlayerBullet, representa la bala disparada por el jugador
class PlayerBullet(Bullet):
    def __init__(self, color, direction, x, y, filename, speed=8, count=1, colorkey=None, scale=2):
        super().__init__(color, direction, x, y, filename, speed=12, count=1, colorkey=BLACK, scale=2)