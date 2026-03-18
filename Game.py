"""Main game loop and object orchestration for Space Invaders clone."""
# pylint: disable=invalid-name,too-many-instance-attributes,no-member,too-many-branches

import pygame
from player import Player
from alien import Alien
from block import Block


class Game:
    """Game engine state and logic."""
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 1000

    # Alien configuration
    ALIEN_ROWS = 4  # Number of rows of aliens
    ALIEN_INITIAL_ROW_Y = 50  # Y position for first row
    FLEET_SPEED = 0.7
    FLEET_DROP_DISTANCE = 10.0
    FLEET_DROP_SPEED = 2.5  # Pixels per frame while dropping

    def __init__(self) -> None:

        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Space Invaders")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        # Initialize player
        self.player = Player(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Initialize blocks (cover/bunkers)
        self.blocks = pygame.sprite.Group()
        self._create_blocks()

        # Initialize aliens
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()  # Alien projectiles (max 3)

        # Global fleet state (synchronized across all aliens when boundary is hit)
        self.fleet_moving_right = True
        self.fleet_is_dropping = False
        self.fleet_drop_progress = 0.0
        self.fleet_edge_cooldown = 0
        self.fleet_speed = self.FLEET_SPEED

        # Create initial rows of aliens
        self._create_initial_aliens()

        self.run()

    def _create_initial_aliens(self) -> None:
        """Create five full rows of aliens at game start."""
        # Get image dimensions to calculate proper spacing
        temp_alien = Alien(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
        alien_width = temp_alien.rect.width
        alien_height = temp_alien.rect.height
        temp_alien.kill()  # Remove temporary alien

        # Calculate spacing with strict minimum gap to prevent any touching
        min_gap = 8  # Match MIN_SPACING in Alien class to ensure no overlaps
        total_width_per_alien = alien_width + min_gap
        row_spacing = alien_height + min_gap  # Vertical spacing between rows

        # Create five full rows of aliens
        for row in range(self.ALIEN_ROWS):
            x = 30  # Start position from left edge with padding
            y = self.ALIEN_INITIAL_ROW_Y + (row * row_spacing)

            # Fill each row with properly spaced aliens (full rows, not reduced)
            while x + alien_width < self.SCREEN_WIDTH - 30:  # Leave padding on right edge
                alien = Alien(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, x, y, row)
                self.aliens.add(alien)
                x += total_width_per_alien

        # Set group references and speed for all aliens
        for alien in self.aliens:
            alien.set_aliens_group(self.aliens)
            alien.set_alien_bullets_group(self.alien_bullets)
            alien.alien_speed = self.fleet_speed

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shoot()

    def _update_global_fleet_state(self) -> None:
        """Update global fleet state when ANY alien hits a boundary.

        If ANY alien touches the left/right boundary:
        - Reverse horizontal direction
        - Enter drop phase for a fixed distance
        """
        # Decrease edge cooldown if recently reversed
        if self.fleet_edge_cooldown > 0:
            self.fleet_edge_cooldown -= 1

        if self.fleet_is_dropping:
            self.fleet_drop_progress += self.FLEET_DROP_SPEED

            if self.fleet_drop_progress >= self.FLEET_DROP_DISTANCE:
                self.fleet_is_dropping = False
                self.fleet_drop_progress = 0.0

            return

        # Only check boundary hit when not currently dropping and cooldown has passed
        if self.fleet_edge_cooldown > 0:
            return

        boundary_hit = False
        for alien in self.aliens:
            if self.fleet_moving_right and alien.rect.right >= self.SCREEN_WIDTH - 2:
                boundary_hit = True
                break
            if not self.fleet_moving_right and alien.rect.left <= 2:
                boundary_hit = True
                break

        if boundary_hit:
            self.fleet_moving_right = not self.fleet_moving_right
            self.fleet_is_dropping = True
            self.fleet_drop_progress = 0.0
            self.fleet_edge_cooldown = 10  # Give fleet a short pause before next boundary check

            # Speed up slightly as aliens are killed (optional classic feel)
            self.fleet_speed = min(6.0, self.fleet_speed + 0.05)
            for alien in self.aliens:
                alien.alien_speed = self.fleet_speed

    def _create_blocks(self) -> None:
        """Create protective blocks in front of the player."""
        # Create four larger blocks with more spacing, placed closer to the player.
        block_count = 4
        spacing = 150
        total_width = block_count * Block.WIDTH + (block_count - 1) * spacing
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        # Place blocks very close to the player (player bullets still stop at the blocks).
        start_y = self.player.rect.top - 60

        for i in range(block_count):
            x = start_x + i * (Block.WIDTH + spacing)
            self.blocks.add(Block(x, start_y))

    def update(self) -> None:
        """Update all game objects and collisions."""
        self.player.check_input()
        self.player.bullets.update()

        # Update global fleet state (detects any boundary hit and reverses entire fleet)
        self._update_global_fleet_state()

        # Update each alien with global fleet state
        for alien in self.aliens:
            alien.update_global_movement(
                self.fleet_moving_right,
                self.fleet_is_dropping,
                self.FLEET_DROP_SPEED,
            )
            alien.update_cooldown()  # Handle shooting
            alien.check_screen_boundaries()
            alien.check_collision_with_aliens(self.aliens)

        # Update alien bullets
        self.alien_bullets.update()

        # Remove alien bullets that have left the screen
        for bullet in list(self.alien_bullets):
            if bullet.rect.top < 0 or bullet.rect.bottom > self.SCREEN_HEIGHT:
                bullet.kill()

        # Player bullets should not pass through blocks.
        # The blocks don't take damage from the player, but they still stop bullets.
        for bullet in list(self.player.bullets):
            hit_blocks = pygame.sprite.spritecollide(bullet, self.blocks, False)
            if hit_blocks:
                bullet.kill()
                continue

            hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, True)
            if hit_aliens:
                bullet.kill()

        # Alien bullets should also collide with blocks and damage 9x9 cells.
        for bullet in list(self.alien_bullets):
            blocked = False
            for block in self.blocks:
                if block.rect.colliderect(bullet.rect):
                    if block.take_damage_at(bullet.rect.centerx, bullet.rect.centery):
                        bullet.kill()
                        blocked = True
                        break
            if blocked:
                continue

            # Check collision with player after block handling.
            if self.player.rect.colliderect(bullet.rect):
                bullet.kill()
                self.player.take_damage(1)
                if self.player.health <= 0:
                    self.running = False

    def _draw_health_bar(self) -> None:
        """Draw the player's health bar at the top of the screen."""
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20

        # Draw background (dark)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Draw health fill
        health_fill_width = (self.player.health / 20) * bar_width
        health_color = self.player.get_health_color()
        pygame.draw.rect(
            self.screen, health_color, (bar_x, bar_y, health_fill_width, bar_height)
        )

        # Draw border
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # Draw health text
        font = pygame.font.Font(None, 24)
        health_text = font.render(
            f"Health: {self.player.health}/20", True, (200, 200, 200)
        )
        self.screen.blit(health_text, (bar_x + bar_width + 15, bar_y + 2))

    def draw(self) -> None:
        """Draw all renderable elements to the screen."""
        self.screen.fill((30, 30, 30))  # Background color

        # Draw blocks
        self.blocks.draw(self.screen)

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw aliens
        for alien in self.aliens:
            alien.blitme(self.screen)

        # Draw alien bullets
        self.alien_bullets.draw(self.screen)

        # Draw player bullets
        self.player.bullets.draw(self.screen)

        # Draw health bar
        self._draw_health_bar()

        pygame.display.flip()
