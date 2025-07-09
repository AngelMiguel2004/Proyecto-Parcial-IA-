# Miguel Ángel Jiménez 23-EISN-2-010
import pygame, Scripts.spritesheet as spritesheet, random
from Scripts.constantes import *
from Scripts.animateobj import *
import Scripts.jugador as jugador
import cmath

import time
import math

# Clase Otto, representa al enemigo Otto en el juego
class Otto(AnimateObj):
    def __init__(self, color, player, filename, rect, count, colorkey=BLACK, scale=2):
        # Inicializa la clase base y carga los sprites de Otto
        super().__init__(self.ottocb)
        ss = spritesheet.spritesheet(filename)
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frame = 15
        self.moveTime = 400
        self.timer = pygame.time.get_ticks()

        self.setcolor(color)

        # Escala y recorta las imágenes de Otto
        for i in range(count):
            image = self.images[i]
            w,h = image.get_size()
            cropped_image = image.subsurface(0, 0, w, h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w, scale*h))
            self.images[i] = scale_image

        self.rect = self.images[0].get_rect()

        # Otto inicia en la posición inicial del jugador
        self.rect.x = player.start_x
        self.rect.y = player.start_y

        # Define los patrones de animación de Otto
        self.addpattern("spawn",[0,1,3,4])
        self.addpattern("otto", [4])
        self.setpattern("spawn")

        self.player = player

        self.step = 0
        self.dir = 2
        self.y = self.rect.y

    # Callback para cambiar el patrón de animación a "otto"
    def ottocb(self, *args):
        self.setpattern("otto")
        self.callback = None

    # Actualiza la posición y animación de Otto
    def update(self):
        self.frame -= 1
        if self.frame == 0:
            self.frame = 5
            # Actualiza el sprite
            super().update()

            # Movimiento de Otto hacia el jugador
            if self.patternkey == "otto":
                player_c = complex(self.player.rect.centerx, self.player.rect.centery)
                otto = complex(self.rect.centerx, self.rect.centery)
                cc = player_c - otto

                sign = lambda x: (x > 0) - (x < 0)

                self.rect.x += 3*sign(int(cc.real))
                self.y += 3*sign(int(cc.imag))

        self.bounce()
        self.rect.y = self.y + self.step

    def draw(self, *args):
        # Método de dibujo (no implementado)
        pass

    def voffset(self):
        # Método de desplazamiento vertical (no implementado)
        offset = 0
        pass

    # Hace que Otto rebote verticalmente
    def bounce(self):
        AMPLITUDE = 50
        self.step += self.dir
        if self.step >= AMPLITUDE:
            self.dir *= -1
            self.step += self.dir
        if self.step <= 0:
            self.dir *= -1
            self.step += self.dir