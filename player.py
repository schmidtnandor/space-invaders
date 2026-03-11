import pygame
from bullet import Bullet  # imported here to allow precise typing


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Kép betöltése és optimalizálása
        self.image = pygame.image.load("grafika/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect()

        # Kezdőpozíció: lent, középen
        self.rect.midbottom = (screen_width // 2, screen_height - 50)
        self.speed = 15

        # hitbox used for collision checks (smaller than the visible sprite)
        self.hitbox = self.rect.inflate(-10, -70)

        # group that holds bullets this player has fired
        # `Group` typing is imperfect in pygame stubs; ignore the assignment error
        self.bullets: pygame.sprite.Group[Bullet] = pygame.sprite.Group()  # type: ignore[assignment]

    def check_input(self):
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT] and self.rect.left > 25:
            self.rect.x -= self.speed
            moved = True
        if keys[pygame.K_RIGHT] and self.rect.right < self.screen_width - 25:
            self.rect.x += self.speed
            moved = True

        # if we changed position, move the hitbox as well
        if moved:
            self.hitbox.center = self.rect.center

    def shoot(self):
        """Create a bullet travelling upwards from the player's gun.

        The player itself doesn't know anything about the game screen; it
        simply returns a new :class:`Bullet` instance.  The caller is
        responsible for adding it to a group and drawing/updating it.
        """
        from bullet import Bullet

        bullet = Bullet(self.rect.centerx, self.rect.top + 50)
        self.bullets.add(bullet)
        return bullet
