# Miguel Ángel Jiménez 23-EISN-2-010
import sys
import pygame
from Scripts.constantes import *

# Clase WallObject, representa una pared en el laberinto
class WallObject(pygame.sprite.Sprite):
    def __init__(self, screen, color, rect):
        super().__init__()
        self.screen = screen
        self.color = color
        self.rect = rect.copy()
        self.wallthickness = WALLTHICKNESS

        # Crea una imagen del bloque y la rellena con el color dado
        self.image = pygame.Surface([rect.width,rect.height])
        self.image.fill(color)

    def draw(self):
        # Método de dibujo (no implementado)
        pass
