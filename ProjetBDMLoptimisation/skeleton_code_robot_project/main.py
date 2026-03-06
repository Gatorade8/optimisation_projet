
import time
import os

from grid import load_grid, get_neighbors
from algorithms.greedy import greedy_search
from algorithms.astar import astar_search
from algorithms.genetic import genetic_search

# chemin absolu vers le dossier grid_datasets, peu importe d'ou on lance le script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRIDS_DIR = os.path.join(BASE_DIR, "..", "grid_datasets")


def afficher_grille_avec_chemin(grid, path, nom_algo):
    # affiche la grille dans le terminal avec le chemin marque par des points
    print(f"\n--- Grille: {nom_algo} ---")
    path_set = set(path)
    for y, row in enumerate(grid):
        ligne = ""
        for x, val in enumerate(row):
            if (x, y) in path_set and val not in ("S", "G"):
                ligne += ". "
            else:
                ligne += val + " "
        print(ligne)
    print()


def comparer_algos(grid, start, goal):
    # compare les 3 algorithmes et affiche un tableau de resultats

    resultats = []

    # algo glouton
    debut = time.perf_counter()
    path_greedy = greedy_search(grid, start, goal)
    temps_greedy = time.perf_counter() - debut
    resultats.append(("Glouton", path_greedy, temps_greedy))

    # algo A*
    debut = time.perf_counter()
    path_astar = astar_search(grid, start, goal)
    temps_astar = time.perf_counter() - debut
    resultats.append(("A*", path_astar, temps_astar))

    # algo genetique
    debut = time.perf_counter()
    path_genetic = genetic_search(grid, start, goal)
    temps_genetic = time.perf_counter() - debut
    resultats.append(("Genetique", path_genetic, temps_genetic))

    return resultats


def traiter_grille(fichier):
    print(f"\n{'='*60}")
    print(f"Grille: {os.path.basename(fichier)}")
    print(f"{'='*60}")

    grid, start, goal = load_grid(fichier)
    print(f"Depart: {start}, But: {goal}")

    # lancement de la comparaison
    resultats = comparer_algos(grid, start, goal)

    # affichage des grilles avec les chemins trouves
    for nom, path, _ in resultats:
        if path:
            afficher_grille_avec_chemin(grid, path, nom)
        else:
            print(f"\n[{nom}] Aucun chemin trouve")

    # tableau comparatif des resultats
    print(f"\n{'Algorithme':<15} {'Longueur chemin':<18} {'Temps execution':<20} {'Chemin trouve ?'}")
    print("-"*65)

    for nom, path, temps in resultats:
        longueur = len(path) if path else 0
        trouve = "Oui" if path and path[-1] == goal else "Non"
        print(f"{nom:<15} {longueur:<18} {temps:.6f}s{'':<12} {trouve}")


def main():
    # recupere toutes les grilles disponibles dans grid_datasets
    grids_path = os.path.normpath(GRIDS_DIR)
    fichiers = sorted([
        os.path.join(grids_path, f)
        for f in os.listdir(grids_path)
        if f.endswith(".txt")
    ])

    if not fichiers:
        print(f"Aucun fichier .txt trouve dans: {grids_path}")
        return

    for fichier in fichiers:
        traiter_grille(fichier)

    # questions d'analyse
    print(f"\n\n{'='*60}")
    print("--- Questions d'analyse ---")
    print("1. Pourquoi le glouton ne garantit pas le chemin optimal ?")
    print("   -> Il choisit toujours le voisin le plus proche du but (heuristique seule),")
    print("      sans tenir compte du cout reel deja parcouru. Il peut tomber dans un")
    print("      cul-de-sac ou prendre un chemin plus long.")
    print()
    print("2. Pourquoi A* est souvent plus performant pour trouver un chemin optimal ?")
    print("   -> A* combine le cout reel g(n) et l'estimation h(n). Avec une heuristique")
    print("      admissible (ne surestime jamais), il garantit le chemin le plus court.")
    print()
    print("3. Avantages et inconvenients d'un algo genetique ?")
    print("   -> Avantages: explore beaucoup de chemins en parallele, fonctionne meme")
    print("      sur des espaces difficiles. Inconvenients: non deterministe, n'est pas")
    print("      garanti de trouver le chemin optimal, plus lent sur des petites grilles.")


if __name__ == "__main__":
    main()
