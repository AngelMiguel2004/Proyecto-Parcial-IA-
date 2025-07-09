# Miguel Ángel Jiménez 23-EISN-2-010
# Módulo para manejar hojas de sprites (spritesheets)

import pygame

class spritesheet(object):
    def __init__(self, filename):
        # Carga la imagen de la hoja de sprites
        try:
            self.sheet = pygame.image.load(filename).convert().convert_alpha()
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Carga una imagen específica de un rectángulo dado
    def image_at(self, rectangle, colorkey=None):
        # Carga la imagen desde x, y, ancho, alto
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Carga varias imágenes y las devuelve como una lista
    def images_at(self, rects, colorkey=None):
        # Carga múltiples imágenes, recibe una lista de coordenadas
        return [self.image_at(rect, colorkey) for rect in rects]

    # Carga una tira de imágenes
    def load_strip(self, rect, image_count, colorkey=None):
        # Carga una tira de imágenes y las devuelve como una lista
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)