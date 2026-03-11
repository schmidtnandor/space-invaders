import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """Egy osztály, amely egyetlen idegent képvisel a flottában."""

    def __init__(self, ai_settings: Settings, screen: pygame.Surface):
        """Az idegen inicializálása és kezdőpozíciójának beállítása."""
        super().__init__() # Egyszerűbb hívás
        self.screen = screen
        self.ai_settings = ai_settings

        # Kép betöltése - Figyelj a perjelre!
        self.image = pygame.image.load('grafika/enemy.png')
        self.rect = self.image.get_rect()

        # Kezdőpozíció
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Lebegőpontos pozíció tárolása a pontos mozgáshoz
        self.x = float(self.rect.x)

    def check_edges(self):
        """Igazat ad, ha az idegen elérte a képernyő szélét."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True
        return False # Explicit False, ha nincs a szélen

    def update(self):
        """Mozgatás jobbra vagy balra."""
        self.x += (self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction)
        self.rect.x = int(self.x) # Konvertáljuk egész számmá a rect számára

    def blitme(self):
        """Kirajzolás."""
        self.screen.blit(self.image, self.rect)