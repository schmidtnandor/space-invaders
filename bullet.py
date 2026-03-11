import pygame


class Bullet(pygame.sprite.Sprite):
    """A small projectile fired by the player.

    The bullet moves straight up and destroys itself when it leaves the
    top of the screen.  It is a simple white rectangle by default but you
    can swap in an image or add more behaviour later.
    """

    def __init__(self, x: int, y: int, speed: int = 15) -> None:
        super().__init__()
        # very simple representation for now
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def update(self) -> None:
        # move the bullet upward and kill it when it leaves the screen
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()
