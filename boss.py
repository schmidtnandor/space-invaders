"""Boss enemy for wave 3."""

# pylint: disable=too-many-instance-attributes,too-many-arguments

import random
from typing import Any
import pygame
from pygame.sprite import Sprite
from alien_bullet import AlienBullet
from config import Config

_config: Config = Config()
_screen_width: int
_screen_height: int
_image: pygame.Surface
_rect: pygame.Rect


class BossMinion(Sprite):

    _minion_speed: float
    _minion_health: int
    _minion_x: float
    _minion_y: float
    _moving_right: bool
    _shoot_cooldown: int

    def __init__(self, spawn_x: int | None = None) -> None:
        super().__init__()
        self._screen_width: int = _config.screen_width
        self._screen_height: int = _config.screen_height

        # Load and scale minion image (smaller version of boss)
        self._image: pygame.Surface = pygame.image.load("grafika/minion.png")
        self._image = pygame.transform.scale(self._image, (80, 80))  # 80x80 px

        self._rect: pygame.Rect = self._image.get_rect()
        self._minion_speed = _config.minion_speed
        self._minion_health = _config.minion_health
        self._shoot_cooldown = 0

        # Position at y=300
        if spawn_x is None:
            spawn_x = self._screen_width // 2
        self._rect.centerx = spawn_x
        self._rect.top = 300
        self._minion_x: float = float(self._rect.x)
        self._minion_y: float = float(self._rect.y)

        # Movement direction
        self._moving_right = random.choice([True, False])

        # Reference to alien bullets group
        self._alien_bullets: Any | None = None

    def set_alien_bullets_group(self, alien_bullets: Any) -> None:
        self._alien_bullets = alien_bullets

    def update_movement(self) -> None:
        # Randomly reverse direction occasionally to make movement less predictable
        if self._moving_right:
            self._minion_x += self._minion_speed
        else:
            self._minion_x -= self._minion_speed
        self._rect.x = int(self._minion_x)

        # Bounce off screen edges
        if self._rect.right >= self._screen_width:
            self._rect.right = self._screen_width - 1
            self._minion_x = float(self._rect.x)
            self._moving_right = False
        elif self._rect.left <= 0:
            self._rect.left = 1
            self._minion_x = float(self._rect.x)
            self._moving_right = True

    def shoot(self) -> None:
        if self._alien_bullets is None:
            return

        if len(self._alien_bullets) < 10:
            bullet = AlienBullet(self._rect.centerx, self._rect.bottom)
            self._alien_bullets.add(bullet)

    def update_cooldown(self) -> None:
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1
        else:
            if random.random() < 0.025:
                self.shoot()
                self._shoot_cooldown = 40

    def take_damage(self, amount: int = 1) -> bool:

        self._minion_health = max(0, self._minion_health - amount)
        return self._minion_health > 0

    def blitme(self, surface: pygame.Surface) -> None:
        surface.blit(self._image, self._rect)

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect


class Boss(Sprite):

    _boss_health: int
    _max_boss_health: int
    _boss_shoot_cooldown: int
    _boss_speed: float
    _x: float
    _y: float
    _moving_right: bool
    _alien_bullets: Any | None

    def __init__(self) -> None:

        super().__init__()
        # Load and scale boss image to 200x200
        self._image: pygame.Surface = pygame.image.load("grafika/boss.png")
        self._image = pygame.transform.scale(self._image, (200, 200))
        self._rect: pygame.Rect = self._image.get_rect()

        self._boss_health = _config.boss_health
        self._max_boss_health = _config.max_boss_health
        self._boss_shoot_cooldown = _config.boss_shoot_cooldown
        self._boss_speed = _config.boss_speed

        # Position at top center of screen
        self._rect.centerx = _config.screen_width // 2
        self._rect.top = 50
        self._x: float = float(self._rect.x)
        self._y: float = float(self._rect.y)

        # Movement direction
        self._moving_right = True

        # Reference to alien bullets group
        self._alien_bullets = None

        # Track which health checkpoints have spawned minions

    def set_alien_bullets_group(self, alien_bullets: Any) -> None:
        self._alien_bullets = alien_bullets

    def update_movement(self) -> None:
        # Randomly reverse direction occasionally to make boss movement less predictable.
        # Use a low chance so movement remains mostly smooth.
        if random.random() < 0.01:  # 1% chance per frame
            self._moving_right = not self._moving_right

        if self._moving_right:
            self._x += self._boss_speed
        else:
            self._x -= self._boss_speed

        self._rect.x = int(self._x)

        # Bounce off screen edges
        if self._rect.right >= _config.screen_width:
            self._rect.right = _config.screen_width - 1
            self._x = float(self._rect.x)
            self._moving_right = False
        elif self._rect.left <= 0:
            self._rect.left = 1
            self._x = float(self._rect.x)
            self._moving_right = True

    def shoot(self) -> None:
        if self._alien_bullets is None:
            return

        # Check if we can fire
        if len(self._alien_bullets) < 10:
            # Left side bullet
            left_x: int = self._rect.left + 50
            bullet1 = AlienBullet(left_x, self._rect.bottom)
            self._alien_bullets.add(bullet1)

            # Right side bullet
            right_x: int = self._rect.right - 50
            bullet2 = AlienBullet(right_x, self._rect.bottom)
            self._alien_bullets.add(bullet2)

    def update_cooldown(self) -> None:
        if self._boss_shoot_cooldown > 0:
            self._boss_shoot_cooldown -= 1
        else:
            if random.random() < 0.02:
                self.shoot()
                self._boss_shoot_cooldown = 30  # Cooldown of 30 frames

    def take_damage(self, amount: int = 1) -> tuple[bool, list[BossMinion]]:
        self._boss_health = max(0, self._boss_health - amount)

        # Check if we should spawn minions at health checkpoints
        minions: list[BossMinion] = []
        checkpoints: list[int] = [27, 24, 21, 18, 15, 12, 9, 6, 3]

        if self._boss_health in checkpoints and self._boss_health:

            # Spawn a minion at boss position, y will be set to 300 by BossMinion
            minion = BossMinion(self._rect.centerx)
            if self._alien_bullets is not None:
                minion.set_alien_bullets_group(self._alien_bullets)
            minions.append(minion)

        return self._boss_health > 0, minions

    def get_health_percent(self) -> float:
        return (self._boss_health / self._max_boss_health) * 100

    def blitme(self, surface: pygame.Surface) -> None:
        surface.blit(self._image, self._rect)

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def boss_health(self) -> int:
        return self._boss_health

    @property
    def max_health(self) -> int:
        return self._max_boss_health
