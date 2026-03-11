import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        # Kép betöltése és optimalizálása
        # A 'player.png' helyett írd be a saját fájlod nevét!
        self.image = pygame.image.load('grafika/player.png').convert_alpha()
        
        # Ha túl nagy a kép, itt átméretezheted (pl. 50x50 pixelre)
        self.image = pygame.transform.scale(self.image, (50, 50))
        
        self.rect = self.image.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Kezdőpozíció: lent, középen
        self.rect.midbottom = (screen_width // 2, screen_height - 10)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < self.screen_width:
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)