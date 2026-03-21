"""Alien enemy entity with movement and shooting behavior."""

# pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments
import random
from typing import Any
import pygame
from pygame.sprite import Sprite
from alien_bullet import AlienBullet


class Alien(Sprite):
    """Egy osztály, amely egyetlen idegent képvisel a flottában."""

    # Settings
    alien_speed: float
    alien_shoot_intensity: int
    alien_shoot_damage: int
    alien_hp: int

    # Minimum spacing between aliens to prevent overlapping
    MIN_SPACING = 8  # pixels - strictly enforced minimum gap

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        x: int = 0,
        y: int = 0,
        row_index: int = 0,
    ) -> None:
        """Az idegen inicializálása és kezdőpozíciójának beállítása.

        Args:
            screen_width: A képernyő szélessége
            screen_height: A képernyő magassága
            x: Kezdő X pozíció (alapértelmezés: 0, a bal oldal)
            y: Kezdő Y pozíció (alapértelmezés: 0, a felső oldal)
            row_index: Az idegen sora (0-4)
        """
        super().__init__()
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.row_index: int = row_index  # Track which row this alien belongs to

        # Kép betöltése és 1.5x-szeresére skálázása az aktuális mérethez képest
        self.image: pygame.Surface = pygame.image.load("grafika/enemy.png")
        # Scale to 1.5x of the 1/7 size: (1/7) * 1.5 = 1.5/7 ≈ 0.214
        original_width: int = self.image.get_width()
        original_height: int = self.image.get_height()
        scale_factor: float = 1.5 / 4.5  # 1.5x the 1/7 size
        scaled_width: int = int(original_width * scale_factor)
        scaled_height: int = int(original_height * scale_factor)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
        self.rect: pygame.Rect = self.image.get_rect()

        # Settings
        self.alien_speed: float = 1.0  # Classic invaders pace
        self.shoot_cooldown: int = 0  # Frames until next shot available
        self.alien_shoot_intensity: int = 1
        self.alien_shoot_damage: int = 1
        self.alien_hp: int = 1

        # Entry animation / invulnerability state
        self.entry_animating: bool = False
        self.entry_target_y: float = float(y)
        self.invulnerable: bool = False

        # Pozíció beállítása
        self.rect.x = x
        self.rect.y = y
        self.x: float = float(self.rect.x)
        self.y: float = float(self.rect.y)

        # Reference to all aliens for collision checking (set by Game after creation)
        self.aliens_group: Any | None = None
        self.alien_bullets: Any | None = (
            None  # Reference to alien bullets group (set by Game)
        )

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
            self.y += fleet_drop_speed
            self.rect.y = int(self.y)
        else:
            dx = self.alien_speed if fleet_moving_right else -self.alien_speed
            self.x += dx
            self.rect.x = int(self.x)

    def set_aliens_group(self, aliens_group: Any) -> None:
        """Store reference to all aliens for collision checking."""
        self.aliens_group = aliens_group

    def set_alien_bullets_group(self, alien_bullets: Any) -> None:
        """Store reference to alien bullets group for shooting."""
        self.alien_bullets = alien_bullets

    def shoot(self) -> None:
        """Fire a projectile downward if available space exists (max 5 total)."""
        if self.alien_bullets is None:
            return

        # Check if we can fire (max 5 alien projectiles on screen)
        if len(self.alien_bullets) < 5:
            bullet = AlienBullet(self.rect.centerx, self.rect.bottom)
            self.alien_bullets.add(bullet)

    def update_cooldown(self) -> None:
        """Update shooting cooldown and attempt random fire."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            # Random chance to shoot (roughly every 1 second at 60 FPS)
            if random.random() < 0.03:  # 3% chance per frame
                self.shoot()
                self.shoot_cooldown = 15  # Cooldown of 15 frames (~0.25 seconds)

    def check_screen_boundaries(self) -> None:
        """Enforce screen boundaries without direction changes.

        Global fleet logic handles direction changes.
        """
        # Right boundary clamping
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width - 1
            self.x = float(self.rect.x)

        # Left boundary clamping
        elif self.rect.left < 0:
            self.rect.left = 1
            self.x = float(self.rect.x)

        # Top boundary (solid ceiling)
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = float(self.rect.y)

        # Bottom boundary (remove from screen)
        if self.rect.top >= self.screen_height:
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
            if alien.row_index == self.row_index and alien is not self
        ]

        colliding: list[Alien] = [
            alien for alien in row_aliens if self.rect.colliderect(alien.rect)
        ]

        if colliding:
            # Collision detected - neutralize velocity by adjusting position slightly
            # Move this alien away from the colliding neighbor
            for alien in colliding:
                if self.rect.centerx < alien.rect.centerx:
                    # This alien is to the left, move slightly left
                    self.rect.x -= 1
                    self.x = float(self.rect.x)
                else:
                    # This alien is to the right, move slightly right
                    self.rect.x += 1
                    self.x = float(self.rect.x)

            # Final bounds check - ensure never goes above top
            if self.rect.top < 0:
                self.rect.top = 0
                self.y = float(self.rect.y)

    def blitme(self, screen: pygame.Surface) -> None:
        """Kirajzolás."""
        screen.blit(self.image, self.rect)
