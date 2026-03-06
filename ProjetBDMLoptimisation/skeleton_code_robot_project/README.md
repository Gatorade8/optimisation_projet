# Projet : Recherche de chemin pour un robot (Heuristiques)

## Description

Un robot se deplace dans une ville representee sous forme de grille 2D. L'objectif est de trouver le meilleur chemin entre un point de depart (S) et une destination (G) en evitant les obstacles (X).

Trois algorithmes sont implementes et compares :
- **Algorithme glouton** : choisit a chaque etape le voisin le plus proche du but
- **Algorithme A\*** : f(n) = g(n) + h(n), garantit le chemin optimal
- **Algorithme genetique** : encode les chemins comme sequences de mouvements, evolue par selection/croisement/mutation

## Structure du projet

```
skeleton_code_robot_project/
|-- main.py                    # point d'entree, comparison des algos
|-- grid.py                    # chargement de la grille et fonction get_neighbors
|-- algorithms/
|   |-- greedy.py              # algorithme glouton
|   |-- astar.py               # algorithme A*
|   |-- genetic.py             # algorithme genetique
|-- data/
    |-- grid1.txt              # grille de test 5x5
    |-- grid2.txt              # grille de test 6x7 (labyrinthe)
```

## Format des grilles

Chaque cellule peut etre :
- `S` : point de depart du robot
- `G` : destination a atteindre
- `0` : case libre
- `X` : obstacle (infranchissable)

Exemple de grille (`data/grid1.txt`) :
```
S 0 0 X 0
0 X 0 X 0
0 X 0 0 0
0 0 0 X 0
0 0 0 X G
```

## Comment executer le programme

### Lancer la comparaison sur grid1.txt

```bash
py main.py
```

ou si `python` est dans le PATH :

```bash
python main.py
```

Le programme affiche :
1. La grille avec le chemin marque par des points (`.`) pour chaque algorithme
2. Un tableau comparatif avec la longueur du chemin et le temps d'execution
3. Les reponses aux questions d'analyse

### Changer de grille

Dans `main.py`, modifier la ligne suivante pour utiliser une autre grille :
```python
fichier = "data/grid1.txt"  # changer par "data/grid2.txt" par exemple
```

### Creer sa propre grille

Creer un fichier `.txt` dans `data/` avec les symboles `S`, `G`, `0`, `X` separes par des espaces. Exemple :
```
S 0 0
0 X 0
0 0 G
```

## Resultats typiques (grid1.txt)

| Algorithme | Longueur chemin | Temps execution | Chemin trouve ? |
|------------|----------------|-----------------|-----------------|
| Glouton    | 13             | ~0.0001s        | Oui             |
| A*         | 9              | ~0.00004s       | Oui             |
| Genetique  | variable       | ~0.002s         | Oui             |

## Questions d'analyse

1. **Pourquoi le glouton ne garantit pas le chemin optimal ?**
   Il choisit toujours le voisin le plus proche du but sans tenir compte du cout deja parcouru, ce qui peut mener a des chemins plus longs.

2. **Pourquoi A* est souvent plus performant ?**
   A* combine le cout reel g(n) et l'heuristique h(n). Avec une heuristique admissible (distance de Manhattan), il garantit le chemin le plus court.

3. **Avantages et inconvenients de l'algo genetique ?**
   - Avantages : explore beaucoup de solutions en parallele, robuste sur des espaces complexes
   - Inconvenients : non deterministe, ne garantit pas l'optimal, plus lent sur petites grilles
