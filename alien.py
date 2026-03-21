"""Alien enemy entity with movement and shooting behavior."""

# pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments
import random
from typing import Any
import pygame
from pygame.sprite import Sprite
from alien_bullet import AlienBullet
from config import Config


class Alien(Sprite):
    """Egy osztály, amely egyetlen idegent képvisel a flottában."""

    config: Config = Config()
    # Settings / state
    _screen_width: int
    _screen_height: int
    _row_index: int
    _image: pygame.Surface
    _rect: pygame.Rect
    _alien_speed: float
    _shoot_cooldown: int
    _alien_shoot_intensity: int
    _alien_shoot_damage: int
    _alien_hp: int
    _entry_animating: bool
    _entry_target_y: float
    _invulnerable: bool
    _x: float
    _y: float
    _aliens_group: Any | None
    _alien_bullets: Any | None
    _min_alien_spacing_px: int  # Minimum spacing in pixels to prevent overlapping

    @property
    def rect(self) -> pygame.Rect:
        """Get the alien's rect for collision checking."""
        return self._rect

    # Minimum spacing between aliens to prevent overlapping

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        row_index: int = 0,
    ) -> None:
        """Az idegen inicializálása és kezdőpozíciójának beállítása.

        Args:
            x: Kezdő X pozíció (alapértelmezés: 0, a bal oldal)
            y: Kezdő Y pozíció (alapértelmezés: 0, a felső oldal)
            row_index: Az idegen sora (0-4)
        """
        super().__init__()
        self._screen_width = self.config.screen_width
        self._screen_height = self.config.screen_height
        self._row_index = row_index  # Track which row this alien belongs to
        self._min_alien_spacing_px = self.config.min_alien_spacing_px
        # Kép betöltése és 1.5x-szeresére skálázása az aktuális mérethez képest
        self._image = pygame.image.load("grafika/enemy.png")
        # Scale to 1.5x of the 1/7 size: (1/7) * 1.5 = 1.5/7 ≈ 0.214
        original_width: int = self._image.get_width()
        original_height: int = self._image.get_height()
        scale_factor: float = 1.5 / 4.5  # 1.5x the 1/7 size
        scaled_width: int = int(original_width * scale_factor)
        scaled_height: int = int(original_height * scale_factor)
        self._image = pygame.transform.scale(self._image, (scaled_width, scaled_height))
        self._rect = self._image.get_rect()

        # Settings
        self._alien_speed = self.config.alien_speed  # Classic invaders pace
        self._shoot_cooldown = (
            self.config.shoot_cooldown
        )  # Frames until next shot available
        self._alien_shoot_intensity = self.config.alien_shoot_intensity
        self._alien_shoot_damage = self.config.alien_shoot_damage
        self._alien_hp = self.config.alien_hp

        # Entry animation / invulnerability state
        self._entry_animating = False
        self._entry_target_y = float(y)
        self._invulnerable = False

        # Pozíció beállítása
        self._rect.x = x
        self._rect.y = y
        self._x = float(self._rect.x)
        self._y = float(self._rect.y)

        # Reference to all aliens for collision checking (set by Game after creation)
        self._aliens_group = None
        self._alien_bullets = None  # Reference to alien bullets group (set by Game)

    def update_global_movement(
        self,
        fleet_moving_right: bool,
        fleet_is_dropping: bool,
        fleet_drop_speed: float,
    ) -> None:
        """Classic Space Invaders fleet movement.

        Aliens move in sync, then all drop when the fleet hits a screen edge.
        """
        if fleet_is_dropping:
            self._y += fleet_drop_speed
            self._rect.y = int(self._y)
        else:
            dx = self._alien_speed if fleet_moving_right else -self._alien_speed
            self._x += dx
            self._rect.x = int(self._x)

    def set_aliens_group(self, aliens_group: Any) -> None:
        """Store reference to all aliens for collision checking."""
        self._aliens_group = aliens_group

    def set_alien_bullets_group(self, alien_bullets: Any) -> None:
        """Store reference to alien bullets group for shooting."""
        self._alien_bullets = alien_bullets

    def shoot(self) -> None:
        """Fire a projectile downward if available space exists (max 5 total)."""
        if self._alien_bullets is None:
            return

        # Check if we can fire (max 5 alien projectiles on screen)
        if len(self._alien_bullets) < 5:
            bullet = AlienBullet(self._rect.centerx, self._rect.bottom)
            self._alien_bullets.add(bullet)

    def update_cooldown(self) -> None:
        """Update shooting cooldown and attempt random fire."""
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1
        else:
            # Random chance to shoot (roughly every 1 second at 60 FPS)
            if random.random() < 0.03:  # 3% chance per frame
                self.shoot()
                self._shoot_cooldown = 15  # Cooldown of 15 frames (~0.25 seconds)

    def check_screen_boundaries(self) -> None:
        """Enforce screen boundaries without direction changes.

        Global fleet logic handles direction changes.
        """
        # Right boundary clamping
        if self._rect.right > self._screen_width:
            self._rect.right = self._screen_width - 1
            self._x = float(self._rect.x)

        # Left boundary clamping
        elif self._rect.left < 0:
            self._rect.left = 1
            self._x = float(self._rect.x)

        # Top boundary (solid ceiling)
        if self._rect.top < 0:
            self._rect.top = 0
            self._y = float(self._rect.y)

        # Bottom boundary (remove from screen)
        if self._rect.top >= self._screen_height:
            self.kill()

    def check_collision_with_aliens(self, aliens_group: Any) -> None:
        """Enforce spacing to prevent overlapping by neutralizing velocity on collision.

        If two alien hitboxes collide, velocity is neutralized to prevent overlapping.

        Args:
            aliens_group: Az összes idegent tartalmazó sprite csoport
        """
        # Only check collisions with aliens in the same row
        row_aliens: list[Alien] = [
            alien
            for alien in aliens_group
            if alien.row_index == self._row_index and alien is not self
        ]

        colliding: list[Alien] = [
            alien for alien in row_aliens if self._rect.colliderect(alien.rect)
        ]

        if colliding:
            # Collision detected - neutralize velocity by adjusting position slightly
            # Move this alien away from the colliding neighbor
            for alien in colliding:
                if self._rect.centerx < alien.rect.centerx:
                    # This alien is to the left, move slightly left
                    self._rect.x -= 1
                    self._x = float(self._rect.x)
                else:
                    # This alien is to the right, move slightly right
                    self._rect.x += 1
                    self._x = float(self._rect.x)

            # Final bounds check - ensure never goes above top
            if self._rect.top < 0:
                self._rect.top = 0
                self._y = float(self._rect.y)

    def blitme(self, screen: pygame.Surface) -> None:
        """Kirajzolás."""
        screen.blit(self._image, self._rect)
