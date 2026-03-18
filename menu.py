"""Game menu entry point."""

# pylint: disable=invalid-name,no-member,too-few-public-methods

import pygame
import pygame_menu

from Game import Game


class Menu:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))
        menu_surface = pygame.display.get_surface()

        custom_theme = pygame_menu.Theme(
            background_color=(0, 0, 0),
            title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
            widget_font=pygame_menu.font.FONT_MUNRO,
        )
        menu = pygame_menu.Menu(title="", width=1200, height=800, theme=custom_theme)

        menu.add.label("SPACE INVADERS", font_size=100, font_color=(255, 255, 255))
        menu.add.image("grafika/enemy.png", scale=(1.0, 1.0))
        menu.add.button("Play", self.start_game, font_size=50)
        menu.add.button("Quit", pygame_menu.events.EXIT, font_size=50)
        menu.mainloop(menu_surface)

    def start_game(self):
        game = Game()
        game.run()

        # After game over, restore menu window size and state.
        pygame.display.set_mode((1200, 800))
