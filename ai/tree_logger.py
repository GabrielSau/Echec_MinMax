"""
ai/tree_logger.py
==========================================================
OUTIL DE VISUALISATION - ne fait pas partie du TP lui-même.

Ce module vous permet d'enregistrer, au fil de l'exécution de
VOTRE algorithme MinMax / Alpha-Beta, les informations nécessaires
pour ensuite afficher l'arbre de recherche : valeurs alpha/beta à
chaque noeud, coup joué, score, et branches coupées (élagage).

Vous n'êtes pas obligés de l'utiliser, mais si vous voulez le
bouton "Voir l'arbre" du menu latéral, voici comment brancher
votre code dessus.

------------------------------------------------------------------
EXEMPLE D'UTILISATION dans ai/custom_ai.py :

    from ai.tree_logger import tree_logger

    def minimax(board, depth, alpha, beta, maximizing, parent_id=None, move=None):
        node_id = tree_logger.new_node(parent_id, depth, alpha, beta,
                                        maximizing, move)

        if depth == 0 or board.is_game_over():
            score = evaluate_board(board)
            tree_logger.update_node(node_id, score=score)
            return score

        best = float("-inf") if maximizing else float("inf")
        for m in board.legal_moves:
            board.push(m)
            score = minimax(board, depth - 1, alpha, beta, not maximizing,
                             node_id, m)
            board.pop()

            if maximizing:
                best = max(best, score)
                alpha = max(alpha, score)
            else:
                best = min(best, score)
                beta = min(beta, score)

            tree_logger.update_node(node_id, alpha=alpha, beta=beta, score=best)

            if beta <= alpha:
                tree_logger.mark_pruned(node_id)   # <-- signale l'élagage
                break

        return best


    def get_best_move_custom(board, depth=3):
        tree_logger.reset()                        # <-- vider l'arbre précédent
        root_id = tree_logger.new_node(None, depth, float("-inf"),
                                        float("inf"), board.turn == chess.WHITE)
        ... votre recherche du meilleur coup, en passant root_id ...
        return best_move
------------------------------------------------------------------
"""

import itertools


class TreeLogger:
    """Enregistre les noeuds explorés par une recherche MinMax/Alpha-Beta.

    Chaque noeud est un dict :
        {
            "id": int,
            "parent": int | None,
            "depth": int,
            "alpha": float,
            "beta": float,
            "maximizing": bool,
            "move": str | None,   # coup (SAN/UCI) qui mène à ce noeud
            "score": float | None,
            "pruned": bool,       # True si on a coupé APRES ce noeud
            "children": [int, ...],
        }
    """

    def __init__(self, max_nodes: int = 4000):
        self.max_nodes = max_nodes
        self.reset()

    def reset(self):
        self.nodes = {}
        self.root_id = None
        self._counter = itertools.count()
        self._truncated = False

    def enabled(self) -> bool:
        return len(self.nodes) < self.max_nodes

    def new_node(self, parent_id, depth, alpha, beta, maximizing, move=None) -> int:
        if not self.enabled():
            self._truncated = True
            return parent_id if parent_id is not None else -1

        node_id = next(self._counter)
        move_str = str(move) if move is not None else None
        self.nodes[node_id] = {
            "id": node_id,
            "parent": parent_id,
            "depth": depth,
            "alpha": alpha,
            "beta": beta,
            "maximizing": maximizing,
            "move": move_str,
            "score": None,
            "pruned": False,
            "children": [],
        }
        if parent_id is not None and parent_id in self.nodes:
            self.nodes[parent_id]["children"].append(node_id)
        if self.root_id is None:
            self.root_id = node_id
        return node_id

    def update_node(self, node_id, alpha=None, beta=None, score=None):
        node = self.nodes.get(node_id)
        if node is None:
            return
        if alpha is not None:
            node["alpha"] = alpha
        if beta is not None:
            node["beta"] = beta
        if score is not None:
            node["score"] = score

    def mark_pruned(self, node_id):
        node = self.nodes.get(node_id)
        if node is not None:
            node["pruned"] = True

    def get_data(self):
        """Retourne (nodes_dict, root_id, truncated_bool)."""
        return self.nodes, self.root_id, self._truncated


# Instance partagée, prête à être importée directement :
#   from ai.tree_logger import tree_logger
tree_logger = TreeLogger()
