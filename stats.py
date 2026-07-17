"""
stats.py
==========================================================
Graphique de statistiques post-partie (temps de reflexion de
l'IA par coup), affiché avec matplotlib.
"""

import matplotlib.pyplot as plt


def show_stats_graph(move_times, mode_label: str):
    if not move_times:
        print("Aucune donnée à afficher (aucun coup IA joué).")
        return

    moves = list(range(1, len(move_times) + 1))

    plt.figure(figsize=(8, 5))
    plt.plot(moves, move_times, marker="o", color="#4c72b0")
    plt.title(f"Temps de reflexion par coup - {mode_label}")
    plt.xlabel("Numéro du coup IA")
    plt.ylabel("Temps (secondes)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
