"""Alien bullet sprite implementation."""

# pylint: disable=too-few-public-methods

import pygame
from config import Config


class AlienBullet(pygame.sprite.Sprite):
    """A projectile fired downward by an alien."""

    config: Config = Config()
    _image: pygame.Surface
    _rect: pygame.Rect
    _speed: int

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        # Simple red rectangle for alien bullets
        self._image: pygame.Surface = pygame.Surface((7, 27))
        self._image.fill((255, 100, 100))  # Red color
        self._rect: pygame.Rect = self._image.get_rect(midtop=(x, y))
        self._speed: int = self.config.alien_bullet_speed

    def update(self) -> None:
        """Move the bullet downward and remove it after leaving the screen."""
        self._rect.y += self._speed
        if self._rect.top > self.config.screen_height:
            self.kill()
