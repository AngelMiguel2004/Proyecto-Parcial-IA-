# Clase base para todos los nodos del árbol de comportamiento.
class Node:
    # Método que debe ser implementado por las subclases.
    def run(self):
        raise NotImplementedError

# Nodo Selector: ejecuta a sus hijos hasta que uno retorna True.
class Selector(Node):
    def __init__(self, *children):
        # Guarda los nodos hijos.
        self.children = children
    def run(self):
        # Ejecuta cada hijo; retorna True si alguno tiene éxito.
        for child in self.children:
            if child.run():
                return True
        # Retorna False si ninguno tuvo éxito.
        return False

# Nodo Secuencia: ejecuta a sus hijos hasta que uno retorna False.
class Sequence(Node):
    def __init__(self, *children):
        # Guarda los nodos hijos.
        self.children = children
    def run(self):
        # Ejecuta cada hijo; retorna False si alguno falla.
        for child in self.children:
            if not child.run():
                return False
        # Retorna True si todos tuvieron éxito.
        return True

# Nodo Acción: ejecuta una función específica.
class Action(Node):
    def __init__(self, fn):
        # Guarda la función a ejecutar.
        self.fn = fn
    def run(self):
        # Ejecuta la función y retorna su resultado.
        return self.fn()
