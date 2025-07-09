# Miguel Ángel Jiménez
# Miguel Ángel Jiménez 23-EISN-2-010

import pygame, Scripts.spritesheet as spritesheet
from itertools import cycle
from Scripts.constantes import *

# Clase Text, para mostrar texto en pantalla
class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        # Inicializa el texto con fuente, tamaño, mensaje, color y posición
        self.font = pygame.font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, surface):
        # Dibuja el texto en la superficie indicada
        surface.blit(self.surface, self.rect)
        pass

# Clase Score, maneja la puntuación del jugador
class Score(pygame.sprite.Sprite):
    score = 0
    bonuslife = True

    @staticmethod
    def addpoints(points):
        # Suma puntos al marcador y otorga vida extra si corresponde
        Score.score += points
        if Score.score >= BONUS_LIFE_SCORE and Score.bonuslife:
            event = pygame.event.Event(BONUS_LIFE)
            pygame.event.post(event)
            Score.bonuslife = False

    def __init__(self,color):
        # Inicializa el sprite de puntuación
        super().__init__()
        self.scorecolor = color

    def update(self):
        # Actualiza el texto de la puntuación
        tmp = '{:>7}'.format(Score.score)
        text = Text(FONT, 20, tmp, self.scorecolor, 60, SCREEN_HEIGHT - BORDERTHICKNESS - WALLTHICKNESS )
        self.image = text.surface
        self.rect = text.rect

    def draw(self):
        # Método de dibujo (no implementado)
        pass

# Clase Bonus, muestra los puntos de bonificación en pantalla
class Bonus(pygame.sprite.Sprite):
    def __init__(self, color, bonus):
        super().__init__()
        Score.addpoints(bonus)
        bonus = 'BONUS  {:3d}'.format(bonus)
        text = Text(FONT, 20, bonus, color, (SCREEN_WIDTH//5)*2, SCREEN_HEIGHT - BORDERTHICKNESS - WALLTHICKNESS)
        self.image = text.surface
        self.rect = text.rect

    def update(self):
        # No requiere actualización
        pass

    def draw(self):
        # Método de dibujo (no implementado)
        pass

# Clase gameFPS, muestra los cuadros por segundo en pantalla
class gameFPS(pygame.sprite.Sprite):
    clock = 0
    color = BLACK
    displayIterator = cycle(range(2))
    display = next(displayIterator)

    @staticmethod
    def toggleDisplay():
        # Alterna la visualización del FPS
        gameFPS.display = next(gameFPS.displayIterator)

    def __init__(self,color=BLACK):
        super().__init__()
        gameFPS.color = color

    def update(self):
        # Actualiza el texto de FPS
        color = BLACK
        if gameFPS.display == True:
            color = gameFPS.color
        fps = "FPS: {:.2f}".format(gameFPS.clock)
        text = Text(FONT,12,fps,color,SCREEN_WIDTH - 90, SCREEN_HEIGHT - BORDERTHICKNESS)
        self.image = text.surface
        self.rect = text.rect

    def draw(self):
        # Método de dibujo (no implementado)
        pass


