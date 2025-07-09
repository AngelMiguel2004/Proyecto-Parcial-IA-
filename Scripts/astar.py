import heapq

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