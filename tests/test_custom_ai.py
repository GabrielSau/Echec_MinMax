"""
tests/test_custom_ai.py
==========================================================
Squelette de tests unitaires pour votre algorithme MinMax.

Ce fichier ne fait QUE vérifier que la fonction renvoie bien un
coup légal, pour que le test passe même avec le placeholder actuel.

>>> C'est à VOUS d'ajouter des tests qui vérifient le comportement
    réel de votre MinMax / Alpha-Beta, par exemple :
    - trouve un mat en 1 coup quand il existe,
    - préfère une prise de dame gratuite à un coup neutre,
    - l'élagage alpha-beta donne le même résultat que minimax pur
      (mais en visitant moins de noeuds),
    - le temps de calcul reste raisonnable à une profondeur donnée.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chess
from ai.custom_ai import get_best_move_custom


def test_returns_legal_move_from_start_position():
    board = chess.Board()
    move = get_best_move_custom(board, depth=2)
    assert move in board.legal_moves


def test_returns_legal_move_mid_game():
    board = chess.Board()
    for san in ["e4", "e5", "Nf3", "Nc6", "Bb5"]:
        board.push_san(san)
    move = get_best_move_custom(board, depth=2)
    assert move in board.legal_moves


# TODO (étudiant) : ajoutez ici vos propres tests sur la logique
# MinMax / Alpha-Beta une fois votre algorithme implémenté.
