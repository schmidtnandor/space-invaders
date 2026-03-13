import pygame
import sys
from player import Player
from alien import Alien
from block import Block


class Game:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    
    # Alien configuration
    ALIEN_ROWS = 5  # Number of rows of aliens
    ALIEN_INITIAL_ROW_Y = 50  # Y position for first row

    def __init__(self) -> None:
        pygame.init()
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
        
        # Fleet movement state (synchronized across all aliens)
        self.fleet_moving_right = True
        self.fleet_is_dropping = False
        self.fleet_drop_speed = 0
        self.fleet_edge_cooldown = 0
        self.FLEET_DROP_AMOUNT = 40
        
        # Create initial rows of aliens
        self._create_initial_aliens()

        self.run()

    def _create_initial_aliens(self) -> None:
        """Create five rows of aliens at game start with strict spacing enforcement."""
        # Get image dimensions to calculate proper spacing
        temp_alien = Alien(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0)
        alien_width = temp_alien.rect.width
        alien_height = temp_alien.rect.height
        temp_alien.kill()  # Remove temporary alien
        
        # Calculate spacing with strict minimum gap to prevent any touching
        min_gap = 8  # Match MIN_SPACING in Alien class to ensure no overlaps
        total_width_per_alien = alien_width + min_gap
        row_spacing = alien_height + min_gap  # Vertical spacing between rows
        
        # Create five rows with precise positioning
        for row in range(self.ALIEN_ROWS):
            x = 20  # Start position from left edge with padding
            y = self.ALIEN_INITIAL_ROW_Y + (row * row_spacing)
            
            # Fill each row with properly spaced aliens
            while x + alien_width < self.SCREEN_WIDTH - 20:  # Leave padding on right edge
                alien = Alien(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, x, y)
                self.aliens.add(alien)
                x += total_width_per_alien

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shoot()

    def _update_fleet_state(self) -> None:
        """Update synchronized fleet movement state with precise boundary detection.
        
        Ensures all aliens respond simultaneously to boundary hits with no sticking.
        """
        # Decrease cooldown
        if self.fleet_edge_cooldown > 0:
            self.fleet_edge_cooldown -= 1
        
        # Handle dropping phase with acceleration
        if self.fleet_is_dropping:
            self.fleet_drop_speed = min(self.fleet_drop_speed + 0.5, self.FLEET_DROP_AMOUNT / 5)
        
        # Check if any alien has hit the edge and needs to reverse (only when not dropping)
        if self.fleet_edge_cooldown <= 0 and not self.fleet_is_dropping:
            edge_detected = False
            
            if self.fleet_moving_right:
                # Check for right edge collision - use a threshold to catch it cleanly
                for alien in self.aliens:
                    if alien.rect.right >= self.SCREEN_WIDTH - 2:
                        edge_detected = True
                        break
            else:
                # Check for left edge collision
                for alien in self.aliens:
                    if alien.rect.left <= 2:
                        edge_detected = True
                        break
            
            if edge_detected:
                # Reverse direction and start dropping
                self.fleet_moving_right = not self.fleet_moving_right
                self.fleet_is_dropping = True
                self.fleet_drop_speed = 0
                self.fleet_edge_cooldown = 5  # Prevent re-triggering for 5 frames
        
        # Complete drop phase
        if self.fleet_is_dropping and self.fleet_drop_speed >= self.FLEET_DROP_AMOUNT / 5:
            self.fleet_is_dropping = False
            self.fleet_drop_speed = 0

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
        self.player.check_input()
        self.player.bullets.update()
        
        # Update synchronized fleet state
        self._update_fleet_state()

        # Move all aliens with fleet synchronization
        for alien in self.aliens:
            alien.update_movement(
                self.fleet_moving_right,
                self.fleet_is_dropping,
                self.fleet_drop_speed
            )
            alien.check_screen()
            alien.check_collision_with_aliens(self.aliens)

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

    def draw(self) -> None:
        self.screen.fill((30, 30, 30))  # Background color

        # Draw blocks
        self.blocks.draw(self.screen)

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw aliens
        for alien in self.aliens:
            alien.blitme(self.screen)

        # Draw bullets
        self.player.bullets.draw(self.screen)

        pygame.display.flip()
