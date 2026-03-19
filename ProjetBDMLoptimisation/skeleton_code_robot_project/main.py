
import time
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

from grid import load_grid
from algorithms.greedy import greedy_search
from algorithms.astar import astar_search
from algorithms.genetic import genetic_search

# chemin absolu vers le dossier grid_datasets, peu importe d'ou on lance le script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRIDS_DIR = os.path.join(BASE_DIR, "..", "grid_datasets")

# couleurs utilisees pour chaque type de case
COULEURS = {
    "0": "#1e2a3a",   # case libre: bleu fonce
    "X": "#c0392b",   # obstacle: rouge
    "S": "#2ecc71",   # depart: vert
    "G": "#f39c12",   # but: orange
    "chemin": "#3498db",  # chemin trouve: bleu clair
}

ALGOS = [
    ("Glouton",  greedy_search),
    ("A*",       astar_search),
    ("Genetique", genetic_search),
]


def afficher_grille_matplotlib(grid, path, ax, titre):
    # affiche la grille dans un subplot matplotlib avec le chemin colore
    rows = len(grid)
    cols = len(grid[0])
    path_set = set(path)

    # construction de la matrice de couleurs
    image = np.zeros((rows, cols, 3))
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if (x, y) in path_set and val not in ("S", "G"):
                hex_c = COULEURS["chemin"]
            else:
                hex_c = COULEURS[val]
            # conversion hex -> rgb normalise entre 0 et 1
            r = int(hex_c[1:3], 16) / 255
            g = int(hex_c[3:5], 16) / 255
            b = int(hex_c[5:7], 16) / 255
            image[y, x] = [r, g, b]

    ax.imshow(image, aspect="equal", interpolation="nearest")

    # quadrillage entre les cases
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=0.8)
    ax.tick_params(which="both", bottom=False, left=False,
                   labelbottom=False, labelleft=False)

    longueur = len(path) if path else 0
    ax.set_title(f"{titre}  (longueur: {longueur})", fontsize=10,
                 color="white", pad=6)
    ax.set_facecolor("#0f1923")


def comparer_algos(grid, start, goal):
    # execute les 3 algos et retourne les resultats
    resultats = []
    for nom, fn in ALGOS:
        debut = time.perf_counter()
        path = fn(grid, start, goal)
        temps = time.perf_counter() - debut
        resultats.append((nom, path, temps))
    return resultats


def visualiser_fichier(fichier):
    # charge la grille, lance les algos et affiche tout dans une figure
    grid, start, goal = load_grid(fichier)
    resultats = comparer_algos(grid, start, goal)

    # 3 grilles en haut + 1 tableau en bas
    fig = plt.figure(figsize=(14, 7), facecolor="#0f1923")
    fig.suptitle(
        f"Comparaison des algorithmes - {os.path.basename(fichier)}",
        fontsize=13, color="white", fontweight="bold", y=0.98
    )

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.35, wspace=0.15,
                           height_ratios=[2, 1])

    # affichage des 3 grilles
    for i, (nom, path, _) in enumerate(resultats):
        ax = fig.add_subplot(gs[0, i])
        afficher_grille_matplotlib(grid, path, ax, nom)

    # legende commune aux 3 grilles
    patches = [
        mpatches.Patch(color=COULEURS["S"],      label="Depart (S)"),
        mpatches.Patch(color=COULEURS["G"],      label="But (G)"),
        mpatches.Patch(color=COULEURS["chemin"], label="Chemin"),
        mpatches.Patch(color=COULEURS["X"],      label="Obstacle (X)"),
        mpatches.Patch(color=COULEURS["0"],      label="Case libre"),
    ]
    fig.legend(handles=patches, loc="upper right", fontsize=8,
               facecolor="#1e2a3a", edgecolor="#ffffff",
               labelcolor="white", ncol=1, framealpha=0.9)

    # tableau comparatif dans la ligne du bas (3 colonnes fusionnees)
    ax_table = fig.add_subplot(gs[1, :])
    ax_table.axis("off")
    ax_table.set_facecolor("#0f1923")

    entetes = ["Algorithme", "Longueur chemin", "Temps execution", "Chemin trouve ?"]
    donnees = [
        [nom,
         str(len(path)) if path else "0",
         f"{temps:.6f}s",
         "Oui" if path and path[-1] == goal else "Non"]
        for nom, path, temps in resultats
    ]

    table = ax_table.table(
        cellText=donnees,
        colLabels=entetes,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    # style du tableau
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("#1e2a3a" if row > 0 else "#2c3e6b")
        cell.set_text_props(color="white")
        cell.set_edgecolor("#3d5a8a")

    # affichage console pour verification rapide
    print(f"\n--- Resultats pour {os.path.basename(fichier)} ---")
    print(f"{'Algorithme':<12} | {'Longueur':<8} | {'Temps':<12} | {'Trouve ?':<8}")
    print("-" * 50)
    for nom, path, temps in resultats:
        trouve = "Oui" if path and path[-1] == goal else "Non"
        longueur = len(path) if path else 0
        print(f"{nom:<12} | {longueur:<8} | {temps:.6f}s | {trouve:<8}")
    print("-" * 50)

    # plt.show()  # commente pour eviter les blocages en environnement sans affichage


def main():
    grids_path = os.path.normpath(GRIDS_DIR)
    fichiers = sorted([
        os.path.join(grids_path, f)
        for f in os.listdir(grids_path)
        if f.endswith(".txt")
    ])

    for fichier in fichiers:
        visualiser_fichier(fichier)


if __name__ == "__main__":
    main()
