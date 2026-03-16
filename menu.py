import pygame
import pygame_menu

from Game import Game


class Menu:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))
        menu_surface = pygame.display.get_surface()
        menu = pygame_menu.Menu(
            "Welcome", 1200, 800, theme=pygame_menu.themes.THEME_GREEN
        )
        menu.add.button("Play", self.start_game)
        menu.add.button("Quit", pygame_menu.events.EXIT)
        menu.mainloop(menu_surface)

    def start_game(self):
        game = Game()
        game.run()
