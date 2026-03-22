# pylint: disable=no-member,too-few-public-methods

import pygame
from config import Config


class Bullet(pygame.sprite.Sprite):

    _config: Config = Config()
    _image: pygame.Surface
    _rect: pygame.Rect
    _speed: int

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        # very simple representation for now
        self._image: pygame.Surface = pygame.Surface((5, 15))
        self._image.fill((255, 255, 255))
        self._rect: pygame.Rect = self._image.get_rect(midbottom=(x, y))
        self._speed = self._config.bullet_speed

    def update(self) -> None:
        """Move the player bullet upward and destroy it off-screen."""
        self._rect.y -= self._speed
        if self._rect.bottom < 0:
            self.kill()

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def speed(self) -> int:
        return self._speed
