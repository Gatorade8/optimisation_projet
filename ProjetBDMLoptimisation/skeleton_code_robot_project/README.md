# Projet : Recherche de chemin pour un robot (Heuristiques)

## Description

Un robot se deplace dans une ville representee sous forme de grille 2D. L'objectif est de trouver le meilleur chemin entre un point de depart (S) et une destination (G) en evitant les obstacles (X).

Trois algorithmes sont implementes et compares dans une **interface web 3D (style Retro Gameboy)** :
- **Algorithme glouton** : choisit a chaque etape le voisin le plus proche du but sans garantir l'optimalite
- **Algorithme A\*** : f(n) = g(n) + h(n), garantit le chemin le plus court
- **Algorithme genetique** : encode les chemins comme sequences de mouvements, evolue de facon non-deterministe par selection/croisement/mutation

## Structure du projet

```
skeleton_code_robot_project/
|-- api.py                     # Backend API FastAPI servant de moteur de resolution
|-- main.py                    # Script de test original en ligne de commande
|-- grid.py                    # utilitaire de lecture de grille
|-- algorithms/
|   |-- greedy.py              # algorithme de recherche gloutonne
|   |-- astar.py               # algorithme de recherche A*
|   |-- genetic.py             # algorithme genetique
|-- data/ ou grid_datasets/    # dossier contenant les differentes cartes
|-- frontend_3d/               # Application Web 3D Pixel Art
```

## Format des cartes

Chaque carte (`.txt`) utilise le format suivant, delimite par des espaces :
- `S` : point de depart du robot
- `G` : destination a atteindre
- `0` : case libre
- `X` : obstacle (infranchissable)

Exemple (`grid1.txt`) :
```text
S 0 0 X 0
0 X 0 X 0
0 X 0 0 0
0 0 0 X 0
0 0 0 X G
```

## Installation & Execution

Ce projet fonctionne en deux parties : une **API Backend** qui resout le pathfinding, et une **UI Web** qui dessine le tout en 3D volumetrique.

### 1. Demarrer le Serveur Backend (Python)

Installez les dependances (FastAPI et Uvicorn) puis lancez le serveur :

```bash
pip install -r requirements.txt
python api.py
```
*(L'API ecoutera sur le port 8000)*

### 2. Demarrer l'Interface Frontend (Node.js)

Ouvrez un deuxieme terminal :

```bash
cd frontend_3d
npm install
npm run dev
# ou bien : npx vite
```
*(L'interface web sera a disposition typiquement sur http://localhost:5173)*

### 3. Utilisation

1. Ouvrez l'adresse de votre frontend dans votre navigateur web.
2. Utilisez le menu deroulant en haut a gauche pour **selectionner la carte** a resoudre.
3. Cliquez sur l'un des algorithmes pour animer sa recherche, ou ajustez les parametres du panneau **Reglages Genetique** si vous utilisez l'option *Genetique*.
4. **Compare All** executera les trois algorithmes en arriere-plan et mettra en surbrillance l'algorithme vainqueur dans les resultats affiches en bas a gauche.

### Creer de nouveaux niveaux

Pour rajouter un niveau dans le frontend, il suffit tout simplement d'ajouter un fichier texte avec un quadrillage dans le dossier ou les cartes se trouvent (souvent `data/` ou `grid_datasets/`). Il apparaitra automatiquement dans le menu de selection du jeu !
