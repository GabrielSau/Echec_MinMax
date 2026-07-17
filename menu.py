"""
menu.py
==========================================================
Menu principal : choix de l'adversaire (votre IA MinMax) avant de lancer une partie.
"""

import sys
import pygame

import config as cfg


class Button:
    def __init__(self, rect, label, value):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = value

    def draw(self, screen, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        color = cfg.COLOR_BUTTON_HOVER if hovered else cfg.COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (90, 90, 90), self.rect, 2, border_radius=10)
        text = font.render(self.label, True, cfg.COLOR_TEXT)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


def run_menu(screen: pygame.Surface) -> str:
    """
    Affiche le menu principal et retourne le mode choisi :
    'custom'  -> jouer contre l'algorithme MinMax du joueur
    """
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 46, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 20)
    button_font = pygame.font.SysFont("arial", 26)

    center_x = cfg.WIDTH // 2
    buttons = [
        Button((center_x - 180, 280, 360, 60), "Jouer contre mon IA (MinMax)", "custom"),
        Button((center_x - 180, 440, 360, 60), "Quitter", "quit"),
    ]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.rect.collidepoint(event.pos):
                        if b.value == "quit":
                            pygame.quit()
                            sys.exit()
                        return b.value

        screen.fill((18, 18, 18))

        title = title_font.render("Chess - MinMax", True, cfg.COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(center_x, 150)))

        subtitle = subtitle_font.render(
            "Choisissez votre adversaire", True, cfg.COLOR_TEXT_DIM)
        screen.blit(subtitle, subtitle.get_rect(center=(center_x, 200)))

        for b in buttons:
            b.draw(screen, button_font, mouse_pos)

        pygame.display.flip()
        clock.tick(cfg.FPS)
