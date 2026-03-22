# pylint: disable=too-few-public-methods

import pygame
from config import Config


class AlienBullet(pygame.sprite.Sprite):

    _config: Config = Config()
    _image: pygame.Surface
    _rect: pygame.Rect
    _speed: int

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self._image: pygame.Surface = pygame.Surface((7, 27))
        self._image.fill((255, 100, 100))  # piros
        # midtop - moves the middle of the image to the given x and moves the top of the image to the given y
        self._rect: pygame.Rect = self._image.get_rect(midtop=(x, y))
        self._speed: int = self._config.alien_bullet_speed

    def update(self) -> None:
        # shoot downwards, and remove if it goes off the screen
        self._rect.y += self._speed
        # rect.top - y coordinate of the tom of the rect
        if self._rect.top > self._config.screen_height:
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
