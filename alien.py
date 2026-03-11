import pygame
from pygame.sprite import Sprite
import random

class Alien(Sprite):
    """Egy osztály, amely egyetlen idegent képvisel a flottában."""
    # Settings
    alien_speed: int 
    alien_shoot_intensity: int 
    alien_shoot_damage: int 
    alien_hp: int 

    def __init__(self, screen: pygame.Surface):
        """Az idegen inicializálása és kezdőpozíciójának beállítása."""
        super().__init__() # Egyszerűbb hívás
        self.screen = screen

        # Kép betöltése - Figyelj a perjelre!
        self.image = pygame.image.load('grafika/enemy.png')
        self.rect = self.image.get_rect()

        # Settings
        self.alien_speed: int = 1
        self.alien_shoot_intensity: int = 1
        self.alien_shoot_damage: int = 1
        self.alien_hp: int = 1


        # Kezdőpozíció
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Lebegőpontos pozíció tárolása a pontos mozgáshoz
        self.rect.x = random.randint(0, screen.get_width() - self.rect.width)
        self.rect.y = random.randint(0, 200) # A felső sávban jelenjenek meg
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def check_edges(self):
        """Igazat ad, ha az idegen elérte a képernyő szélét."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True
        return False # Explicit False, ha nincs a szélen

    def mozgas(self):
        """Véletlenszerű mozgás minden irányba."""
        # Generálunk egy kis elmozdulást X és Y irányba is
        # A sebességet a settings-ből vesszük, de véletlen irányba szorozzuk
        sebzes_x = random.uniform(-1, 1) * self.alien_speed
        sebzes_y = random.uniform(-0.5, 0.5) * self.alien_speed

        self.x += sebzes_x
        self.y += sebzes_y

        # Frissítjük a rect pozícióját
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Határok ellenőrzése (hogy ne menjenek ki a képernyőről)
    def check_screen(self):
        screen_rect = self.screen.get_rect()
        
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            self.x -= (self.rect.x - self.rect.x) # Megállítja vagy visszafordíthatod
        if self.rect.bottom >= screen_rect.bottom or self.rect.top <= 0:
            self.y = self.y # Itt is korlátozhatod a függőleges mozgást

    def blitme(self):
        """Kirajzolás."""
        self.screen.blit(self.image, self.rect)