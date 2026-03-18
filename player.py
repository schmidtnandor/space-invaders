"""Player ship and fire control."""

# pylint: disable=too-many-instance-attributes,no-member

import pygame
from bullet import Bullet  # imported here to allow precise typing


class Player(pygame.sprite.Sprite):
    """The player's spaceship and input-handling logic."""

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        self.health = 20
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Kép betöltése és optimalizálása
        self.image = pygame.image.load("grafika/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect()

        # Kezdőpozíció: lent, középen
        self.rect.midbottom = (screen_width // 2, screen_height - 50)
        self.speed = 15

        # hitbox used for collision checks (smaller than the visible sprite)
        self.hitbox = self.rect.inflate(-10, -70)

        # group that holds bullets this player has fired
        # `Group` typing is imperfect in pygame stubs; ignore the assignment error
        self.bullets: pygame.sprite.Group[Bullet] = (
            pygame.sprite.Group()  # type: ignore[assignment]
        )

    def check_input(self):
        """Update player position based on keyboard input."""
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.rect.left > 25:
            self.rect.x -= self.speed
            moved = True
        if (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
            and self.rect.right < self.screen_width - 25
        ):
            self.rect.x += self.speed
            moved = True

        # if we changed position, move the hitbox as well
        if moved:
            self.hitbox.center = self.rect.center

    def take_damage(self, amount: int = 1) -> None:
        """Reduce health when hit by an alien bullet."""
        self.health = max(0, self.health - amount)

    def get_health_color(self) -> tuple[int, int, int]:
        """Get the health bar color based on current health percentage."""
        health_percent = (self.health / 20) * 100
        if health_percent <= 10:
            return (255, 0, 0)  # Red
        if health_percent <= 20:
            return (255, 99, 0)  # Orange-red
        if health_percent <= 30:
            return (255, 132, 0)  # Orange
        if health_percent <= 40:
            return (255, 195, 0)  # Yellow
        if health_percent <= 50:
            return (191, 201, 0)  # Yellow-green
        return (60, 200, 60)  # Green

    def shoot(self):
        """Create a bullet travelling upwards from the player's gun."""
        bullet = Bullet(self.rect.centerx, self.rect.top + 50)
        self.bullets.add(bullet)
        return bullet
