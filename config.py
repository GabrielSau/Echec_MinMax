# ==========================================================
# config.py - Paramètres globaux de l'application
# ==========================================================

# --- Fenêtre / affichage ---
WIDTH, HEIGHT = 900, 640
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
SIDEBAR_WIDTH = WIDTH - BOARD_SIZE
FPS = 60

# --- Couleurs ---
COLOR_LIGHT = (240, 217, 181)
COLOR_DARK = (181, 136, 99)
COLOR_SELECTED = (186, 202, 68)
COLOR_LEGAL_MOVE = (100, 100, 100)
COLOR_LAST_MOVE = (246, 246, 105)
COLOR_CHECK = (220, 80, 80)
COLOR_BG_SIDEBAR = (24, 24, 24)
COLOR_TEXT = (235, 235, 235)
COLOR_TEXT_DIM = (150, 150, 150)
COLOR_BUTTON = (60, 60, 60)
COLOR_BUTTON_HOVER = (90, 90, 90)
COLOR_WHITE_PIECE = (250, 250, 250)
COLOR_BLACK_PIECE = (20, 20, 20)

# --- IA ---
DEFAULT_DEPTH = 3          # profondeur passée à votre algorithme MinMax

# --- Promotion automatique ---
# Pour rester simple, toute promotion de pion se fait automatiquement en Dame.
AUTO_PROMOTE_TO = "q"
