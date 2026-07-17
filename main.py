"""
main.py
==========================================================
Point d'entrée de l'application.
Lance le menu, puis la partie dans le mode choisi, en boucle
jusqu'à ce que l'utilisateur quitte.
"""

import pygame

import config as cfg
from menu import run_menu
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption("Chess - MinMax")
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))

    while True:
        mode = run_menu(screen)
        game = Game(screen, mode)
        game.run()


if __name__ == "__main__":
    main()
