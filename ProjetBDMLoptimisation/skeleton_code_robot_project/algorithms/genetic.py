
import random
import sys
import os

# permet d'importer grid.py depuis le dossier parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grid import get_neighbors


# chaque mouvement est encode comme un entier: 0=droite, 1=gauche, 2=bas, 3=haut
MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# parametres de l'algo genetique
POPULATION_SIZE = 100
GENERATIONS = 200
MUTATION_RATE = 0.05
TOURNAMENT_SIZE = 5


def apply_moves(grid, start, goal, chromosome):
    # applique la sequence de mouvements sur la grille depuis le depart
    # retourne le chemin parcouru (liste de positions) et la distance min atteinte au but
    x, y = start
    path = [(x, y)]
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    for move in chromosome:
        dx, dy = MOVES[move]
        nx, ny = x + dx, y + dy
        # verifie qu'on reste dans la grille et qu'on evite les obstacles
        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] != "X":
            x, y = nx, ny
            path.append((x, y))
            # si on atteint le but on arrete
            if (x, y) == goal:
                break

    return path


def fitness(grid, start, goal, chromosome):
    # calcule la qualite d'un chromosome: plus le score est eleve, meilleur il est
    path = apply_moves(grid, start, goal, chromosome)
    last_pos = path[-1]

    # distance de manhattan au but depuis la derniere position atteinte
    dist = abs(last_pos[0] - goal[0]) + abs(last_pos[1] - goal[1])

    # bonus si on atteint le but, malus pour les chemins longs
    if last_pos == goal:
        # on favorise les chemins courts qui atteignent le but
        return 1000 - len(path)
    else:
        # on favorise les chromosomes qui s'approchent du but
        return -dist


def selection_tournoi(population, scores):
    # selection par tournoi: on tire un sous-ensemble et on choisit le meilleur
    tournament = random.sample(range(len(population)), TOURNAMENT_SIZE)
    best = max(tournament, key=lambda i: scores[i])
    return population[best]


def croisement(parent1, parent2):
    # croisement en un point: on coupe les deux parents et on melange les moities
    point = random.randint(1, len(parent1) - 1)
    enfant = parent1[:point] + parent2[point:]
    return enfant


def mutation(chromosome):
    # mutation: chaque gene a une chance de changer aleatoirement
    return [
        random.randint(0, 3) if random.random() < MUTATION_RATE else gene
        for gene in chromosome
    ]


def genetic_search(grid, start, goal):
    # algorithme genetique pour trouver un chemin dans la grille
    # encode un chemin comme une sequence de mouvements (genes)

    # on adapte la taille du chromosome en fonction de la taille de la grille
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    # la longueur du chromosome depend de la taille de la grille (par ex. pour s'assurer d'avoir assez de mouvements)
    chromosome_length = max(40, rows * cols)

    # initialisation de la population: chromosomes aleatoires
    population = [
        [random.randint(0, 3) for _ in range(chromosome_length)]
        for _ in range(POPULATION_SIZE)
    ]

    best_path = []
    best_score = float("-inf")

    for generation in range(GENERATIONS):
        scores = []
        solution_trouvee = False
        
        # evaluation des chromosomes un par un
        for chrom in population:
            score = fitness(grid, start, goal, chrom)
            scores.append(score)
            
            # met a jour le meilleur chemin trouve jusqu'ici
            if score > best_score:
                best_score = score
                best_path = apply_moves(grid, start, goal, chrom)
                
            # s'arrete des qu'un chromosome a trouve la solution
            if best_path and best_path[-1] == goal:
                solution_trouvee = True
                break
                
        # si on a trouve un chemin jusqu'au but on peut s'arreter (meme avant la fin de la generation)
        if solution_trouvee:
            break

        # creation de la nouvelle generation
        new_population = []
        for _ in range(POPULATION_SIZE):
            parent1 = selection_tournoi(population, scores)
            parent2 = selection_tournoi(population, scores)
            enfant = croisement(parent1, parent2)
            enfant = mutation(enfant)
            new_population.append(enfant)

        population = new_population

    return best_path
