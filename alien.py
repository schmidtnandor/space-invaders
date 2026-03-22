import random
from typing import Any
import pygame
from pygame.sprite import Sprite
from alien_bullet import AlienBullet
from config import Config


class Alien(Sprite):

    _config: Config = Config()
    _screen_width: int
    _screen_height: int
    _row_index: int
    _image: pygame.Surface
    _rect: pygame.Rect
    _alien_speed: float
    # shoot_cooldown - how many frames till the next shot can be fired, if 0 then there is a chance to shoot a bullet
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
    _min_alien_spacing_px: int  # Minimum spacing between aliens to prevent overlapping

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def row_index(self) -> int:
        return self._row_index

    @property
    def y(self) -> float:
        return self._y

    @property
    def alien_speed(self) -> float:
        return self._alien_speed

    @property
    def entry_animating(self) -> bool:
        return self._entry_animating

    @property
    def entry_target_y(self) -> float:
        return self._entry_target_y

    @property
    def invulnerable(self) -> bool:
        return self._invulnerable

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        row_index: int = 0,
    ) -> None:
        # row_index - what row is the alien in
        super().__init__()
        self._screen_width = self._config.screen_width
        self._screen_height = self._config.screen_height
        self._row_index = row_index
        self._min_alien_spacing_px = self._config.min_alien_spacing_px
        self._image = pygame.image.load("grafika/enemy.png")
        original_width: int = self._image.get_width()
        original_height: int = self._image.get_height()
        scale_factor: float = 0.33
        scaled_width: int = int(original_width * scale_factor)
        scaled_height: int = int(original_height * scale_factor)
        self._image = pygame.transform.scale(self._image, (scaled_width, scaled_height))
        self._rect = self._image.get_rect()

        self._alien_speed = self._config.alien_speed
        self._shoot_cooldown = self._config.alien_shoot_cooldown
        self._alien_shoot_intensity = self._config.alien_shoot_intensity
        self._alien_shoot_damage = self._config.alien_shoot_damage
        self._alien_hp = self._config.alien_hp

        self._entry_animating = False
        self._entry_target_y = float(y)
        self._invulnerable = False

        # set position
        self._rect.x = x
        self._rect.y = y
        self._x = float(self._rect.x)
        self._y = float(self._rect.y)

        # Reference to all aliens and their bullets
        self._aliens_group = None
        self._alien_bullets = None

    def update_global_movement(
        self,
        fleet_moving_right: bool,
        fleet_is_dropping: bool,
        fleet_drop_speed: float,
    ) -> None:
        # lefele mozognak, ha fleet_is_dropping igaz, egyébként jobbra vagy balra a fleet_moving_right alapján
        if fleet_is_dropping:
            self._y += fleet_drop_speed
            self._rect.y = int(self._y)
        else:
            dx = self._alien_speed if fleet_moving_right else -self._alien_speed
            self._x += dx
            self._rect.x = int(self._x)

    def set_fleet_speed(self, speed: float) -> None:
        self._alien_speed = speed

    def begin_entry_animation(self, target_y: float, start_y: float) -> None:
        self._entry_animating = True
        self._invulnerable = True
        self._entry_target_y = target_y
        self._y = start_y
        self._rect.y = int(self._y)

    def update_entry_animation(self, speed: float) -> bool:
        if not self._entry_animating:
            return False

        self._y += speed
        if self._y >= self._entry_target_y:
            self._y = self._entry_target_y
            self._entry_animating = False
            self._invulnerable = False

        self._rect.y = int(self._y)
        return self._entry_animating

    def set_aliens_group(self, aliens_group: Any) -> None:
        # set group of aliens
        self._aliens_group = aliens_group

    def set_alien_bullets_group(self, alien_bullets: Any) -> None:
        # set group of alien bullets
        self._alien_bullets = alien_bullets

    def shoot(self) -> None:
        # if there is no alien_bullets group set, we can't shoot
        if self._alien_bullets is None:
            return

        # we dont shoot if there are more than 4 bullets on screen
        if len(self._alien_bullets) < 5:
            bullet = AlienBullet(self._rect.centerx, self._rect.bottom)
            self._alien_bullets.add(bullet)

    def update_cooldown(self) -> None:
        # if cooldown is active, decrease it, otherwise try to shoot and reset cooldown if shot
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1
        else:
            if random.random() < 0.03:
                self.shoot()
                self._shoot_cooldown = 15  # 15 frame till next chance of shooting

    def check_screen_boundaries(self) -> None:

        # if alien goes off the right edge, move it back and set x to the new position
        if self._rect.right > self._screen_width:
            self._rect.right = self._screen_width - 1
            self._x = float(self._rect.x)

        # same here
        elif self._rect.left < 0:
            self._rect.left = 1
            self._x = float(self._rect.x)

    def check_collision_with_aliens(self, aliens_group: Any) -> None:
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
            # adjust position to prevent overlap with colliding neighbors
            # Move this alien away from the colliding neighbor
            for alien in colliding:
                if self._rect.centerx < alien.rect.centerx:
                    # this alien is to the left, move slightly left
                    self._rect.x -= 1
                    self._x = float(self._rect.x)
                else:
                    # same but for the right
                    self._rect.x += 1
                    self._x = float(self._rect.x)

    def blitme(self, screen: pygame.Surface) -> None:
        # draw the alien on the screen at its current position
        screen.blit(self._image, self._rect)
