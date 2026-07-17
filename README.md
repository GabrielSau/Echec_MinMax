# ♟️ Chess AI — MinMax & Élagage Alpha-Bêta

Jeu d'échecs jouable en graphique (Pygame) contre une intelligence
artificielle maison, basée sur l'algorithme **MinMax avec élagage
Alpha-Bêta**. Réalisé dans le cadre du TP02 noté (Jeux en situation
d'adversité).

## 1. Présentation du jeu

### Description

Le joueur humain affronte une IA aux échecs. L'IA explore l'arbre des
coups possibles avec l'algorithme MinMax, élagué par la technique
Alpha-Bêta pour réduire le nombre de nœuds visités, et choisit le coup
qui maximise (pour elle) / minimise (pour l'adversaire) une fonction
d'évaluation de la position.

### Problème adressé

Aux échecs, l'espace des coups possibles explose exponentiellement
avec la profondeur de recherche. Le TP illustre comment MinMax +
Alpha-Bêta permet de trouver un coup fort sans explorer l'intégralité
de l'arbre, et comment une fonction d'évaluation plus riche que le
simple comptage de matériel améliore la qualité du jeu.

### Public cible

Étudiants, curieux d'IA de jeux, ou toute personne souhaitant jouer
une partie d'échecs contre une IA locale simple, sans connexion
internet ni moteur externe (type Stockfish).

## 2. Fonctionnalités

- **Partie graphique complète** : échiquier interactif (Pygame),
  sélection de pièce à la souris, surlignage des coups légaux, mise
  en évidence du dernier coup joué et de l'échec au roi.
- **IA MinMax + élagage Alpha-Bêta** (`ai/custom_ai.py`) :
  - Recherche récursive avec coupure Alpha-Bêta (`alpha >= beta`).
  - **Profondeur dynamique** : la profondeur de recherche augmente
    automatiquement quand il reste peu de pièces sur l'échiquier
    (finale), pour explorer plus loin quand l'espace de recherche est
    plus petit.
  - **Fonction d'évaluation enrichie**, au-delà du simple matériel :
    - Score matériel classique (pion=1, cavalier/fou=3, tour=5, dame=9).
    - Contrôle du centre par les pions (case centrale et centre élargi).
    - Pénalité pour un cavalier posté au bord de l'échiquier.
    - Bonus pour des tours liées (même rangée/colonne, rien entre
      elles).
    - Bonus pour chaque pièce mineure développée (sortie de sa case
      de départ).
    - Bonus pour la sécurité du roi (roqué + bouclier de pions
      devant lui), malus s'il reste au centre en milieu de partie.
    - Détection de mat / pat / nulle (matériel insuffisant, règle des
      50 coups, répétition).
- **Historique des coups** affiché en notation SAN dans le panneau
  latéral.
- **Statistiques de réflexion** : graphique (Matplotlib) du temps de
  calcul de l'IA coup par coup, accessible en fin de partie.
- **Visualiseur d'arbre de recherche** (bonus) : bouton « Voir
  l'arbre » qui exporte l'arbre MinMax réellement exploré (nœuds,
  valeurs alpha/bêta, branches élaguées) vers une page HTML
  autonome et navigable (zoom, déplacement, dépliage des nœuds).
- **Promotion automatique en Dame** pour rester simple.
- **Tests unitaires** (`pytest`) vérifiant que l'IA renvoie toujours
  un coup légal, en début et en milieu de partie.

## 3. Installation

Prérequis : Python 3.12 (ou compatible).

```bash
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Dépendances principales : `pygame`, `python-chess`, `matplotlib`,
`pytest`.

## 4. Lancer le jeu

```bash
python main.py
```

Un menu s'affiche pour lancer une partie contre l'IA (« Jouer contre
mon IA (MinMax) »). Le joueur humain joue toujours les **Blancs** :
cliquer sur une pièce puis sur la case de destination (les coups
légaux sont surlignés). L'IA joue les Noirs automatiquement dès que
c'est son tour.

En bas du panneau latéral :
- **Voir l'arbre** : ouvre dans le navigateur l'arbre de recherche
  MinMax du dernier coup calculé par l'IA.
- **Statistiques** : affiche le graphique du temps de réflexion de
  l'IA par coup.
- **Rejouer** / **Retour au menu** / **Quitter**.

## 5. Lancer les tests

```bash
pytest tests/
```

`tests/test_custom_ai.py` vérifie que `get_best_move_custom` renvoie
toujours un coup légal, en position de départ et en milieu de partie.

## 6. Exemples d'utilisation

1. Lancer `python main.py`, choisir « Jouer contre mon IA (MinMax) ».
2. Jouer un coup blanc (ex. e2-e4) : l'IA réfléchit puis répond
   automatiquement en noir.
3. À tout moment, cliquer sur « Voir l'arbre » pour visualiser
   comment l'IA a évalué ses options sur le dernier coup joué.
4. En fin de partie (mat, pat, nulle), cliquer sur « Statistiques »
   pour voir l'évolution du temps de calcul de l'IA au fil de la
   partie.

## 7. Structure du projet

```
Echec_MinMax/
├── main.py                 # point d'entrée
├── menu.py                 # menu de sélection
├── game.py                 # boucle de jeu, tour par tour, appel de l'IA
├── renderer.py              # affichage Pygame (échiquier + panneau latéral)
├── stats.py                  # graphique matplotlib (temps de calcul IA)
├── tree_html_export.py        # export de l'arbre de recherche en HTML
├── tree_visualizer.py          # utilitaires de visualisation de l'arbre
├── config.py                    # constantes (couleurs, tailles, profondeur par défaut)
├── ai/
│   ├── custom_ai.py             # <-- MinMax + élagage Alpha-Bêta + évaluation
│   └── tree_logger.py           # enregistrement de l'arbre exploré (pour la visualisation)
├── tests/
│   └── test_custom_ai.py        # tests unitaires
└── requirements.txt
```

## 8. Usage de l'IA générative (déclaration obligatoire)

Un assistant IA (Claude, Anthropic) a été utilisé ponctuellement en
appui du développement. Tout le code concerné est encadré dans le
code source par des commentaires `# ######## CODE IA (Claude) ####`.
Détail complet des prompts et de ce qui a été relu / validé : voir la
section dédiée de la documentation PDF (`Documentation_TP02.pdf`).

Résumé :
- Toute la coquille du jeu.
- Enrichissement de la fonction d'évaluation `evaluate_board` avec de
  nouveaux critères positionnels (centre, cavalier au bord, tours
  liées, développement, sécurité du roi).
- Ajout d'une profondeur de recherche dynamique selon le nombre de
  pièces restantes.
- Intégration du `tree_logger` dans les fonctions `minmax` /
  `get_best_move_custom` pour alimenter le visualiseur d'arbre.

L'algorythme minmax Alpha-Beta provient de mon travaille

## 9. Limites connues / pistes d'amélioration

- Promotion toujours automatique en Dame (pas de choix de pièce à
  l'écran).
- Pas de gestion de temps limite (timeout) par coup pour l'IA : la
  profondeur dynamique peut rendre certains coups de finale plus
  longs à calculer.
- La fonction d'évaluation reste heuristique et manuelle (pas
  d'apprentissage ni de table de transposition / tri des coups pour
  accélérer l'élagage).
- Pas encore de table de transposition ni de tri des coups
  (move ordering), ce qui limiterait encore l'espace exploré à
  profondeur égale.
- Le rendu des pièces utilise des glyphes unicode ; selon les polices
  disponibles sur la machine, le rendu peut légèrement varier.
- Pas d'interface non graphique (CLI/API) : le jeu nécessite un
  environnement graphique pour Pygame.
