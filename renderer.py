"""
renderer.py
==========================================================
Tout l'affichage pygame : échiquier, pièces (glyphes unicode),
surbrillances, panneau latéral (tour, historique, statut).
Ne fait pas partie du TP (pas de logique IA ici).
"""

import pygame
import chess

import config as cfg

UNICODE_PIECES = {
    (chess.PAWN, chess.WHITE): "\u2659",
    (chess.KNIGHT, chess.WHITE): "\u2658",
    (chess.BISHOP, chess.WHITE): "\u2657",
    (chess.ROOK, chess.WHITE): "\u2656",
    (chess.QUEEN, chess.WHITE): "\u2655",
    (chess.KING, chess.WHITE): "\u2654",
    (chess.PAWN, chess.BLACK): "\u265F",
    (chess.KNIGHT, chess.BLACK): "\u265E",
    (chess.BISHOP, chess.BLACK): "\u265D",
    (chess.ROOK, chess.BLACK): "\u265C",
    (chess.QUEEN, chess.BLACK): "\u265B",
    (chess.KING, chess.BLACK): "\u265A",
}


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._init_fonts()

    def _init_fonts(self):
        # On essaie plusieurs polices système susceptibles de contenir
        # les glyphes d'échecs unicode ; sinon repli sur la police par défaut.
        candidates = ["segoeuisymbol", "dejavusans", "arialunicodems", "freeserif"]
        self.piece_font = None
        for name in candidates:
            try:
                self.piece_font = pygame.font.SysFont(name, int(cfg.SQUARE_SIZE * 0.7))
                if self.piece_font:
                    break
            except Exception:
                continue
        if self.piece_font is None:
            self.piece_font = pygame.font.Font(None, int(cfg.SQUARE_SIZE * 0.7))

        self.ui_font = pygame.font.SysFont("arial", 20)
        self.ui_font_bold = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)

    @staticmethod
    def square_to_xy(square: int, flipped: bool = False):
        """Convertit une case python-chess (0-63) en coordonnées pixel (col, row)."""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if not flipped:
            col = file
            row = 7 - rank
        else:
            col = 7 - file
            row = rank
        return col, row

    @staticmethod
    def xy_to_square(col: int, row: int, flipped: bool = False) -> int:
        if not flipped:
            file = col
            rank = 7 - row
        else:
            file = 7 - col
            rank = row
        return chess.square(file, rank)

    def draw_board(self, board: chess.Board, selected_square=None,
                    legal_targets=None, last_move=None, flipped=False):
        legal_targets = legal_targets or []

        # Cases
        for square in chess.SQUARES:
            col, row = self.square_to_xy(square, flipped)
            x, y = col * cfg.SQUARE_SIZE, row * cfg.SQUARE_SIZE
            is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
            color = cfg.COLOR_LIGHT if is_light else cfg.COLOR_DARK

            if last_move and square in (last_move.from_square, last_move.to_square):
                color = cfg.COLOR_LAST_MOVE
            if selected_square == square:
                color = cfg.COLOR_SELECTED

            pygame.draw.rect(self.screen, color, (x, y, cfg.SQUARE_SIZE, cfg.SQUARE_SIZE))

            if board.is_check() and board.piece_type_at(square) == chess.KING \
                    and board.piece_at(square) and board.piece_at(square).color == board.turn:
                pygame.draw.rect(self.screen, cfg.COLOR_CHECK,
                                  (x, y, cfg.SQUARE_SIZE, cfg.SQUARE_SIZE), 4)

        # Points de coups légaux
        for target in legal_targets:
            col, row = self.square_to_xy(target, flipped)
            cx = col * cfg.SQUARE_SIZE + cfg.SQUARE_SIZE // 2
            cy = row * cfg.SQUARE_SIZE + cfg.SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, cfg.COLOR_LEGAL_MOVE, (cx, cy), 12)

        # Pièces
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            col, row = self.square_to_xy(square, flipped)
            x, y = col * cfg.SQUARE_SIZE, row * cfg.SQUARE_SIZE
            glyph = UNICODE_PIECES[(piece.piece_type, piece.color)]
            text_color = cfg.COLOR_WHITE_PIECE if piece.color == chess.WHITE else cfg.COLOR_BLACK_PIECE
            surf = self.piece_font.render(glyph, True, text_color)
            rect = surf.get_rect(center=(x + cfg.SQUARE_SIZE // 2, y + cfg.SQUARE_SIZE // 2))
            self.screen.blit(surf, rect)

        # Coordonnées (a-h, 1-8)
        for i in range(8):
            file_letter = chr(ord('a') + (7 - i if flipped else i))
            label = self.small_font.render(file_letter, True, cfg.COLOR_TEXT_DIM)
            self.screen.blit(label, (i * cfg.SQUARE_SIZE + 4, cfg.BOARD_SIZE - 18))

            rank_number = str(i + 1 if flipped else 8 - i)
            label = self.small_font.render(rank_number, True, cfg.COLOR_TEXT_DIM)
            self.screen.blit(label, (4, i * cfg.SQUARE_SIZE + 2))

    def draw_sidebar(self, board: chess.Board, mode_label: str, move_history,
                      status_text: str, buttons: dict, last_ai_time=None):
        x0 = cfg.BOARD_SIZE
        pygame.draw.rect(self.screen, cfg.COLOR_BG_SIDEBAR,
                          (x0, 0, cfg.SIDEBAR_WIDTH, cfg.HEIGHT))

        pad = 16
        y = pad

        title = self.ui_font_bold.render("Chess AI", True, cfg.COLOR_TEXT)
        self.screen.blit(title, (x0 + pad, y))
        y += 36

        mode = self.ui_font.render(f"Mode : {mode_label}", True, cfg.COLOR_TEXT_DIM)
        self.screen.blit(mode, (x0 + pad, y))
        y += 28

        turn_str = "Blancs" if board.turn == chess.WHITE else "Noirs"
        turn = self.ui_font.render(f"Trait : {turn_str}", True, cfg.COLOR_TEXT)
        self.screen.blit(turn, (x0 + pad, y))
        y += 28

        if last_ai_time is not None:
            t = self.small_font.render(f"Dernier coup IA : {last_ai_time:.2f}s",
                                        True, cfg.COLOR_TEXT_DIM)
            self.screen.blit(t, (x0 + pad, y))
            y += 24

        status = self.small_font.render(status_text, True, (255, 210, 120))
        self.screen.blit(status, (x0 + pad, y))
        y += 32

        # Historique des coups
        hist_title = self.ui_font.render("Historique", True, cfg.COLOR_TEXT)
        self.screen.blit(hist_title, (x0 + pad, y))
        y += 26

        max_lines = 14
        recent = move_history[-max_lines:]
        for i, san in enumerate(recent):
            line = self.small_font.render(san, True, cfg.COLOR_TEXT_DIM)
            self.screen.blit(line, (x0 + pad, y))
            y += 20

        # Boutons (en bas)
        mouse_pos = pygame.mouse.get_pos()
        rects = {}
        by = cfg.HEIGHT - pad - 40
        for label in reversed(list(buttons.keys())):
            rect = pygame.Rect(x0 + pad, by, cfg.SIDEBAR_WIDTH - 2 * pad, 34)
            hovered = rect.collidepoint(mouse_pos)
            color = cfg.COLOR_BUTTON_HOVER if hovered else cfg.COLOR_BUTTON
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            text = self.ui_font.render(label, True, cfg.COLOR_TEXT)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            rects[label] = rect
            by -= 44

        return rects
