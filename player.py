"""Player ship and fire control."""

from __future__ import annotations

# pylint: disable=too-many-instance-attributes,no-member
from typing import Any

import pygame
from bullet import Bullet
from config import Config


class Player(pygame.sprite.Sprite):
    config: Config = Config()
    _health: int
    _screen_width: int
    _screen_height: int
    _image: pygame.Surface
    _rect: pygame.Rect
    _hitbox: pygame.Rect
    _speed: int
    _bullets: pygame.sprite.Group[Any]
    _keys: pygame.key.ScancodeWrapper
    _moved: bool
    _health_percent: float
    _bullet: Bullet

    def __init__(self) -> None:
        super().__init__()
        self._health = self.config.player_health
        self._screen_width = self.config.screen_width
        self._screen_height = self.config.screen_height
        self._speed = 15

        # Kép betöltése és optimalizálása
        self._image = pygame.image.load("grafika/player.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (100, 100))
        self._rect = self._image.get_rect()

        # Kezdőpozíció: lent, középen
        self._rect.midbottom = (self._screen_width // 2, self._screen_height - 50)

        # hitbox used for collision checks (smaller than the visible sprite)
        self._hitbox = self._rect.inflate(-10, -90)

        # group that holds bullets this player has fired
        self._bullets = pygame.sprite.Group()

    def check_input(self) -> None:
        """Update player position based on keyboard input."""
        self._keys = pygame.key.get_pressed()
        self._moved = False
        if (
            self._keys[pygame.K_LEFT]
            and self._rect.left > 25
            or self._keys[pygame.K_a]
            and self._rect.left > 25
        ):
            self._rect.x -= self._speed
            self._moved = True
        if (
            self._keys[pygame.K_RIGHT]
            and self._rect.right < self._screen_width - 25
            or self._keys[pygame.K_d]
            and self._rect.right < self._screen_width - 25
        ):
            self._rect.x += self._speed
            self._moved = True

        # if we changed position, move the hitbox as well
        if self._moved:
            self._hitbox.center = self._rect.center

    def take_damage(self, amount: int = 1) -> None:
        """Reduce health when hit by an alien bullet."""
        self._health = max(0, self._health - amount)

    def heal(self, amount: int = 10) -> None:
        """Restore player health (capped by max health)."""
        self._health = min(self.config.player_health, self._health + amount)

    def get_health_color(self) -> tuple[int, int, int]:
        """Get the health bar color based on current health percentage."""
        self._health_percent = (self._health / self.config.player_health) * 100
        if self._health_percent <= 10:
            return (255, 0, 0)  # Red
        if self._health_percent <= 20:
            return (255, 99, 0)  # Orange-red
        if self._health_percent <= 30:
            return (255, 132, 0)  # Orange
        if self._health_percent <= 40:
            return (255, 195, 0)  # Yellow
        if self._health_percent <= 50:
            return (191, 201, 0)  # Yellow-green
        return (60, 200, 60)  # Green

    def shoot(self) -> Bullet:
        """Create a bullet travelling upwards from the player's gun."""
        self._bullet: Bullet = Bullet(self._rect.centerx, self._rect.top + 50)
        self._bullets.add(self._bullet)
        return self._bullet
