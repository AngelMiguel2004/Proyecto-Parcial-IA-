# Miguel Ángel Jiménez 23-EISN-2-010
import pygame, Scripts.spritesheet as spritesheet, random
from pygame.locals import *
from Scripts.constantes import *
from Scripts.animateobj import *
import Scripts.jugador as jugador
from Scripts.disparos import *
from Scripts.grid import *
import math
import cmath    # Números complejos
import itertools

# Clase Robot, representa a los robots enemigos del juego
class Robot(AnimateObj):
    # Grupo de sprites de robots y contadores globales
    grp = pygame.sprite.Group()
    killcnt = 0
    robotcnt = 0
    laserEnable = False

    @staticmethod
    def getGroup():
        # Devuelve el grupo de robots
        return Robot.grp

    @staticmethod
    def killCount():
        # Devuelve el número de robots eliminados
        return Robot.killcnt

    @staticmethod
    def robotCount():
        # Devuelve el número total de robots
        return Robot.robotcnt

    @staticmethod
    def newLevel(laser):
        # Inicializa los contadores para un nuevo nivel
        Robot.robotcnt = 0
        Robot.killcnt = 0
        Robot.laserEnable = laser

    @staticmethod
    def robotCollision(robot):
        # Verifica colisiones entre robots
        combo = list(itertools.combinations(Robot.getGroup(), 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b) == True:
                if a in Robot.getGroup():
                    if type(a) is Robot:
                        return True
                if b in Robot.getGroup():
                    if type(b) is Robot:
                        return True

        # Verifica colisión de un nuevo robot con los existentes
        collidelist = pygame.sprite.spritecollide(robot, Robot.getGroup(), False)
        for collide in collidelist:
            if type(collide) is not jugador.Player:
                robot.player.electrocute()
                break
            else:
                pass

    def __init__(self, color, cbRobot, player, grid, pillars, walls, imagefiles, rect, count, frame = 5, colorkey=BLACK, scale=2):
        # Inicializa el robot, carga sprites y lo agrega al grupo
        super().__init__()
        ss = spritesheet.spritesheet(imagefiles['robot'])
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frameupdate = self.frame = frame
        self.cbRobot = cbRobot
        self.imagefiles = imagefiles
        self.active = False
        self.pillars = pillars
        self.cellX = 0
        self.cellY = 0
        self.grid = grid

        # Escala y recorta las imágenes del robot
        for i in range(count):
            image = self.images[i]
            image.set_colorkey(colorkey, RLEACCEL)
            w,h = image.get_size()
            cropped_image = image.subsurface(0,0,w,h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w,scale*h))
            self.images[i] = scale_image

        self.setcolor(color)

        self.rect = self.images[0].get_rect()

        # Define los patrones de animación del robot
        self.addpattern("roving_eye", [0,1,2,1,0,5,4,5])
        self.addpattern("east", [7,6,6])
        self.addpattern("south", [0,8,0,9])
        self.addpattern("west", [10,11,11])
        self.addpattern("north", [12,13,12,14])
        self.setpattern("roving_eye")

        self.reset(walls,grid)
        self.player = player

        self.timer = pygame.time.get_ticks()
        self.cooldown = 600
        Robot.grp.add(self)
        Robot.robotcnt += 1

    def reset(self,walls,grid):
        # Coloca el robot en una posición válida del laberinto
        w,h = self.rect.width, self.rect.height
        self.rect.width *= 2
        self.rect.height *= 2
        while True:
            rx = random.randrange(1,38)
            ry = random.randrange(1,21)

            # Evita colocar el robot en posiciones prohibidas
            if rx in (7,8,15,16,23,24,31,32):
                continue
            if ry in (6,7,14,15):
                continue
            x,y = grid.getScreenCoor(rx, ry)

            cell = grid.getCell(rx,ry)
            if cell.reachable == False:
                continue

            cells = grid.get_adjacent_cells(cell)
            for adjcell in cells:
                if adjcell.reachable == False:
                    cell = None
                    break
            if cell is None:
                continue

            # Evita colocar el robot cerca de la posición inicial del jugador
            if grid.getQuadrant(x,y) in ((2,0),(0,1),(4,1),(2,2)):
                continue

            self.rect.x = x
            self.rect.y = y

            # Evita colisiones con otros robots
            if pygame.sprite.spritecollideany(self, Robot.getGroup()):
                continue

            cell.reachable = False
            self.cellX = rx
            self.cellY = ry

            break

        self.rect.width = w
        self.rect.height = h

        # Selecciona una imagen aleatoria para iniciar la animación
        self.index = random.randrange(len(self.pattern))

    def kill(self):
        # Elimina el robot y actualiza el contador de muertes
        super().kill()
        if type(self) == Robot:
            Robot.killcnt += 1

            # Otorga puntos extra si se eliminan todos los robots
            if Robot.killcnt == Robot.robotcnt:
                bonus = 10 * Robot.killcnt
                event = pygame.event.Event(BONUS_POINTS, bonuspoints = bonus)
                pygame.event.post(event)
            elif (Robot.robotcnt - Robot.killcnt) <= 2:
                # Acelera los robots cuando quedan dos o menos
                for robot in Robot.getGroup():
                    if type(robot) is Robot:
                        if robot.frameupdate >= 2:
                            robot.frameupdate -= 1

    def update(self):
        # Actualiza la animación y el movimiento del robot
        self.frame -= 1
        if self.frame == 0:
            self.frame = self.frameupdate
            super().update()

            deltaX, deltaY = 0,0

            if self.active:
                rx, ry = self.grid.getCellCoor(self.rect.x, self.rect.y)
                if rx == self.cellX and ry == self.cellY:
                    px, py = self.grid.getCellCoor(self.player.rect.centerx,self.player.rect.centery)
                    if rx != px or ry != py:
                        maze = AStar()
                        maze.init_grid(self.grid,(rx,ry),(px,py))
                        path = maze.solve()

                        if path is not None:
                            rx,ry = path.pop(1)
                            self.cellX = rx
                            self.cellY = ry

                        del maze
                else:
                    rx = self.cellX
                    ry = self.cellY

                rx,ry = self.grid.getScreenCoor(rx, ry)
                waypoint = complex(rx,ry)
                robot = complex(self.rect.x, self.rect.y)
                cc = waypoint - robot

                sign = lambda x: (x > 0) - (x < 0)
                deltaX = sign(int(cc.real))*2
                self.rect.x += deltaX
                deltaY = sign(int(cc.imag))*2
                self.rect.y += deltaY

            # Determina el patrón de animación según la dirección
            pattern = "roving_eye"
            if (deltaX == 0) & (deltaY == 0):
                pattern = "roving_eye"
            elif deltaX > 0:
                pattern = "east"
            elif deltaX < 0:
                pattern = "west"
            elif deltaY < 0:
                pattern = "north"
            elif deltaY > 0:
                pattern = "south"

            if pattern != self.patternkey:
                self.setpattern(pattern)

            # Dispara láser si el cooldown ha pasado
            now = pygame.time.get_ticks()
            if now - self.timer > self.cooldown:
                if Robot.laserEnable:
                    self.shoot()
                self.timer = now

    def sameCell(self):
        # Verifica si el robot y el jugador están en la misma celda
        bRet = False
        robotCell = self.getCell(self.rect)
        playerCell = self.getCell(self.player.rect)
        if robotCell == playerCell:
            bRet = True
        return bRet

    def sameRow(self):
        # Verifica si el robot y el jugador están en la misma fila
        bRet = False
        robotRow = self.getRow(self.rect)
        playerRow = self.getRow(self.player.rect)
        if robotRow == playerRow:
            bRet = True
        return bRet

    def sameCol(self):
        # Verifica si el robot y el jugador están en la misma columna
        bRet = False
        robotCol = self.getCol(self.rect)
        playerCol = self.getCol(self.player.rect)
        if robotCol == playerCol:
            bRet = True
        return bRet

    def getRow(self, rect):
         # Calcula la fila del rectángulo
         return (rect.y - MAZE_YMIN)/BORDER_VSEGMENT

    def getCol(self, rect):
        # Calcula la columna del rectángulo
        return (rect.x - MAZE_XMIN)/BORDER_HSEGMENT

    def getCell(self, rect):
        # Calcula la celda del rectángulo
        col = (rect.x - MAZE_XMIN)/BORDER_HSEGMENT
        row = (rect.y - MAZE_YMIN)/BORDER_VSEGMENT
        return (row*5)+col

    def getAngle(self, x1, y1, x2, y2):
        # Devuelve el ángulo entre dos puntos (en grados)
        rise = y1 - y2
        run = x1 - x2
        angle = math.atan2(run, rise)
        angle = angle * (180 / math.pi)
        return angle

    # Los robots disparan si están alineados con el jugador en alguna de las 8 direcciones
    def shoot(self):
        direction = None
        # Detecta alineación horizontal
        if (self.rect.centery >= self.player.rect.top) and (self.rect.centery <= self.player.rect.bottom):
            direction = ("W", "E")[self.rect.centerx <= self.player.rect.centerx]
        # Detecta alineación vertical
        elif (self.rect.centerx >= self.player.rect.left) and (self.rect.centerx <= self.player.rect.right):
            direction = ("N", "S")[self.rect.centery <= self.player.rect.centery]
        # Detecta alineación diagonal (comentado)
        """
        if abs(self.rect.centerx - self.player.rect.centerx) == abs(self.rect.centery - self.player.rect.centery):
            if self.rect.centery <= self.player.rect.centery:
                direction = ("SE","SW")[self.rect.centerx >= self.player.rect.centerx]
            else:
                direction = ("NE","NW")[self.rect.centerx >= self.player.rect.centerx]
        """
        if direction is None:
            angle = self.getAngle(self.rect.centerx, self.rect.centery, self.player.rect.centerx, self.player.rect.centery)
            if (angle >= 35.0) and (angle <= 55.0):
                direction = "NW"
            elif (angle >= 125.0) and (angle <= 145.0):
                direction = "SW"
            elif (angle >= -145.0) and (angle <= -125.0):
                direction = "SE"
            elif (angle >= -55.0) and (angle <= -35.0):
                direction = "NE"

        self.fire(direction)

    def fire(self,direction):
        # Dispara una bala en la dirección indicada
        x,y = 0,0
        if self.patternkey == "east":
            x, y = {"NE":(10,-10), "E":(8,0), "SE":(10,0)}.get(direction,(0,0))
        elif self.patternkey == "west":
            x, y = {"SW":(-20,0), "W":(-20,0), "NW":(-20,-10)}.get(direction,(0,0))
        elif self.patternkey in ("north","south"):
            x, y = {"N":(8,-20),"S":(8,6)}.get(direction,(0,0))

        if (x != 0) or (y != 0):
            bullet = RobotBullet(self.color, direction, self.rect.centerx + x, self.rect.centery + y, self.imagefiles['bullets'] )
            if bullet is not None:
                if self.cbRobot is not None:
                    self.cbRobot("FIRE", bullet)

    def draw(self):
        # Método de dibujo (no implementado)
        pass

    def explode(self):
        # Método para explotar el robot (no implementado)
        pass

# Clase RobotBullet, representa la bala disparada por el robot
class RobotBullet(Bullet):
    def __init__(self, color, direction, x, y, filename, speed=8, count=1, colorkey=None, scale=2):
        super().__init__(color, direction, x, y, filename, speed=4, count=1, colorkey=BLACK, scale=2)

# Clase RobotExplode, animación de explosión del robot
class RobotExplode(AnimateObj):
    def __init__(self, robot, cbExplode, filename, rect, count, colorkey=BLACK, scale=2):
        super().__init__(cbExplode)
        ss = spritesheet.spritesheet(filename)
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frame = 10

        # Escala y recorta las imágenes de la explosión
        for i in range(count):
            image = self.images[i]
            image.set_colorkey(colorkey)  # negro es transparente
            w,h = image.get_size()
            cropped_image = image.subsurface(0,0,w,h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w,scale*h))
            self.images[i] = scale_image

        self.rect = self.images[0].get_rect()
        self.rect.x = robot.rect.x
        self.rect.y = robot.rect.y
        self.setcolor(robot.color)

        self.addpattern("explode", [0,1,2])
        self.setpattern("explode")
        Robot.grp.add(self)

    def update(self):
        # Actualiza la animación de explosión
        self.frame -= 1
        if self.frame == 0:
            self.frame = 5
            super().update()

    def draw(self):
        # Método de dibujo (no implementado)
        pass