"""Game menu entry point."""

# pylint: disable=invalid-name,no-member,too-few-public-methods
from typing import Any

import pygame
import pygame_menu
from pygame_menu import events, font
from pygame_menu.widgets.widget.menubar import MENUBAR_STYLE_NONE
from Game import Game
from config import Config


class Menu:
    config: Config = Config()

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_mode((self.config.screen_width, self.config.screen_height))
        menu_surface: pygame.Surface = pygame.display.get_surface()
        custom_theme: pygame_menu.Theme = pygame_menu.Theme(
            background_color=(0, 0, 0),
            title_bar_style=MENUBAR_STYLE_NONE,
            widget_font=font.FONT_MUNRO,
        )
        menu: Any = pygame_menu.Menu(
            title="",
            width=self.config.screen_width,
            height=self.config.screen_height,
            theme=custom_theme,
        )
        menu.add.label("SPACE INVADERS", font_size=100, font_color=(255, 255, 255))
        menu.add.image("grafika/enemy.png", scale=(1.0, 1.0))
        menu.add.button("Play", self.start_game, font_size=50)
        menu.add.button("Quit", events.EXIT, font_size=50)
        menu.mainloop(menu_surface)

    def start_game(self) -> None:
        game: Game = Game()
        game.run()

        # After game over, restore menu window size and state.
        pygame.display.set_mode((self.config.screen_width, self.config.screen_height))
