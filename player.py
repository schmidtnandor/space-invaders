import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Kép betöltése és optimalizálása
        # A 'player.png' helyett írd be a saját fájlod nevét!
        self.image = pygame.image.load("grafika/player.png").convert_alpha()

        # Ha túl nagy a kép, itt átméretezheted (pl. 50x50 pixelre)
        self.image = pygame.transform.scale(self.image, (50, 50))

        self.rect = self.image.get_rect()

        # Kezdőpozíció: lent, középen
        self.rect.midbottom = (1920 // 2, 1080 - 10)
        self.speed = 5

    def check_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 1920:
            self.rect.x += self.speed
