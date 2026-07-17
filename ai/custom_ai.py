import random
import chess

from ai.tree_logger import tree_logger

# ######## CODE IA (Claude) #########
"""
Prompt: 
Modifie mon evaluation de l'echequier pour qu'elle prenne en compte les points suivants:
récompenser quand les pions prennent le centre
punir quand le cavalier est au bord de l'echequier
recompenser quand les tours sont liées
recompenser quand toutes les pieces sont développées
recompenser quand le roi est à l'abri (roqué avec des pions devant lui)
"""
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]
EXTENDED_CENTER = [chess.C3, chess.C4, chess.C5, chess.C6,
                    chess.D3, chess.D6, chess.E3, chess.E6,
                    chess.F3, chess.F4, chess.F5, chess.F6]

# Cases de départ, pour détecter si une pièce a "développé" ou non
STARTING_SQUARES = {
    chess.WHITE: {
        chess.KNIGHT: [chess.B1, chess.G1],
        chess.BISHOP: [chess.C1, chess.F1],
    },
    chess.BLACK: {
        chess.KNIGHT: [chess.B8, chess.G8],
        chess.BISHOP: [chess.C8, chess.F8],
    },
}

RIM_FILES = [chess.A, chess.H] if hasattr(chess, "A") else [0, 7]  # fallback si besoin

MATE_SCORE = 100000

def _is_on_rim(square: int) -> bool:
    file = chess.square_file(square)   # 0=a ... 7=h
    rank = chess.square_rank(square)   # 0=1ère rangée ... 7=8e rangée
    return file == 0 or file == 7 or rank == 0 or rank == 7


def _material_score(board: chess.Board) -> float:
    values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0,
    }
    score = 0
    for piece_type, value in values.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def _center_control_score(board: chess.Board) -> float:
    score = 0
    for square in CENTER_SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            score += 0.30 if piece.color == chess.WHITE else -0.30
    for square in EXTENDED_CENTER:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            score += 0.10 if piece.color == chess.WHITE else -0.10
    return score


def _knight_rim_penalty(board: chess.Board) -> float:
    score = 0
    for color in (chess.WHITE, chess.BLACK):
        for square in board.pieces(chess.KNIGHT, color):
            if _is_on_rim(square):
                score += -0.25 if color == chess.WHITE else 0.25
    return score


def _connected_rooks_score(board: chess.Board) -> float:
    """Bonus si les 2 tours d'une couleur se voient (même rangée ou
    colonne, sans pièce entre elles)."""
    score = 0
    for color in (chess.WHITE, chess.BLACK):
        rooks = list(board.pieces(chess.ROOK, color))
        if len(rooks) != 2:
            continue
        r1, r2 = rooks
        same_rank = chess.square_rank(r1) == chess.square_rank(r2)
        same_file = chess.square_file(r1) == chess.square_file(r2)
        if same_rank or same_file:
            between = chess.SquareSet(chess.between(r1, r2))
            if not any(board.piece_at(sq) for sq in between):
                score += 0.30 if color == chess.WHITE else -0.30
    return score


def _development_score(board: chess.Board) -> float:
    """Bonus par cavalier/fou qui a quitté sa case de départ."""
    score = 0
    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        for piece_type, starts in STARTING_SQUARES[color].items():
            for start_square in starts:
                piece = board.piece_at(start_square)
                still_there = piece and piece.piece_type == piece_type and piece.color == color
                if not still_there:
                    score += sign * 0.20
    return score


def _king_safety_score(board: chess.Board) -> float:
    """Bonus si le roi est roqué (déplacé sur g/c) avec des pions
    devant lui ; malus s'il est encore au centre en milieu de partie."""
    score = 0
    total_pieces = len(board.piece_map())
    midgame_or_later = total_pieces <= 28  # heuristique grossière

    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1
        king_square = board.king(color)
        if king_square is None:
            continue
        king_file = chess.square_file(king_square)

        castled = king_file in (2, 6)  # colonnes c ou g
        if castled:
            score += sign * 0.40
        elif midgame_or_later and king_file == 4:  # encore sur e1/e8
            score -= sign * 0.30

        # Bouclier de pions devant le roi
        shield_files = [f for f in (king_file - 1, king_file, king_file + 1) if 0 <= f <= 7]
        shield_rank = 1 if color == chess.WHITE else 6
        shield_count = 0
        for f in shield_files:
            sq = chess.square(f, shield_rank)
            piece = board.piece_at(sq)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                shield_count += 1
        score += sign * 0.10 * shield_count

    return score


def evaluate_board(board: chess.Board) -> float:

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or \
       board.can_claim_fifty_moves() or board.is_repetition():
        return 0

    return (
        _material_score(board)
        + _center_control_score(board)
        + _knight_rim_penalty(board)
        + _connected_rooks_score(board)
        + _development_score(board)
        + _king_safety_score(board)
    )
# ########################################

### code IA (Claude) ###
"""
Prompt:
Tu peux augmenter la profondeur en fonction du nombre de pieces qu'il reste sur l'echequier stp
"""
def get_dynamic_depth(board: chess.Board, base_depth: int = 3, max_depth: int = 6) -> int:
    """Augmente la profondeur de recherche quand il reste peu de pièces
    (l'espace de recherche est plus petit en finale)."""
    piece_count = len(board.piece_map())

    if piece_count > 20:      # ouverture / début de milieu de jeu
        return base_depth
    elif piece_count > 12:    # milieu de jeu
        return base_depth + 1
    elif piece_count > 6:     # début de finale
        return base_depth + 2
    else:                     # finale avancée
        return max_depth
###

def get_best_move_custom(board: chess.Board, depth: int = 3, alpha: float = float("-inf"), beta: float = float("inf"), joueur_max: bool = True) -> chess.Move:
    """
    Retourne le meilleur coup pour le joueur actuel (blanc ou noir)
    en utilisant l'algorithme MinMax avec élagage Alpha-Beta.
    """
    depth = get_dynamic_depth(board, base_depth=depth)
    ### CODE IA (Claude) ###
    tree_logger.reset()
    ###

    joueur_max = board.turn == chess.WHITE
    meilleur_coup = None
    meilleure_valeur = float("-inf") if joueur_max else float("inf")

    ### CODE IA (Claude) ###
    root_id = tree_logger.new_node(None, depth, float("-inf"), float("inf"), joueur_max)
    ###


    for move in board.legal_moves:
        board.push(move)
        valeur = minmax(board, depth - 1, float("-inf"), float("inf"), not joueur_max, root_id, move)
        board.pop()

        if joueur_max and valeur > meilleure_valeur:
            meilleure_valeur = valeur
            meilleur_coup = move
        elif not joueur_max and valeur < meilleure_valeur:
            meilleure_valeur = valeur
            meilleur_coup = move

        ### CODE IA (Claude) ###
        tree_logger.update_node(root_id, score=meilleure_valeur)
        ###
    return meilleur_coup


def minmax(board: chess.Board, depth: int, alpha: float, beta: float, joueur_max: bool, parent_id: int = None, move: chess.Move = None) -> float:
    """
    Implémentation de l'algorithme MinMax avec élagage Alpha-Beta
    pour évaluer les positions d'échecs.
    """

    ### CODE IA (Claude) ###
    node_id = tree_logger.new_node(parent_id, depth, alpha, beta, joueur_max, move)
    ###

    if depth == 0 or board.is_game_over():
        score = evaluate_board(board)

        ### CODE IA (Claude) ###
        tree_logger.update_node(node_id, score=score)
        ###
        
        return score
    
    #### CODE IA (Claude) ###
    node_id = tree_logger.new_node(parent_id, depth, alpha, beta, joueur_max, move)
    ####
    
    if joueur_max:
        best_move = float("-inf")
        for move in board.legal_moves:
            board.push(move)
            valeur = minmax(board, depth - 1, alpha, beta, False, node_id, move)
            board.pop()
            best_move = max(best_move, valeur)
            alpha = max(alpha, valeur)

            ### CODE IA (Claude) ###
            tree_logger.update_node(node_id, alpha=alpha, beta=beta, score=best_move)
            ###

            if alpha >= beta:
                break
        return best_move
    else:
        best_move = float("inf")
        for move in board.legal_moves:
            board.push(move)
            valeur = minmax(board, depth - 1, alpha, beta, True, node_id, move)
            board.pop()
            best_move = min(best_move, valeur)
            beta = min(beta, valeur)
            
            ### CODE IA (Claude) ###
            tree_logger.update_node(node_id, alpha=alpha, beta=beta, score=best_move)
            ###

            if alpha >= beta:
                break
        return best_move

