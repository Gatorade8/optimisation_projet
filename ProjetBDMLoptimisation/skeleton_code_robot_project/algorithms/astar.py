
import heapq
import sys
import os

# permet d'importer grid.py depuis le dossier parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grid import get_neighbors


def heuristic(a, b):
    # heuristique admissible: distance de manhattan
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(grid, start, goal):
    # algorithme A*: f(n) = g(n) + h(n)
    # g(n) = cout reel depuis le depart
    # h(n) = estimation heuristique jusqu'au but (distance manhattan)
    # garantit le chemin optimal si h est admissible

    # file de priorite: (f_score, position)
    open_list = []
    heapq.heappush(open_list, (0, start))

    # dictionnaire pour retrouver le chemin: came_from[pos] = parent
    came_from = {start: None}

    # cout reel depuis le depart pour chaque case visitee
    g_score = {start: 0}

    while open_list:
        _, current = heapq.heappop(open_list)

        # on a atteint le but, on reconstruit le chemin
        if current == goal:
            return rebuild_path(came_from, goal)

        for neighbor in get_neighbors(grid, current):
            # cout pour aller vers ce voisin = +1 par deplacement
            new_g = g_score[current] + 1

            if neighbor not in g_score or new_g < g_score[neighbor]:
                g_score[neighbor] = new_g
                came_from[neighbor] = current
                f = new_g + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f, neighbor))

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
