# Miguel Ángel Jiménez
# Miguel Ángel Jiménez 23-EISN-2-010
import pygame, Scripts.spritesheet as spritesheet
from Scripts.constantes import *
from Scripts.animateobj import *

# Clase Lives, representa las vidas del jugador en pantalla
class Lives(pygame.sprite.Sprite):
    def __init__(self, life, filename, rect, color, colorkey=BLACK, scale=3):
        # Inicializa el sprite de vida
        super(Lives,self).__init__()
        ss = spritesheet.spritesheet(filename)
        image =  ss.image_at(rect)
        image.set_colorkey(colorkey)
        w,h = image.get_size()
        cropped_image = image.subsurface(0,0,w,h)
        scale_image = pygame.transform.scale(cropped_image,(scale*w,scale*h))
        self.image = scale_image
        self.rect = self.image.get_rect()
        self.life = life

        # Calcula la posición de la vida en pantalla según el número de vidas
        self.rect.x = SCREEN_WIDTH/4 + self.rect.width*{3:1, 4:2, 5:3, 6:4, 7:5}.get(life,0)
        self.rect.y = SCREEN_HEIGHT - BORDERTHICKNESS - self.rect.height/2

        self.color = color
        # Cambia el color blanco de la imagen por el color de la vida
        pixelArray = pygame.PixelArray(self.image)
        pixelArray.replace(WHITE,color)

    def update(self):
        # No requiere actualización
        pass

    def draw(self):
        # Método de dibujo (no implementado)
        pass
