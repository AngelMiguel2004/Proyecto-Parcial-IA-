# Miguel Ángel Jiménez 23-EISN-2-010
# Este módulo implementa la lógica de la cuadrícula (grid) y el algoritmo A* para el juego PyBerzerk.

import sys, os, pygame
from pygame.locals import *
import heapq
from Scripts.constantes import *
from Scripts.astar import AStar  # Importa la clase AStar desde el nuevo archivo

# Clase que representa una celda del grid/laberinto
class Cell(object):
    def __init__(self, x, y, reachable):
        """
        Inicializa una nueva celda.
        @param reachable: ¿es alcanzable la celda? ¿no es una pared?
        @param x: coordenada x de la celda
        @param y: coordenada y de la celda
        @param g: costo desde el inicio hasta esta celda
        @param h: estimación del costo hasta la celda final
        @param f: f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

        # Coordenadas en pantalla para dibujar la celda
        self.screenX = MAZE_XMIN-4 + x*16
        self.screenY = MAZE_YMIN+8 + y*22

    # Permite comparar celdas por su valor f (para heapq)
    def __lt__(self, other):
        return self.f < other.f

"""
0: celda vacía
1: celda no alcanzable (pared)
2: celda final
3: celda visitada
"""

# Clase que representa el grid/laberinto
class Grid(object):
    def __init__(self, width, height, walls, cols=5, rows=3):
        self.width = width
        self.height = height
        self.walls = walls
        self.gridcells = []
        self.wallcells = []

        # Crea todas las celdas como alcanzables inicialmente
        for x in range(width):       # 0-39
            for y in range(height):   # 0-21
                self.gridcells.append(Cell(x,y,True))

        # Marca las celdas que son paredes según la configuración de 'walls'
        for i, w in list(enumerate(walls[:])):
            if w == "N":
                # Pared norte: marca como no alcanzables las celdas en la parte superior de la sección correspondiente
                x = (8,16,24,32)[i%4]
                # Selecciona el rango de filas según la sección
                for y in {0:(0,1,2,3,4,5,6),1:(6,7,8,9,10,11,12,13,14)}[int(i/4)]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "S":
                # Pared sur: marca como no alcanzables las celdas en la parte inferior de la sección correspondiente
                x = (8,16,24,32)[i%4]
                for y in {0:(6,7,8,9,10,11,12,13,14),1:(14,15,16,17,18,19,20,21)}[int(i/4)]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "E":
                # Pared este: marca como no alcanzables las celdas en el borde derecho de la sección correspondiente
                y = (6,14)[int(i/4)]
                for x in {0:(8,9,10,11,12,13,14,15,16),1:(16,17,18,19,20,21,22,23,24),2:(24,25,26,27,28,29,30,31,32),3:(32,33,34,35,36,37,38,39)}[i%4]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "W":
                # Pared oeste: marca como no alcanzables las celdas en el borde izquierdo de la sección correspondiente
                y = (6,14)[int(i/4)]
                for x in {0:(0,1,2,3,4,5,6,7,8),1:(8,9,10,11,12,13,14,15,16),2:(16,17,18,19,20,21,22,23,24),3:(24,25,26,27,28,29,30,31,32)}[i%4]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            else:
                pass

    # Devuelve las coordenadas en pantalla de una celda
    def getScreenCoor(self,x,y):
        cell = self.gridcells[x * self.height + y]
        return cell.screenX, cell.screenY

    # Convierte coordenadas de pantalla a coordenadas de celda
    def getCellCoor(self,x,y):
        return (x - (MAZE_XMIN-4))/16, (y - (MAZE_YMIN+8))/22

    # Devuelve el objeto Cell en la posición x, y
    def getCell(self,x,y):
        return self.gridcells[x * self.height + y]

    # Devuelve el cuadrante del laberinto en el que está una posición
    def getQuadrant(self,x,y):
        return int((x-MAZE_XMIN)/BORDER_HSEGMENT), int((y-MAZE_YMIN)/BORDER_VSEGMENT)

    # Devuelve las celdas adyacentes a una celda (derecha, arriba, izquierda, abajo)
    def get_adjacent_cells(self, cell):
        """
        Devuelve las celdas adyacentes a una celda.
        El orden es horario comenzando por la derecha.
        @param cell: celda para la que se buscan adyacentes
        @returns: lista de celdas adyacentes
        """
        cells = []
        if cell.x < self.width-1:
            cells.append(self.getCell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.getCell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.getCell(cell.x-1, cell.y))
        if cell.y < self.height-1:
            cells.append(self.getCell(cell.x, cell.y+1))
        return cells

    """
    def drawGrid(self,screen):
        # Dibuja la cuadrícula del laberinto (debug)
        for i in range(len(self.gridcells)):
            x,y = self.gridcells(i)
        for x in range(MAZE_XMIN,MAZE_XMAX,16):
            for y in range(MAZE_YMIN,MAZE_YMAX ,22):
                pygame.draw.line(screen, RED, (x, y), (MAZE_XMAX, y), (1))
                pygame.draw.line(screen, RED, (x, y), (x, MAZE_YMAX), (1))
                print(x,y)

        # Asegura que el rectángulo esté dentro de los límites
        self.rect.x = random.randrange(MAZE_XMIN+self.rect.width,  MAZE_XMAX-self.rect.width)
        self.rect.y = random.randrange(MAZE_YMIN+self.rect.height, MAZE_YMAX-self.rect.height)
    """
# Clase que implementa el algoritmo A* para encontrar caminos
class AStar(object):
    def __init__(self):
        # Lista de celdas abiertas (por explorar)
        self.opened = []
        heapq.heapify(self.opened)
        # Conjunto de celdas cerradas (ya exploradas)
        self.closed = set()
        # Lista de todas las celdas del grid
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    # Inicializa el grid para la búsqueda A*
    def init_grid(self, grid, start, end):
        """
        Prepara las celdas del grid y las paredes.
        @param grid: objeto Grid
        @param start: tupla (x, y) de inicio
        @param end: tupla (x, y) de destino
        """
        self.grid_height = grid.height
        self.grid_width = grid.width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in grid.wallcells:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    # Calcula la heurística (distancia Manhattan) para una celda
    def get_heuristic(self, cell):
        """
        Calcula el valor heurístico H para una celda.
        Distancia entre esta celda y la celda final multiplicada por 10.
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    # Devuelve la celda en la posición x, y
    def get_cell(self, x, y):
        x = int(x)
        y = int(y)
        cell = self.cells[x * self.grid_height + y]
        return cell

    # Devuelve las celdas adyacentes a una celda
    def get_adjacent_cells(self, cell):
        """
        Devuelve las celdas adyacentes a una celda.
        El orden es horario comenzando por la derecha.
        @param cell: celda para la que se buscan adyacentes
        @returns: lista de celdas adyacentes
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))  # Derecha
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))  # Arriba
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))  # Izquierda
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))  # Abajo
        return cells

    # Reconstruye el camino desde el final hasta el inicio
    def get_path(self):
        """
        Reconstruye el camino desde la celda final hasta la inicial.
        @returns: lista de tuplas (x, y) representando el camino
        """
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            if cell is None:
                pass  # Si no hay camino, simplemente termina
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    # Actualiza los valores de una celda adyacente
    def update_cell(self, adj, cell):
        """
        Actualiza la celda adyacente.
        @param adj: celda adyacente a la celda actual
        @param cell: celda actual
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    # Muestra el camino encontrado (por consola)
    def display_path(self):
        cell = self.end
        while cell.parent is not self.start:
            cell = cell.parent
            print('path: cell: %d,%d' % (cell.x, cell.y))

    # Resuelve el laberinto usando A* y devuelve el camino encontrado
    def solve(self):
        """
        Resuelve el laberinto, encuentra el camino a la celda final.
        @returns: lista de tuplas (x, y) del camino o None si no hay solución.
        """
        # Agrega la celda inicial a la cola de prioridad
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # Saca la celda con menor f de la cola
            f, cell = heapq.heappop(self.opened)
            # Marca la celda como cerrada
            self.closed.add(cell)
            # Si es la celda final, devuelve el camino
            if cell is self.end:
                #self.display_path()
                return self.get_path()
            # Obtiene las celdas adyacentes
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # Si ya está en la lista abierta, verifica si el nuevo camino es mejor
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # Agrega la celda adyacente a la lista abierta
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))
                        # Verifica si el nuevo camino es mejor
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                        else:
                            self.update_cell(adj_cell, cell)
                            # Agrega la celda adyacente a la lista abierta
                            heapq.heappush(self.opened, (adj_cell.f, adj_cell))
                        # Repite la verificación por seguridad
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                        else:
                            self.update_cell(adj_cell, cell)
                            heapq.heappush(self.opened, (adj_cell.f, adj_cell))
