"""
game.py
==========================================================
Boucle de jeu principale : gère les entrées souris, les coups,
l'appel à l'IA sélectionnée, la fin de partie et les statistiques.

Ne contient AUCUNE logique de recherche d'IA : l'appel à votre
algorithme se fait via ai.custom_ai.get_best_move_custom
"""

import sys
import time

import pygame
import chess

import config as cfg
from renderer import Renderer
from ai.custom_ai import get_best_move_custom
from ai.tree_logger import tree_logger
from stats import show_stats_graph
from tree_html_export import export_tree_html


class Game:
    def __init__(self, screen: pygame.Surface, mode: str):
        """
        mode: 'custom' -> l'IA du joueur (MinMax) joue les Noirs
        Le joueur humain joue toujours les Blancs.
        """
        self.screen = screen
        self.mode = mode
        self.renderer = Renderer(screen)
        self.clock = pygame.time.Clock()

        self.board = chess.Board()
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.move_history_san = []
        self.move_times = []  # temps de reflexion de l'IA, un par coup IA
        self.last_ai_time = None
        self.status_text = ""
        self.game_over = False
        self.result_text = ""

    # ------------------------------------------------------------------
    def mode_label(self):
        return "Mon IA (MinMax)"

    # ------------------------------------------------------------------
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    running = self._handle_click(event.pos)

            self._draw()
            self.clock.tick(cfg.FPS)

            if not self.game_over and self.board.turn == chess.BLACK:
                self._play_ai_move()

        return self.mode  # permet de relancer le même mode si besoin

    # ------------------------------------------------------------------
    def _handle_click(self, pos):
        x, y = pos
        if x >= cfg.BOARD_SIZE:
            return self._handle_sidebar_click(pos)

        if self.game_over or self.board.turn != chess.WHITE:
            return True

        col, row = x // cfg.SQUARE_SIZE, y // cfg.SQUARE_SIZE
        square = self.renderer.xy_to_square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.legal_targets = [
                    m.to_square for m in self.board.legal_moves
                    if m.from_square == square
                ]
        else:
            move = self._build_move(self.selected_square, square)
            if move in self.board.legal_moves:
                self._push_move(move)
            self.selected_square = None
            self.legal_targets = []

        return True

    def _handle_sidebar_click(self, pos):
        for label, rect in self._last_button_rects.items():
            if rect.collidepoint(pos):
                if label == "Retour au menu":
                    return False
                if label == "Rejouer":
                    self.__init__(self.screen, self.mode)
                if label == "Statistiques":
                    show_stats_graph(self.move_times, self.mode_label())
                if label == "Voir l'arbre":
                    export_tree_html(tree_logger.get_data())
                if label == "Quitter":
                    self._quit()
        return True

    def _build_move(self, from_sq, to_sq) -> chess.Move:
        piece = self.board.piece_at(from_sq)
        promotion = None
        if piece and piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(to_sq)
            if target_rank in (0, 7):
                promotion = chess.Piece.from_symbol(cfg.AUTO_PROMOTE_TO.upper()).piece_type
        return chess.Move(from_sq, to_sq, promotion=promotion)

    def _push_move(self, move: chess.Move):
        san = self.board.san(move)
        self.board.push(move)
        self.move_history_san.append(san)
        self.last_move = move
        self._check_game_over()

    # ------------------------------------------------------------------
    def _play_ai_move(self):
        self.status_text = "L'IA réfléchit..."
        self._draw()
        pygame.display.flip()

        start = time.time()
        if self.mode == "custom":
            move = get_best_move_custom(self.board, cfg.DEFAULT_DEPTH)
        elapsed = time.time() - start

        self.move_times.append(elapsed)
        self.last_ai_time = elapsed
        self.status_text = ""

        if move is not None and move in self.board.legal_moves:
            self._push_move(move)

    # ------------------------------------------------------------------
    def _check_game_over(self):
        if self.board.is_game_over():
            self.game_over = True
            outcome = self.board.outcome()
            if outcome.winner is None:
                self.result_text = "Partie nulle."
            else:
                winner = "Blancs" if outcome.winner == chess.WHITE else "Noirs"
                self.result_text = f"Victoire des {winner} ({outcome.termination.name})."
            self.status_text = self.result_text

    # ------------------------------------------------------------------
    def _draw(self):
        self.screen.fill((0, 0, 0))
        self.renderer.draw_board(
            self.board,
            selected_square=self.selected_square,
            legal_targets=self.legal_targets,
            last_move=self.last_move,
        )

        buttons = {}
        if self.game_over:
            if self.mode == "custom":
                buttons["Voir l'arbre"] = None
            buttons["Statistiques"] = None
            buttons["Rejouer"] = None
            buttons["Retour au menu"] = None
        else:
            if self.mode == "custom":
                buttons["Voir l'arbre"] = None
            buttons["Retour au menu"] = None

        self._last_button_rects = self.renderer.draw_sidebar(
            self.board,
            self.mode_label(),
            self.move_history_san,
            self.status_text,
            buttons,
            self.last_ai_time,
        )

        pygame.display.flip()

    # ------------------------------------------------------------------
    def _quit(self):
        pygame.quit()
        sys.exit()
