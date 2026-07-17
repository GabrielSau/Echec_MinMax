"""
tree_visualizer.py
==========================================================
Affiche l'arbre de recherche enregistré par ai.tree_logger.

Ne fait pas partie du TP (pas de logique MinMax ici) : ce module
se contente de dessiner les noeuds/coups/valeurs alpha-beta que
VOTRE algorithme a enregistrés via TreeLogger.

Comme l'arbre complet d'un MinMax est en général bien trop grand
pour être lisible, l'affichage :
  - se limite à une profondeur maximale (max_depth_display),
  - se limite à un nombre de noeuds maximal (max_nodes_display),
  - indique clairement si l'arbre affiché est partiel/tronqué,
  - met en évidence les branches/noeuds concernés par l'élagage.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


def _annotate_depth_from_root(nodes, root_id):
    """Ajoute 'depth_from_root' (0 = racine) à chaque noeud, calculé par
    parcours du graphe (indépendant de la profondeur restante passée
    à minimax, qui peut varier selon votre implémentation)."""
    if root_id is None or root_id not in nodes:
        return
    stack = [(root_id, 0)]
    while stack:
        node_id, d = stack.pop()
        nodes[node_id]["depth_from_root"] = d
        for child_id in nodes[node_id]["children"]:
            if child_id in nodes:
                stack.append((child_id, d + 1))


def _collect_visible(nodes, root_id, max_depth_display, max_nodes_display):
    """Sélectionne un sous-ensemble lisible de l'arbre à afficher."""
    visible = {}
    order = []

    def recurse(node_id):
        if node_id not in nodes or len(visible) >= max_nodes_display:
            return
        node = nodes[node_id]
        if node["depth_from_root"] > max_depth_display:
            return
        visible[node_id] = node
        order.append(node_id)
        for child_id in node["children"]:
            if len(visible) >= max_nodes_display:
                break
            recurse(child_id)

    recurse(root_id)
    return visible, order


def _layout(visible, root_id):
    """Calcule une position (x, y) par noeud pour un affichage en arbre."""
    positions = {}
    leaf_x = [0]

    def recurse(node_id):
        node = visible[node_id]
        children = [c for c in node["children"] if c in visible]
        if not children:
            x = leaf_x[0]
            leaf_x[0] += 1
        else:
            xs = [recurse(c) for c in children]
            x = sum(xs) / len(xs)
        positions[node_id] = (x, -node["depth_from_root"])
        return x

    recurse(root_id)
    return positions


def _fmt(value):
    if value == float("-inf"):
        return "-inf"
    if value == float("inf"):
        return "inf"
    if isinstance(value, (int, float)):
        return f"{value:.1f}"
    return "?"


def show_tree(tree_data, max_depth_display: int = 4, max_nodes_display: int = 120):
    """
    tree_data : tuple (nodes, root_id, truncated) tel que renvoyé par
                ai.tree_logger.TreeLogger.get_data()
    """
    nodes, root_id, was_truncated_during_search = tree_data

    if root_id is None or not nodes:
        print("Aucun arbre à afficher (lancez une partie contre 'Mon IA' d'abord).")
        return

    _annotate_depth_from_root(nodes, root_id)
    visible, order = _collect_visible(nodes, root_id, max_depth_display, max_nodes_display)
    positions = _layout(visible, root_id)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Arêtes : rouge en pointillés quand le noeud ENFANT correspond à
    # une branche qui a été coupée par le parent (élagage).
    for node_id in order:
        node = visible[node_id]
        x1, y1 = positions[node_id]
        for child_id in node["children"]:
            if child_id not in visible:
                continue
            x2, y2 = positions[child_id]
            pruned_edge = node["pruned"] and child_id == node["children"][-1]
            color = "#888888"
            style = "-"
            ax.plot([x1, x2], [y1, y2], color=color, linestyle=style,
                    linewidth=1.2, zorder=1)

    # Repère visuel sous les noeuds où l'élagage a eu lieu
    for node_id in order:
        node = visible[node_id]
        if node["pruned"]:
            x, y = positions[node_id]
            ax.text(x, y - 0.33, "✂ coupé (β≤α)", color="#d94f4f", fontsize=7,
                    ha="center", va="top", style="italic")

    # Noeuds
    for node_id in order:
        node = visible[node_id]
        x, y = positions[node_id]
        is_max = node["maximizing"]
        face = "#3b6fa0" if is_max else "#a04b3b"
        if node["pruned"]:
            face = "#6f6f6f"

        box = mpatches.FancyBboxPatch(
            (x - 0.42, y - 0.22), 0.84, 0.44,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1, edgecolor="black", facecolor=face, alpha=0.92, zorder=2,
        )
        ax.add_patch(box)

        label = f"a={_fmt(node['alpha'])} b={_fmt(node['beta'])}\nscore={_fmt(node['score'])}"
        ax.text(x, y, label, ha="center", va="center", fontsize=7,
                color="white", zorder=3)

        if node["move"]:
            ax.text(x, y + 0.30, node["move"], ha="center", va="bottom",
                    fontsize=7, color="#333333", zorder=3)

    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 0.8, 1)
    ax.axis("off")

    title = "Arbre de recherche MinMax / Alpha-Beta"
    truncated = was_truncated_during_search or len(visible) < len(nodes)
    if truncated:
        title += f"  (affichage partiel : {len(visible)}/{len(nodes)} noeuds, profondeur <= {max_depth_display})"
    ax.set_title(title, fontsize=12)

    legend_elems = [
        mpatches.Patch(facecolor="#3b6fa0", edgecolor="black", label="Noeud MAX"),
        mpatches.Patch(facecolor="#a04b3b", edgecolor="black", label="Noeud MIN"),
        mpatches.Patch(facecolor="#6f6f6f", edgecolor="black", label="Noeud avec branche coupée"),
        Line2D([0], [0], color="#d94f4f", label="Elagage signalé (voir 'coupé')", linestyle="--"),
    ]
    ax.legend(handles=legend_elems, loc="upper right", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    plt.show()
