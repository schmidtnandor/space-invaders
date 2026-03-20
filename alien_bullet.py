"""Alien bullet sprite implementation."""
# pylint: disable=too-few-public-methods

import pygame


class AlienBullet(pygame.sprite.Sprite):
    """A projectile fired downward by an alien."""

    def __init__(self, x: int, y: int, speed: int = 8) -> None:
        super().__init__()
        # Simple red rectangle for alien bullets
        self.image = pygame.Surface((7, 27))
        self.image.fill((255, 100, 100))  # Red color
        self.rect = self.image.get_rect(midtop=(x, y))
        self.speed = speed

    def update(self) -> None:
        """Move the bullet downward and remove it after leaving the screen."""
        self.rect.y += self.speed
        if self.rect.top > 1200:  # Screen height
            self.kill()
