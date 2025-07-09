# Miguel Ángel Jiménez
# Miguel Ángel Jiménez 23-EISN-2-010

import sys

# --- Comprobación de versión de Python ---
if sys.version_info < (3, 7):
    print("Este juego requiere Python 3.7 o superior.")
    sys.exit(1)

print("¡Bienvenido a Berserk Ejecutando el juego...")

__author__ = 'TerryO'

# Importaciones de módulos y recursos necesarios
import sys, os, platform, pygame
from pygame.locals import *
from Scripts.constantes import *
from Scripts.Enemigo import *
from Scripts.jugador import *
from Scripts.disparos import *
from Scripts.Enemigoflotante import *
from Scripts.laberinto import *
from Scripts.wall import *
from Scripts.vidas import *
from Scripts.record import *
from Scripts.utils import *
from Scripts.grid import *
import itertools

# --- Constantes globales ---
SCREEN_RECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)   # dimensiones de la pantalla

# Lista de claves de imágenes para la caché
IMAGEKEYS = ['player', 'robot', 'otto', 'robotexplode', 'lives', 'bullets', 'icon']

# Diccionario para mapear teclas de dirección a valores binarios
DIRECT_DICT = {K_LEFT : 0x01, K_RIGHT : 0x02, K_UP : 0x04, K_DOWN : 0x08, K_SPACE : 0x10}

# Estados posibles del juego
GAME_STATES = ["HighScores", "Cntrls", "Play"]

screen = None

# Clase que maneja los estados del juego (pantallas)
class GameState:
    def __init__(self):
        # Prepara el entorno de pygame
        os.environ['SDL_VIDEO_CENTERED'] = '1'      # centra la pantalla
        pygame.init()
        pygame.display.set_caption(CAPTION)
        pygame.mouse.set_visible(0)
        pygame.font.init()

        # Inicializa el mixer de pygame para música
        pygame.mixer.init()
        self.load_and_play_music()

        # Obtiene el directorio donde están el juego e imágenes
        path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path)

        # Carga las imágenes (sprites)
        global imagefiles
        imagefiles = {}
        try:
            imagefiles = {key: os.path.join('assets','images', "{}.png".format(key)) for key in IMAGEKEYS}
        except:
            pass

        global screen
        screen = pygame.display.set_mode(SCREEN_RECT.size)

        # Carga el icono de la ventana
        icon = pygame.image.load(imagefiles['icon']).convert_alpha()
        pygame.display.set_icon(icon)

        self.game = None

        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)
    

    # Carga y reproduce música al iniciar el juego
    # Busca archivos de música en la carpeta 'music' y reproduce el primero encontrado
    # Si no se encuentra la carpeta o no hay música, no se reproduce nada
    def load_and_play_music(self):
        """Carga y reproduce la primera música encontrada en la carpeta 'music'."""
        music_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets','music')
        if os.path.isdir(music_folder):
            for file in os.listdir(music_folder):
                if file.lower().endswith(('.mp3', '.ogg', '.wav')):
                    music_path = os.path.join(music_folder, file)
                    try:
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.play(-1)  # Repetir indefinidamente
                        print(f"Reproduciendo música: {file}")
                    except Exception as e:
                        print(f"No se pudo reproducir la música: {e}")
                    break
        else:
            print("Carpeta 'music' no encontrada. No se reproducirá música.")

    # Estado de pantalla de puntajes altos
    def HighScore(self):
        gamestate = "Play"
        keys = highScoresScreen(screen)
        # Asegura que keys sea un dict y contiene la clave K_F1
        if isinstance(keys, dict) and keys.get(K_F1, False):
            gamestate = "Cntrls"
        self.Go(gamestate)

    # Estado de pantalla de controles
    def Cntrls(self):
        gameCntrls(screen)
        self.Go("HighScore")

    # Estado principal de juego
    def Play(self):
        if self.game == None:
            self.game = Game()

        """
         robot color  level   bullet
         DARK YELLOW  0       0
         RED          500     1
         DARK CYAN    1500    2
         GREEN        3K      3
         DARK PURPLE  4.5K    4
         LIGHT YELLOW 6K      5
         WHITE        7.5K    1 *fast bullets
         DARK CYAN    10K     2
         LIGHT PURPLE 11K     3
         GRAY         13K     4
         DARK YELLOW  15K     5
         RED          17K     5
         LIGHT CYAN   19K     5
        """
        # Configuración de colores y dificultad de los robots según el puntaje
        robotcolors = ((YELLOW, False, 0, 500, 5), (RED, True, 1, 1500, 4), (CYAN, True, 2, 3000, 3),
                       (GREEN, True, 3, 4500, 2), (PURPLE, True, 4, 6000, 1), (YELLOW, True, 5, 7500, 1),
                       (WHITE, True, -1, 10000, 1), (LIGHTSKYBLUE, True, -2, 11000, 1), (PURPLE, True, -3, 13000, 1),
                       (GRAY, True, -4, 15000, 1), (YELLOW, True, -5, 17000, 1), (RED, True, -5, 19000, 1),
                       (LIGHTSKYBLUE, True, -5, 999999, 1)
                       )

        # Selecciona la configuración de robots según el puntaje actual
        for color, fire, maxbullets, max_score, frameupdate in robotcolors:
            if  Score.score < max_score:
                break

        self.game.run(color, fire, frameupdate)

        gamestate = "Play"
        if self.game.lives <= 0:
            if gameOver(screen,Score.score):
                gamestate = "HighScore"
            Score.score = 0
            tmp = sys.getrefcount(self.game)
            del self.game
            self.game = None

        self.Go(gamestate)

    # Finaliza el juego
    def Quit(self):
        pygame.quit()
        sys.exit()

    # Cambia de estado del juego
    def Go(self,gamestate):
        if hasattr(self,gamestate):
            state = getattr(self,gamestate)
            state()

# Clase principal del juego, maneja la lógica y los sprites
class Game:
    def __init__(self):
        self.done = False
        self.event_type = None
        self.shotflg = False
        self.keycnt = 0
        self.movdir = 0
        self.maze = Maze(0x53,0x31)   # sala inicial X,Y
        self.mazeexit = None
        self.lives = MAX_LIVES
        self.bonuspts = None
        self.keys = pygame.key.get_pressed()

        # Detecta joysticks conectados (opcional, para referencia)
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)

    # Procesa los eventos de pygame
    def process_events(self):
        for e in pygame.event.get():
            if e.type == QUIT or self.keys[K_ESCAPE]:
                self.done = True
                pygame.quit()
                sys.exit()
                break
            elif e.type == SPAWN_OTTO:
                self.spawnOtto()
            elif e.type == ROBOT_ACTIVE:
                self.robotActive()
            elif e.type == PLAYER_EXIT:
                self.playerExit(e.mazeexit)
            elif e.type == BONUS_POINTS:
                self.bonusPoints(e.bonuspoints)
            elif e.type == BONUS_LIFE:
                self.bonusLife()
            elif e.type == PLAYER_ELECTROCUTED:
                self.playerElectrocuted()
            elif e.type in (KEYUP,KEYDOWN):
                self.keys = pygame.key.get_pressed()
                if self.keys[K_F1]:
                    gamePause(screen)
                if self.keys[K_F2]:
                    gameFPS.toggleDisplay()
                if e.type == KEYDOWN:
                    self.keycnt += 1
                    if e.key in DIRECT_DICT:
                        self.movdir |= DIRECT_DICT[e.key]
                elif e.type == KEYUP:
                    self.keycnt -= 1
                    if e.key in DIRECT_DICT:
                        self.movdir &= ~DIRECT_DICT[e.key]

                # Verifica si el modificador izquierdo está presionado
                if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    pass
            elif e.type == pygame.JOYAXISMOTION:
                # Ejes: e.axis (0=izq/der, 1=arriba/abajo), e.value (-1 a 1)
                if e.axis == 0:  # Horizontal
                    if e.value < -0.5:
                        self.movdir |= 0x01  # Izquierda
                        self.movdir &= ~0x02
                    elif e.value > 0.5:
                        self.movdir |= 0x02  # Derecha
                        self.movdir &= ~0x01
                    else:
                        self.movdir &= ~(0x01 | 0x02)
                elif e.axis == 1:  # Vertical
                    if e.value < -0.5:
                        self.movdir |= 0x04  # Arriba
                        self.movdir &= ~0x08
                    elif e.value > 0.5:
                        self.movdir |= 0x08  # Abajo
                        self.movdir &= ~0x04
                    else:
                        self.movdir &= ~(0x04 | 0x08)
            elif e.type == pygame.JOYBUTTONDOWN:
                if e.button == 0:  # Botón A (disparo)
                    self.movdir |= 0x10
                elif e.button == 1:  # Botón B (también disparo/acción)
                    self.movdir |= 0x10
            elif e.type == pygame.JOYBUTTONUP:
                if e.button == 0:
                    self.movdir &= ~0x10
                elif e.button == 1:
                    self.movdir &= ~0x10

    # Lógica cuando el jugador es electrocutado
    def playerElectrocuted(self):
        pygame.time.set_timer(PLAYER_ELECTROCUTED,0) # desactiva el temporizador
        self.maze.exit()
        self.mazeexit = None
        self.done = True
        for obj in self.sprites:
            if type(obj) is Lives:
                if obj.life == self.lives:
                    obj.kill()
                    break
        self.lives -= 1
        if self.lives <= 0:
            for obj in self.wall2grp:
                obj.kill()
            self.player.kill()
            self.refreshSprites()
        else:
            screenMazeClear(screen)
        self.spriteCleanUp()

    # Ejecuta la animación de electrocutar al jugador
    def electrocute(self):
        if self.player.patternkey != "electrocuting":
            # desactiva temporizadores activos
            pygame.time.set_timer(SPAWN_OTTO,0)
            pygame.time.set_timer(ROBOT_ACTIVE,0)

            # pone al jugador en modo electrocutado
            self.player.electrocute()
            pygame.time.set_timer(PLAYER_ELECTROCUTED, 1000)  # 1 segundo

            # los robots dejan de disparar
            Robot.laserEnable = False

            for obj in self.wall2grp:
                obj.kill()

    # Lógica cuando un robot explota
    def robot_explode(self,robot):
        # callback después de la animación de explosión
        def callback(robot):
            robot.kill()        # elimina el sprite de explosión

        explode = RobotExplode(robot, callback, imagefiles['robotexplode'], ROBOTEXPLODE_RECT, ROBOTEXPLODE_SPRITES )
        self.sprites.add(explode)
        robot.kill()            # elimina el sprite del robot
        self.score.addpoints(ROBOT_KILL_POINTS)

    # Suma puntos de bonificación
    def bonusPoints(self, bonus):
        points = Bonus(GRAY, bonus)
        self.sprites.add(points)

    # Otorga una vida extra
    def bonusLife(self):
        self.lives += 1
        life = Lives(self.lives, imagefiles['lives'], LIVES_RECT, GREEN)
        self.sprites.add(life)

    # Verifica todas las colisiones del juego
    def check_collisions(self):
        # verifica colisión de balas con robots/otto
        collidedict = pygame.sprite.groupcollide(self.bullets, Robot.getGroup(), False, False)
        if collidedict:
            for bullet in collidedict.keys():
                bullet.kill()
                for value in collidedict.values():
                    for robot in value:
                        if type(robot) is Robot:
                            self.robot_explode(robot)
                        else:
                            pass

        # verifica colisión de balas con el jugador
        collidedict = pygame.sprite.groupcollide(self.bullets, self.playergrp, False, False)
        if collidedict:
            for bullet in collidedict.keys():
                if type(bullet) is RobotBullet:
                    bullet.kill()
                    for value in collidedict.values():
                        for player in value:
                            if type(player) is Player:
                                self.electrocute()
                                return
                            else:
                                pass

        # verifica colisión entre balas
        combo = list(itertools.combinations(self.bullets, 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b):
                a.kill()    # elimina del grupo
                b.kill()

        # verifica colisión de balas con paredes
        for bullet in self.bullets:
            if pygame.sprite.spritecollideany(bullet, self.wallgrp):
                bullet.kill()

        # verifica colisión de robots con paredes
        collidedict = pygame.sprite.groupcollide(Robot.getGroup(), self.wallgrp, False, False)
        if collidedict:
            for robot in collidedict.keys():
                if type(robot) is Robot:
                    self.robot_explode(robot)

        # elimina viejas advertencias de pared
        for x in self.wall2grp:
            x.kill()

        # advierte al jugador si está cerca de una pared resaltando el área de la pared
        r = self.player.rect.copy()
        self.player.rect = self.player.rect.inflate(16, 16)
        collide_list = pygame.sprite.spritecollide(self.player, self.wallgrp, False)
        for collide in collide_list:
            c = collide.rect.clip(self.player.rect)
            if collide.rect.w == 8:
                c.left = collide.rect.left
                c.w = 8
            else:
                c.top = collide.rect.top
                c.h = 8
            wall2 = WallObject(screen, GREEN, c)
            self.sprites.add(wall2)
            self.wall2grp.add(wall2)

        self.player.rect = r.copy()

        # verifica colisión del jugador con paredes
        if pygame.sprite.spritecollideany(self.player, self.wallgrp):
            self.electrocute()

        # verifica colisión del jugador con robots
        collide = pygame.sprite.spritecollideany(self.player, Robot.getGroup())
        if collide:
            if type(collide) is Robot:
                self.robot_explode(collide)
            self.electrocute()

        # verifica colisión entre robots
        combo = list(itertools.combinations(Robot.getGroup(), 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b):
                if type(a) is Robot:
                    self.robot_explode(a)
                if type(b) is Robot:
                    self.robot_explode(b)

    # Crea el enemigo Otto
    def spawnOtto(self):
        pygame.time.set_timer(SPAWN_OTTO,0) # desactiva temporizador
        otto = Otto(self.levelcolor, self.player, imagefiles['otto'], OTTO_RECT, OTTO_SPRITES )
        self.sprites.add(otto)
        Robot.getGroup().add(otto)

    # Activa los robots después de cierto tiempo
    def robotActive(self):
        pygame.time.set_timer(ROBOT_ACTIVE,0) # desactiva temporizador

        # activa los robots
        for robot in Robot.getGroup():
            if type(robot) == Robot:
                robot.active = True

    # Lógica cuando el jugador sale del laberinto
    def playerExit(self,mazeexit):
        pygame.time.set_timer(SPAWN_OTTO,0)     # desactiva temporizadores activos
        pygame.time.set_timer(ROBOT_ACTIVE,0)
        screenScroll(screen,mazeexit,self.levelcolor)
        self.maze.exit(mazeexit)
        self.mazeexit = mazeexit
        self.done = True

        for obj in self.sprites:
            if type(obj) == Bonus:
                obj.kill()
                break

        self.spriteCleanUp()

    # Limpia todos los sprites y grupos
    def spriteCleanUp(self):
        # limpia los sprites
        self.bullets.empty()
        self.wallgrp.empty()
        self.wall2grp.empty()
        self.playergrp.empty()
        self.explodegrp.empty()
        self.lifegrp.empty()
        Robot.getGroup().empty()
        self.sprites.empty()
        del self.bullets
        del self.wallgrp
        del self.wall2grp
        del self.playergrp
        del self.explodegrp
        del self.lifegrp
        del self.sprites
        del self.score
        del self.gamefps

    # Ejecuta el bucle principal del juego
    def run(self, levelcolor, robotLaser, frameupdate):
        self.levelcolor = levelcolor

        # mantiene el seguimiento de los sprites
        self.explodegrp = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        Bullet.bulletcnt = BULLETS_MAX
        self.wallgrp = pygame.sprite.Group()
        self.wall2grp = pygame.sprite.Group()
        self.playergrp = pygame.sprite.GroupSingle()

        self.sprites = pygame.sprite.LayeredUpdates(self.wallgrp, self.playergrp,self.explodegrp)
        self.lifegrp = pygame.sprite.Group()

        door = {"E":"W","W":"E","N":"S","S":"N"}.get(self.mazeexit,"W")
        self.player = Player(door, PLAYER_COLOR, imagefiles['player'], PLAYER_RECT, PLAYER_SPRITES)
        self.sprites.add(self.player)
        self.playergrp.add(self.player)

        self.score = Score(GREEN)
        self.sprites.add(self.score)

        self.gamefps = gameFPS(GREEN)
        self.sprites.add(self.gamefps)

        self.Arena(screen,self.maze,levelcolor)
        grid = Grid(40, 22, self.maze.pillars)

        def robotCallBack(cmd, *argv):
            if cmd == "FIRE":
                bullet = argv[0]
                self.sprites.add(bullet)
                self.bullets.add(bullet)

        # crea los robots
        Robot.newLevel(robotLaser)
        for i in range(random.randrange(MIN_ROBOTS,MAX_ROBOTS)):
            robot = Robot(levelcolor, robotCallBack, self.player, grid, self.maze.pillars, self.wallgrp, imagefiles, ROBOT_RECT, ROBOT_SPRITES, frameupdate )
            self.sprites.add(robot)

        # crea las vidas
        for i in range(2, self.lives+1):
            life = Lives(i, imagefiles['lives'], LIVES_RECT, GREEN)
            self.sprites.add(life)

        # mantiene el seguimiento del tiempo
        clock = pygame.time.Clock()

        self.timer = pygame.time.get_ticks()
        self.cooldown = 600

        # establece el evento del temporizador para Otto
        pygame.time.set_timer(SPAWN_OTTO,1500*Robot.robotcnt) # 1.5seg/robot

        # establece el evento del temporizador para el movimiento del robot
        pygame.time.set_timer(ROBOT_ACTIVE,3000) # 3seg

        # bucle del laberinto
        self.done = False
        while not self.done:
            now = pygame.time.get_ticks()
            self.process_events()

            if self.done:
                break

            gameFPS.clock = clock.get_fps()

            if self.player.patternkey != "electrocuting":
                self.player.mov(self.movdir)

                if self.movdir & 0x10:
                    # dispara el láser solo si ha pasado 0.6 seg de enfriamiento
                    if now - self.timer > self.cooldown:
                        bullet = self.player.fire(levelcolor, imagefiles['bullets'])
                        if bullet != None:
                            self.sprites.add(bullet)
                            self.bullets.add(bullet)
                            self.timer = now

            self.check_collisions()
            self.refreshSprites()
            clock.tick(FPS)     # mantiene la tasa de cuadros

    # Refresca y dibuja los sprites en pantalla
    def refreshSprites(self):
        # usado para borrar el sprite
        def clear_callback(surf, rect):
            surf.fill(BLACK, rect)
            pass

        # borra posiciones anteriores
        self.sprites.clear(screen, clear_callback)

        # actualiza los sprites
        self.sprites.update()

        # debugAIgrid()

        # redibuja los sprites
        dirty = self.sprites.draw(screen)
        pygame.display.update(dirty)

    # Dibuja la cuadrícula de IA para depuración
    def debugAIgrid(self):
        # código de depuración para la cuadrícula de IA del robot
        for x in range(MAZE_XMIN-4,MAZE_XMAX+16,16):
        #for x in range(MAZE_XMIN, MAZE_XMAX,24):
            for y in range(MAZE_YMIN+8,MAZE_YMAX ,22):
            #for y in range(MAZE_YMIN, MAZE_YMAX,24):
                pygame.draw.line(screen, RED, (x, y), (MAZE_XMAX, y), (1))
                pygame.draw.line(screen, RED, (x, y), (x, MAZE_YMAX), (1))

    # Construye las paredes del laberinto y los bordes
    def Arena(self, screen, maze, doorcolor=None):
        # bordes: oeste arriba, oeste abajo, este arriba, este abajo, izquierda arriba, izquierda abajo, derecha arriba, derecha abajo
        borders = [
            (BORDER_XMIN, BORDER_YMIN, WALLTHICKNESS, BORDER_VSEGMENT + WALLTHICKNESS),
            (BORDER_XMIN, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*2, WALLTHICKNESS, BORDER_VSEGMENT),
            (BORDER_XMAX, BORDER_YMIN, WALLTHICKNESS, BORDER_VSEGMENT + WALLTHICKNESS),
            (BORDER_XMAX, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*2, WALLTHICKNESS, BORDER_VSEGMENT),
            (BORDER_XMIN, BORDER_YMIN, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*3, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*3, BORDER_YMIN, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*3, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*3, BORDER_HSEGMENT*2 + WALLTHICKNESS, WALLTHICKNESS)
        ]

        for left,top,width,height in borders:
            wall = WallObject(screen, WALL_COLOR, pygame.Rect(int(left),int(top),int(width),int(height)))
            self.sprites.add(wall)
            self.wallgrp.add(wall)

        PILLAR_HSEGMENT = BORDER_HSEGMENT
        PILLAR_VSEGMENT = BORDER_VSEGMENT
        HPILLAR = (PILLAR_HSEGMENT, WALLTHICKNESS)
        VPILLAR = (WALLTHICKNESS, PILLAR_VSEGMENT)

        pillars = maze.getPillars()
        i = 0
        for p in pillars[:]:
            fx,fy  = {0:(1,1), 1:(2,1), 2:(3,1), 3:(4,1), 4:(1,2), 5:(2,2), 6:(3,2), 7:(4,2)}[i]
            x = MAZE_XMIN + PILLAR_HSEGMENT*fx
            y = MAZE_YMIN + PILLAR_VSEGMENT*fy
            x_offset,y_offset,w,h = 0,0,0,0

            if p == "N":
                w,h = VPILLAR
                h += {1:WALLTHICKNESS}.get(i,0)
                y_offset -= PILLAR_VSEGMENT
                y_offset += {1:-WALLTHICKNESS}.get(i,0)

            elif p == "S":
                w,h = VPILLAR
                h += {5:WALLTHICKNESS}.get(i,0)

            elif p == "E":
                w,h = HPILLAR
                w += WALLTHICKNESS
                y_offset += {0:-WALLTHICKNESS,1:-WALLTHICKNESS,2:-WALLTHICKNESS,3:-WALLTHICKNESS}.get(i,0)

            elif p == "W":
                w,h = HPILLAR
                w += WALLTHICKNESS
                x_offset -= PILLAR_HSEGMENT
                y_offset += {0:-WALLTHICKNESS,1:-WALLTHICKNESS,2:-WALLTHICKNESS,3:-WALLTHICKNESS}.get(i,0)

            else:
                    pass
            i += 1

            if p != "O":
                rect = pygame.Rect(int(x+x_offset), int(y+y_offset), int(w), int(h))
                mazewall = WallObject(screen, WALL_COLOR, rect)
                self.sprites.add(mazewall)
                self.wallgrp.add(mazewall)

        # NOTA: la puerta de salida está opuesta a donde el jugador salió del laberinto
        x,y,w,h = 0,0,0,0
        doors = maze.getDoors()
        for door in doors[:]:
            if door in ("E", "W"):
                y = BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT
                w,h = WALLTHICKNESS//2, BORDER_VSEGMENT
                if door == "E":
                    x = MAZE_XMAX + WALLTHICKNESS//4
                else:
                    x = BORDER_XMIN + WALLTHICKNESS//4
            elif door in ("N", "S"):
                x = BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*2
                w,h = BORDER_HSEGMENT, WALLTHICKNESS//2
                if door == "N":
                    y = BORDER_YMIN + WALLTHICKNESS//4
                else:
                    y = MAZE_YMAX + WALLTHICKNESS//4
            rect = pygame.Rect(int(x), int(y), int(w), int(h))
            mazewall = WallObject(screen, doorcolor, rect)
            self.sprites.add(mazewall)
            self.wallgrp.add(mazewall)
