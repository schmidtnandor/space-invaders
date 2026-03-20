"""Boss enemy for wave 3."""
# pylint: disable=too-many-instance-attributes,too-many-arguments

import random
import pygame
from pygame.sprite import Sprite
from alien_bullet import AlienBullet


class BossMinion(Sprite):
    """Small minion version of the boss that spawns at health checkpoints."""

    def __init__(self, screen_width: int, screen_height: int, spawn_x: int = None):
        """Initialize a boss minion.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            spawn_x: X coordinate to spawn at (defaults to center)
        """
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load and scale minion image (smaller version of boss)
        self.image = pygame.image.load("grafika/boss.png")
        self.image = pygame.transform.scale(self.image, (80, 80))  # 80x80 px
        
        # Tint minion image blue
        self.image.fill((0,152,255), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.rect = self.image.get_rect()

        # Settings
        self.minion_speed = 1.5
        self.shoot_cooldown = 0
        self.minion_health = 5  # Minions have less health

        # Position at y=300
        if spawn_x is None:
            spawn_x = screen_width // 2
        self.rect.centerx = spawn_x
        self.rect.top = 300
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Movement direction
        self.moving_right = random.choice([True, False])

        # Reference to alien bullets group
        self.alien_bullets = None

    def set_alien_bullets_group(self, alien_bullets):
        """Store reference to alien bullets group for shooting."""
        self.alien_bullets = alien_bullets

    def update_movement(self):
        """Update minion horizontal movement."""
        if self.moving_right:
            self.x += self.minion_speed
        else:
            self.x -= self.minion_speed

        self.rect.x = int(self.x)

        # Bounce off screen edges
        if self.rect.right >= self.screen_width:
            self.rect.right = self.screen_width - 1
            self.x = float(self.rect.x)
            self.moving_right = False
        elif self.rect.left <= 0:
            self.rect.left = 1
            self.x = float(self.rect.x)
            self.moving_right = True

    def shoot(self):
        """Fire a bullet from the minion."""
        if self.alien_bullets is None:
            return

        if len(self.alien_bullets) < 10:
            bullet = AlienBullet(self.rect.centerx, self.rect.bottom, speed=5)
            self.alien_bullets.add(bullet)

    def update_cooldown(self):
        """Update shooting cooldown and attempt to fire."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            if random.random() < 0.025:  # 2.5% chance per frame
                self.shoot()
                self.shoot_cooldown = 40

    def take_damage(self, amount: int = 1) -> bool:
        """Reduce minion health.

        Args:
            amount: Damage to take

        Returns:
            True if minion is still alive, False if defeated
        """
        self.minion_health = max(0, self.minion_health - amount)
        return self.minion_health > 0

    def blitme(self, surface):
        """Draw the minion to the screen."""
        surface.blit(self.image, self.rect)


class Boss(Sprite):
    """Boss enemy with 30 health that shoots from both sides."""

    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the boss.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load and scale boss image to 200x200
        self.image = pygame.image.load("grafika/boss.png")
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()

        # Settings
        self.boss_speed = 2.0
        self.shoot_cooldown = 0
        self.boss_health = 30  # Changeable health
        self.max_health = 30

        # Position at top center of screen
        self.rect.centerx = screen_width // 2
        self.rect.top = 50
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Movement direction
        self.moving_right = True

        # Reference to alien bullets group
        self.alien_bullets = None

        # Track which health checkpoints have spawned minions
        self.spawned_at_health = set()

    def set_alien_bullets_group(self, alien_bullets):
        """Store reference to alien bullets group for shooting."""
        self.alien_bullets = alien_bullets

    def update_movement(self):
        """Update boss horizontal movement with screen boundary bouncing."""
        if self.moving_right:
            self.x += self.boss_speed
        else:
            self.x -= self.boss_speed

        self.rect.x = int(self.x)

        # Bounce off screen edges
        if self.rect.right >= self.screen_width:
            self.rect.right = self.screen_width - 1
            self.x = float(self.rect.x)
            self.moving_right = False
        elif self.rect.left <= 0:
            self.rect.left = 1
            self.x = float(self.rect.x)
            self.moving_right = True

    def shoot(self):
        """Fire two bullets from both sides of the boss."""
        if self.alien_bullets is None:
            return

        # Check if we can fire
        if len(self.alien_bullets) < 10:
            # Left side bullet
            left_x = self.rect.left + 50
            bullet1 = AlienBullet(left_x, self.rect.bottom, speed=6)
            self.alien_bullets.add(bullet1)

            # Right side bullet
            right_x = self.rect.right - 50
            bullet2 = AlienBullet(right_x, self.rect.bottom, speed=6)
            self.alien_bullets.add(bullet2)

    def update_cooldown(self):
        """Update shooting cooldown and attempt to fire."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            # Random chance to shoot (roughly every 0.5 seconds at 60 FPS)
            if random.random() < 0.02:  # 2% chance per frame
                self.shoot()
                self.shoot_cooldown = 30  # Cooldown of 30 frames (~0.5 seconds)

    def take_damage(self, amount: int = 1):
        """Reduce boss health and return any spawned minions.

        Args:
            amount: Damage to take

        Returns:
            Tuple of (boss_alive: bool, spawned_minions: list)
        """
        self.boss_health = max(0, self.boss_health - amount)

        # Check if we should spawn minions at health checkpoints
        minions = []
        checkpoints = [27, 24, 21, 18, 15, 12, 9, 6, 3]

        if self.boss_health in checkpoints and self.boss_health not in self.spawned_at_health:
            self.spawned_at_health.add(self.boss_health)
            # Spawn a minion at boss position, y will be set to 300 by BossMinion
            minion = BossMinion(self.screen_width, self.screen_height, spawn_x=self.rect.centerx)
            minion.set_alien_bullets_group(self.alien_bullets)
            minions.append(minion)

        return self.boss_health > 0, minions

    def get_health_percent(self) -> float:
        """Get boss health as a percentage."""
        return (self.boss_health / self.max_health) * 100

    def blitme(self, surface):
        """Draw the boss to the screen."""
        surface.blit(self.image, self.rect)
