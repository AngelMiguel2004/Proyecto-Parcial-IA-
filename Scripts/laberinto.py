# Miguel Ángel Jiménez 23-EISN-2-010
import random
from Scripts.numAleatorios import *

# Clase Maze, representa el laberinto del juego
class Maze(object):
    def __init__(self,roomX,roomY):
        # Inicializa el laberinto con la posición de la sala
        self.rmX = roomX
        self.rmY = roomY
        RNG.seed = 0
        self.rmNumber = (self.rmY << 8) + self.rmX
        self.exitDoors = {}
        self.pillars = ""

    # Genera los pilares del laberinto de forma pseudoaleatoria
    def getPillars(self,):
        RNG.seed = self.rmNumber
        #pillars = [[0 for x in range(2)] for x in range(5)]
        pillars = ""
        for row in range(2):
            for col in range(4):
                RNG.getRandomNumber()
                pillarValue = RNG.getRandomNumber()
                walldirection = self.getWall(pillarValue)
                #pillars[row][col] = walldirection
                pillars += walldirection
        self.pillars = pillars
        return pillars

    """
    Convierte el número generado por el generador de números aleatorios
    en una dirección de pared (N, S, E, W).
    """
    def getWall(self, pillarValue):
        # Devuelve la dirección de la pared según los bits bajos del valor
        return {0:"N",1:"S",2:"E",3:"W"}[pillarValue & 0x03]

    # Cambia de sala al salir por una puerta
    def exit(self, door = ""):
        x,y,z = {"S":(0,1,"N"), "N":(0,-1,"S"), "W":(-1,0,"E"), "E":(1,0,"W"), "":(0,0,"")}[door]

        self._exitMazeDoor(self.rmNumber,door)

        # Si no hay puerta de salida, elige una sala aleatoria
        if door == "":
            x = (-1,0,1)[random.randrange(0,3)]
            y = (-1,0,1)[random.randrange(0,3)]
        self.rmX = (self.rmX + x) & 0xFF
        self.rmY = (self.rmY + y) & 0xFF
        self.rmNumber = (self.rmY << 8) + self.rmX

        self._exitMazeDoor(self.rmNumber,z)

    # Marca la puerta de salida usada en la sala
    def _exitMazeDoor(self,room,door):
        exits = ""
        try:
            exits = self.exitDoors.pop(room)
        except:
            pass

        exits = exits + door
        self.exitDoors.setdefault(room,exits)
        pass

    # Devuelve las puertas de salida disponibles en la sala actual
    def getDoors(self):
        doors = ""
        try:
            doors = self.exitDoors.setdefault(self.rmNumber,doors)
        except:
            pass

        #print( self.rmNumber, doors )
        return doors

"""
close door S  roomY--
close door E  roomX--
close door W  roomX++
close door N  roomY++
"""

# Explicación:
# Este bloque de comentarios indica cómo se actualizan las coordenadas de la sala (roomX, roomY)
# cuando se cierra una puerta en una dirección específica:
# - Si se cierra la puerta Sur (S), se decrementa roomY.
# - Si se cierra la puerta Este (E), se decrementa roomX.
# - Si se cierra la puerta Oeste (W), se incrementa roomX.
# - Si se cierra la puerta Norte (N), se incrementa roomY.
# Esto sirve como referencia para la lógica de movimiento entre salas en el laberinto.