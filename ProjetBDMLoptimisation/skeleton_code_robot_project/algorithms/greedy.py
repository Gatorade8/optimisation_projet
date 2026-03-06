
import heapq
import sys
import os

# permet d'importer grid.py depuis le dossier parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grid import get_neighbors


def heuristic(a, b):
    # distance de manhattan: somme des differences absolues en x et y
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def greedy_search(grid, start, goal):
    # algorithme glouton: choisit toujours le voisin le plus proche du but
    # il est pas garanti de trouver le chemin optimal

    # file de priorite: (heuristique, position)
    open_list = []
    heapq.heappush(open_list, (heuristic(start, goal), start))

    # dictionnaire pour retrouver le chemin: came_from[pos] = parent
    came_from = {start: None}

    while open_list:
        _, current = heapq.heappop(open_list)

        # on a atteint le but, on reconstruit le chemin
        if current == goal:
            return rebuild_path(came_from, goal)

        for neighbor in get_neighbors(grid, current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                h = heuristic(neighbor, goal)
                heapq.heappush(open_list, (h, neighbor))

    # aucun chemin trouver
    return []


def rebuild_path(came_from, goal):
    # remonte depuis le but jusqu'au debut pour reconstruire le chemin
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
