# Miguel Ángel Jiménez
# Miguel Ángel Jiménez 23-EISN-2-010

import sys
import pygame
from pygame.locals import *
from Scripts.constantes import *
from operator import itemgetter
import pickle

# Muestra la pantalla de Game Over y gestiona si el jugador entra al Hall of Fame
def gameOver(screen, score):
    bRet = False
    hs = getHighScores()
    if 0 <= hs.__len__() < 10:
        if score > 0:
            hallOfFame(screen, hs, score)
            bRet = True
        else:
          _gameOver(screen)
    else:
        for (name,topscore) in hs:
            if score > topscore:
                hallOfFame(screen, hs, score)
                bRet = True
                break
        else:
            _gameOver(screen)
    return bRet

# Muestra el mensaje de Game Over y espera a que el usuario presione una tecla
def _gameOver(screen):
    _gameWait(screen, "JUEGO TERMINADO", "Presione BARRA ESPACIADORA para iniciar", K_SPACE)

# Pausa el juego y espera a que el usuario presione F1 para continuar
def gamePause(screen):
    _gameWait(screen, "JUEGO EN PAUSA", "Presione F1 para continuar", K_F1)

# Muestra un mensaje en pantalla y espera a que el usuario presione una tecla específica
def _gameWait(screen, msg, submsg, key):
    font_path = FONT_PATH
    font_size = 32
    fontObj = pygame.font.Font(font_path, font_size)
    txt = fontObj.render(msg, 1, GREEN)
    width = txt.get_width()
    height = txt.get_height()
    screen.blit(txt, (MAZE_CENTERX - width//2, MAZE_CENTERY - height//2))

    font_size = 10
    fontObj = pygame.font.Font(font_path, font_size)
    txt = fontObj.render(submsg, 1, GREEN)
    width = txt.get_width()
    h = height
    height = txt.get_height()
    screen.blit(txt, (MAZE_CENTERX - width//2, MAZE_CENTERY + h - height//2))

    pygame.display.flip()
    wait4User(screen, key )

# Espera a que el usuario presione una tecla específica para continuar
def wait4User(screen, key):
    pause = True
    while pause:
        for e in pygame.event.get():
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if keys[key]:
                pause = False
                break
    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    screen.fill(BLACK)
    pygame.display.flip()

# Limpia la pantalla del laberinto
def screenMazeClear(screen):
    screen.fill(BLACK)
    pygame.display.flip()
    screen.fill(BLACK)
    pygame.display.flip()

# Realiza el efecto de scroll al cambiar de sala, en dirección opuesta a la salida del jugador
def screenScroll(screen, exit, color):
    # cantidad de desplazamiento y repeticiones según la dirección de salida
    dx, dy, iterations = {"N":(0,10,SCREEN_HEIGHT//10), "S":(0,-10, SCREEN_HEIGHT//10), "W":(10,0,SCREEN_WIDTH//10), "E":(-10,0,SCREEN_WIDTH//10)}[exit]

    # Captura la imagen actual del área del laberinto
    bg = screen.subsurface(0,0,SCREEN_WIDTH, BORDERTHICKNESS + MAZE_HEIGHT + WALLTHICKNESS*4).convert()

    # Cambia todos los colores del laberinto a azul
    pixelArray = pygame.PixelArray(bg)
    pixelArray.replace(color,WALL_COLOR)
    pixelArray.replace(GREEN,WALL_COLOR)
    del pixelArray

    # Realiza el desplazamiento visual
    for i in range(iterations):
        screen.blit(bg,(0,0))
        pygame.display.flip()
        pygame.time.delay(40)
        bg.scroll(dx,dy)

    screenMazeClear(screen)

# Muestra la pantalla de controles del juego
def gameCntrls(screen):
    blinkMsg(screen, blinkCntrls, "Presione cualquier tecla para salir")

# Dibuja los controles del juego y un mensaje parpadeante
def blinkCntrls(screen, msg, display=True):
    title = "JUEGO  BERZERK  CONTROLES"
    font_path = FONT_PATH
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)
    fonttxt = font.render(title,1,GREEN)
    w,h = font.size(title)
    screen.blit(fonttxt,(SCREEN_WIDTH//2 - w//2, BORDERTHICKNESS))

    # Instrucciones en español
    cntrls = (
        "[ FLECHA IZQUIERDA ] - Mover al jugador a la izquierda",
        "[ FLECHA DERECHA ] - Mover al jugador a la derecha",
        "[ FLECHA ARRIBA ] - Mover al jugador hacia arriba",
        "[ FLECHA ABAJO ] - Mover al jugador hacia abajo",
        "[ BARRA ESPACIADORA ] - Disparar láser",
        "[ TECLA F1 ] - Pausar el juego",
        "[ TECLA F2 ] - Mostrar/ocultar FPS",
        "[ TECLA ESC ] - Salir del juego"
    )

    font = pygame.font.Font(FONT, 16)
    y = BORDERTHICKNESS + h*3
    for txt in cntrls:
        fonttxt = font.render(txt,True,WHITE,BLACK)
        w,h = font.size(txt)
        screen.blit(fonttxt,(SCREEN_WIDTH//2 - w//2,y - h))
        y += h + h//2

    if display == True:
        font_size = 12
        font = pygame.font.Font(font_path,font_size)
        txt = font.render(msg,1,GREEN)
        txt_width = txt.get_width()
        txt_height = txt.get_height()
        screen.blit(txt,(SCREEN_WIDTH//2 - txt_width//2,SCREEN_HEIGHT - txt_height))

    pygame.display.flip()

# Muestra un mensaje parpadeante y espera a que el usuario presione una tecla
def blinkMsg(screen, function, msg):
    pause = True
    keys = None
    display = True
    screen.fill(BLACK)
    pygame.display.flip()
    pygame.time.set_timer(BLINK,500)    # 0.5 sec event
    while pause:
        function(screen, msg, display)
        for e in pygame.event.get():
            if e.type == BLINK:
                display = not display
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                pygame.time.set_timer(BLINK,0)
                pause = False
                break
    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    screen.fill(BLACK)
    pygame.display.flip()
    return keys

# Muestra la pantalla de puntajes altos
def highScoresScreen(screen):
    return blinkMsg(screen, blinkHighScores, MSG1)

HIGH_SCORE = "Puntajes Altos"
COPYRIGHT = u"\u00A9" + " 1980  STERN  Electrónica,  Inc."
MSG1 = "Cómo jugar: F1    Iniciar juego: BARRA ESPACIADORA"

# Dibuja la pantalla de puntajes altos
def blinkHighScores(screen, msg, display):
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)
    txt = font.render(HIGH_SCORE,1,GREEN)
    w,h = font.size(HIGH_SCORE)
    screen.blit(txt,(SCREEN_WIDTH//2 - w//2,BORDERTHICKNESS))
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH//5,BORDERTHICKNESS+30),(SCREEN_WIDTH//5*4, BORDERTHICKNESS+30), 4)

    hs = getHighScores()

    # determina el ancho y desplazamiento inicial para los puntajes
    images = []
    txt = '10W00000WWXXX'     # plantilla para puntaje alto
    _colortext(txt,font,False,(BLACK),images)
    imglen = 0
    for img in images:
        imglen += img[0][0]
    y_offset = img[0][1]

    for i, (name,score) in enumerate(hs,1):
        x = SCREEN_WIDTH//2 - imglen//2
        images[:] = []  # limpia la lista

        # ordena de mayor a menor
        txt = '{:02d}W'.format(i)
        _colornum(txt,font,True,(RED),images)

        # puntaje
        txt = '{:05d}W'.format(score)
        _colornum(txt,font,True,(YELLOW),images)

        # iniciales
        txt = '{:3}'.format(name)
        _colortext(txt,font,True,(DARK_ORCHID),images)

        y = BORDERTHICKNESS+30 + y_offset*i
        for img in images:
            x1,y1 = img[0]
            screen.blit(img[1],(x,y))
            x += x1

    txt = font.render(COPYRIGHT,True,WHITE,BLACK)
    w,h = font.size(COPYRIGHT)
    screen.blit(txt,(SCREEN_WIDTH//2 - w//2,SCREEN_HEIGHT - BORDERTHICKNESS*2 - h))
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH//5,SCREEN_HEIGHT - BORDERTHICKNESS*2 - h//2*3), (SCREEN_WIDTH//5*4, SCREEN_HEIGHT - BORDERTHICKNESS*2 - h//2*3), 4)
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH//5,SCREEN_HEIGHT - BORDERTHICKNESS*2 + h//2),   (SCREEN_WIDTH//5*4, SCREEN_HEIGHT - BORDERTHICKNESS*2 + h//2),   4)

    if display == True:
        font_size = 12
        font = pygame.font.Font(FONT_PATH,font_size)
        txt = font.render(MSG1,1,GREEN)
        txt_width = txt.get_width()
        txt_height = txt.get_height()
        screen.blit(txt,(SCREEN_WIDTH//2 - txt_width//2,SCREEN_HEIGHT - txt_height))

    pygame.display.flip()

# Dibuja un número coloreado para la pantalla de puntajes altos
def _colornum(text, font, flag, color, images):
    for c in text[:]:
        _color = color
        if (flag == True) and (c == '0'):
            _color = BLACK
        else:
            flag = False    # oculta ceros a la izquierda
        if c == 'W':
            _color = BLACK
        offset = font.size(c)
        img = font.render(c, True, _color, BLACK)
        images.append((offset,img))

# Dibuja texto coloreado para la pantalla de puntajes altos
def _colortext(text, font, flag, color, images):
    for c in text[:]:
        _color = color
        if flag == True:
            if c == ' ':
                c = 'W'
                _color = BLACK
        offset = font.size(c)
        img = font.render(c, True, _color, BLACK)
        images.append((offset,img))

# Obtiene los puntajes altos guardados en archivo
def getHighScores():
    highscores = []

    # Prueba si el archivo existe y lo carga
    try:
        with open('highscores.txt', 'rb') as file:
            highscores = pickle.load(file)
            high_scores = sorted(highscores, key=itemgetter(1), reverse=True)[:10]
    except (IOError, EOFError) as e:
        # No existe o está vacío
        pass

    return highscores

# Muestra la pantalla para ingresar al Hall of Fame y guarda el puntaje
def hallOfFame(screen, highscores, score):
    font_path = FONT_PATH
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)

    tbl = [((YELLOW),1, "¡Felicidades Jugador!"),
           ((BLACK), 1, " "),
           ((DEEPSKYBLUE), 1, "Has entrado entre los inmortales"),
           ((DEEPSKYBLUE), 1, "en el salón de la fama de BERZERK"),
           ((BLACK), 1, " "),
           ((DEEPSKYBLUE), 1.5, "Ingresa tus iniciales:"),
           ((WHITE), 1, "W|W|W"),
           ((WHITE), 1, " "),
           ((GREEN), 1, "Usa las flechas arriba/abajo para cambiar letra"),
           ((GREEN), 1, "y la flecha derecha para guardar.")]

    y = BORDERTHICKNESS*3
    coor = None
    for (color, factor, txt) in tbl:
        fonttxt = font.render(txt,True,color,BLACK)
        w,h = font.size(txt)
        if txt == "W|W|W":
            coor = getInitialCoor(font,SCREEN_WIDTH//2 - w//2,y)
        else:
            screen.blit(fonttxt,(SCREEN_WIDTH//2 - w//2, y))
        y += int(h*factor)

    for x,y,w,h in coor:
        underlineInitials(screen,WHITE,(x,y),(x+w,y))

    indx = 0
    hof = ""
    while True:
        x,y,w,h = coor[indx]
        initial = enterInitial(screen,font,x,y,w,h)
        hof += initial
        underlineInitials(screen,BLACK,(x,y),(x+w,y))
        pygame.display.flip()
        indx += 1
        if indx >= 3:
            break

    # Guarda el nuevo puntaje en el archivo
    topScores(highscores, hof, score)

# Permite al usuario ingresar sus iniciales para el Hall of Fame
def enterInitial(screen,font,x,y,w,h):
    inits = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    indx = 0
    exitkey = None

    letter = "A"
    fonttxt = font.render(letter, True, WHITE, BLACK)
    # centra la letra
    wtmp,htmp = font.size(letter)
    offset = (w - wtmp)/2
    screen.blit(fonttxt,(x+offset,y))
    pygame.display.flip()

    wait = True
    while wait:
        for e in pygame.event.get():
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                KEY_DICT = {K_UP:1, K_DOWN:-1}
                if e.key in KEY_DICT:
                    indx += KEY_DICT[e.key]
                    if indx < 0:
                        indx = len(inits)-1
                    if indx >= len(inits):
                        indx = 0
                    letter = inits[indx:indx+1]
                    fonttxt = font.render("W",True,BLACK,BLACK)
                    screen.blit(fonttxt,(x,y))
                    fonttxt = font.render(letter,True,WHITE,BLACK)
                    # centra la letra
                    wtmp,htmp = font.size(letter)
                    offset = (w - wtmp)/2
                    screen.blit(fonttxt,(x+offset,y))
                    pygame.display.flip()
                if e.key == K_RIGHT:
                    wait = False

    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    return letter

# Calcula las coordenadas para subrayar las iniciales ingresadas
def getInitialCoor(font,x,y):
    coor = [(0,0,0,0),(0,0,0,0),(0,0,0,0)]
    txt = "W|W|W"
    w,h = font.size(txt)
    _x = SCREEN_WIDTH//2 - w//2
    lst = list(enumerate(txt))
    for i,letter in lst:
        _w,_h = font.size(letter)
        if i in [0,2,4]:
            coor[i//2] = (_x,y+h,_w,_h)
            _x += _w
        else:
            _x += _w//2
    return coor

# Dibuja una línea para subrayar las iniciales
def underlineInitials(screen,color,start_pos,end_pos):
    pygame.draw.line(screen,color,start_pos,end_pos,2)

# Guarda los puntajes altos en el archivo
def topScores(topscores, player, score):
    topscores.append((player,score))

    # solo los 10 mejores
    topscores = sorted(topscores, key=itemgetter(1), reverse=True)[:10]

    try:
        with open('highscores.txt', 'wb') as file:
            pickle.dump(topscores, file)
    except IOError as e:
        # no existe el archivo
        pass