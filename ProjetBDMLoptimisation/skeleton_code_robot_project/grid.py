
def load_grid(file):
    # charge la grille depuis un fichier texte et retourne la grille, le debut et la fin
    grid=[]
    start=None
    goal=None

    with open(file) as f:
        for y,line in enumerate(f):
            row=line.strip().split()
            for x,val in enumerate(row):
                if val=="S":
                    start=(x,y)
                if val=="G":
                    goal=(x,y)
            grid.append(row)

    return grid,start,goal


def get_neighbors(grid, pos):
    # retourne la liste des voisins accessibles de la position (x, y)
    # on se deplace seulement en haut, bas, gauche, droite (pas en diagonal)
    x, y = pos
    rows = len(grid)
    cols = len(grid[0])

    # les 4 direction possibles: droite, gauche, bas, haut
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    neighbors = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        # verifie qu'on reste dans les bornes de la grille
        if 0 <= nx < cols and 0 <= ny < rows:
            # accepte seulement les cases libres, le debut et l'arrivee
            if grid[ny][nx] != "X":
                neighbors.append((nx, ny))

    return neighbors
