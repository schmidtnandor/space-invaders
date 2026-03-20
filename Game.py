"""Main game loop and object orchestration for Space Invaders clone."""
# pylint: disable=invalid-name,too-many-instance-attributes,no-member,too-many-branches

import pygame
from player import Player
from alien import Alien
from block import Block
from boss import Boss, BossMinion


class Game:
    """Game engine state and logic."""
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800

    # Alien configuration
    ALIEN_ROWS = 3  # Number of rows of aliens
    ALIEN_INITIAL_ROW_Y = 50  # Y position for first row
    FLEET_SPEED = 0.7
    FLEET_DROP_DISTANCE = 35
    FLEET_DROP_SPEED = 1.5  # Pixels per frame while dropping
    SHOOT_COOLDOWN = 200  # Milliseconds between shots (0.5 seconds)

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

        # Boss minions for wave 3
        self.boss_minions = pygame.sprite.Group()

        # Global fleet state (synchronized across all aliens when boundary is hit)
        self.fleet_moving_right = True
        self.fleet_is_dropping = False
        self.fleet_drop_progress = 0.0
        self.fleet_edge_cooldown = 0
        self.fleet_speed = self.FLEET_SPEED

        # Wave management: start on wave 1 and allow exactly 3 waves total
        self.current_wave = 1
        self.max_waves = 3

        # Boss state (only used for wave 3)
        if self.current_wave == 3:
            self._create_boss()
        else:
            self.boss = None
            # Create initial rows of aliens (not needed for wave 3 boss fight)
            self._create_initial_aliens()

        # Game over state (stops the loop and allows a final draw)
        self.game_over = False
        self.game_over_message = ""

        # Shoot cooldown tracking
        self.last_shot_time = 0

    def _create_boss(self) -> None:
        """Create the boss for wave 3."""
        self.boss = Boss(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.boss.set_alien_bullets_group(self.alien_bullets)

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

                # Wave 2 entry: start off-screen and glide into place invulnerable
                if self.current_wave == 2:
                    alien.entry_animating = True
                    alien.invulnerable = True
                    alien.entry_target_y = float(y)
                    alien.y = -alien_height - 20.0  # Start just above the top
                    alien.rect.y = int(alien.y)

                self.aliens.add(alien)
                x += total_width_per_alien

        # Set group references and speed for all aliens
        for alien in self.aliens:
            alien.set_aliens_group(self.aliens)
            alien.set_alien_bullets_group(self.alien_bullets)
            alien.alien_speed = self.fleet_speed

    def _prepare_wave(self) -> None:
        """Prepare state for the next wave of aliens."""
        self.aliens.empty()
        self.alien_bullets.empty()
        self.boss_minions.empty()
        self.boss = None
        self.fleet_moving_right = True
        self.fleet_is_dropping = False
        self.fleet_drop_progress = 0.0
        self.fleet_edge_cooldown = 0
        self.fleet_speed = self.FLEET_SPEED

    def _start_next_wave(self) -> None:
        """Start the next wave if within allowed limits, otherwise win."""
        if self.current_wave < self.max_waves:
            self.current_wave += 1
            self._prepare_wave()
            
            # Wave 3 is the boss fight
            if self.current_wave == 3:
                self._create_boss()
            else:
                self._create_initial_aliens()
            
            print(f"Starting wave {self.current_wave}/{self.max_waves}")
        else:
            self._trigger_game_over("All waves defeated")

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        # Do not quit pygame here: return to menu for replay or exit.
        # pygame.quit() is managed by the menu/app level.


    def handle_events(self) -> None:
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_shot_time >= self.SHOOT_COOLDOWN:
                        self.player.shoot()
                        self.last_shot_time = current_time
                elif event.key == pygame.K_k:
                    # Kill switch: destroy all enemies in current wave
                    self.aliens.empty()
                    if self.boss:
                        self.boss.kill()
                        self.boss = None
                    self.boss_minions.empty()

    def _update_wave_entry(self) -> bool:
        """Animate wave entry for new wave allies, return True if any still animating."""
        entry_speed = 3.0
        still_animating = False

        for alien in self.aliens:
            if alien.entry_animating:
                still_animating = True
                alien.y += entry_speed
                if alien.y >= alien.entry_target_y:
                    alien.y = alien.entry_target_y
                    alien.entry_animating = False
                    alien.invulnerable = False
                alien.rect.y = int(alien.y)

        return still_animating

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

    def _trigger_game_over(self, message: str) -> None:
        """End the game and set the game-over message."""
        if not self.game_over:
            self.game_over = True
            self.game_over_message = message
            print("Game Over:", message)
            self.running = False

    def update(self) -> None:
        """Update all game objects and collisions."""
        self.player.check_input()
        self.player.bullets.update()

        # Wave entry animation: second wave flies in from top and is invulnerable while moving.
        if self._update_wave_entry():
            self.alien_bullets.update()
            for bullet in list(self.alien_bullets):
                if bullet.rect.top < 0 or bullet.rect.bottom > self.SCREEN_HEIGHT:
                    bullet.kill()
            return

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

        # End game if any alien reaches 700px from the top
        # (instead of colliding with the blocks)
        for alien in self.aliens:
            if alien.rect.top >= 500:
                self._trigger_game_over("Aliens reached the danger zone")
                break

        # Update boss on wave 3
        if self.boss:
            self.boss.update_movement()
            self.boss.update_cooldown()

        # Update boss minions
        for minion in self.boss_minions:
            minion.update_movement()
            minion.update_cooldown()

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

            # Check collision with boss first (wave 3)
            if self.boss and bullet.rect.colliderect(self.boss.rect):
                boss_alive, minions = self.boss.take_damage(1)
                if minions:
                    for minion in minions:
                        self.boss_minions.add(minion)
                if not boss_alive:
                    self.boss = None  # Boss defeated
                bullet.kill()
                continue

            hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, False)
            vulnerable_aliens = [alien for alien in hit_aliens if not alien.invulnerable]
            if vulnerable_aliens:
                for alien in vulnerable_aliens:
                    alien.kill()
                bullet.kill()
                continue

            # Check collision with boss minions
            hit_minions = pygame.sprite.spritecollide(bullet, self.boss_minions, False)
            if hit_minions:
                for minion in hit_minions:
                    if not minion.take_damage(1):
                        minion.kill()
                bullet.kill()
                continue

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

        # If all aliens are dead, spawn the next wave or end the game.
        # For wave 3 (boss), check if boss is defeated instead.
        if not self.game_over:
            if self.current_wave == 3 and not self.boss:
                self._start_next_wave()
            elif not self.boss and not self.aliens and self.current_wave < 3:
                self._start_next_wave()

        # Check if any minions reached the player
        if pygame.sprite.spritecollide(self.player, self.boss_minions, False):
            self.player.take_damage(1)

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

    def _draw_boss_health_bar(self) -> None:
        """Draw the boss's health bar at the top right of the screen."""
        if not self.boss:
            return

        bar_width = 300
        bar_height = 30
        bar_x = self.SCREEN_WIDTH - bar_width - 20
        bar_y = 20

        # Draw background (dark)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Draw health fill (yellow to red gradient based on health)
        health_fill_width = (self.boss.boss_health / self.boss.max_health) * bar_width
        health_percent = self.boss.get_health_percent()

        if health_percent <= 20:
            health_color = (255, 0, 0)  # Red
        elif health_percent <= 40:
            health_color = (255, 100, 0)  # Orange
        elif health_percent <= 60:
            health_color = (255, 200, 0)  # Yellow
        else:
            health_color = (100, 255, 100)  # Green

        pygame.draw.rect(
            self.screen, health_color, (bar_x, bar_y, health_fill_width, bar_height)
        )

        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Draw health text
        font = pygame.font.Font(None, 24)
        health_text = font.render(
            f"Boss: {self.boss.boss_health}/{self.boss.max_health}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(health_text, (bar_x + 10, bar_y + 5))

    def draw(self) -> None:
        """Draw all renderable elements to the screen."""
        self.screen.fill((0, 0, 0))  # Background color set to black

        # Draw blocks
        self.blocks.draw(self.screen)

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw aliens
        for alien in self.aliens:
            alien.blitme(self.screen)

        # Draw boss on wave 3
        if self.boss:
            self.boss.blitme(self.screen)

        # Draw boss minions
        for minion in self.boss_minions:
            minion.blitme(self.screen)

        # Draw alien bullets
        self.alien_bullets.draw(self.screen)

        # Draw player bullets
        self.player.bullets.draw(self.screen)

        # Draw health bar
        self._draw_health_bar()

        # Draw boss health bar if boss exists
        self._draw_boss_health_bar()

        # Draw current wave indicator
        wave_font = pygame.font.Font(None, 24)
        wave_text = wave_font.render(
            f"Wave: {self.current_wave}/{self.max_waves}", True, (255, 255, 255)
        )
        self.screen.blit(wave_text, (20, 50))

        pygame.display.flip()

        if self.game_over:
            font = pygame.font.SysFont(None, 72)
            text_surface = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            self.screen.blit(text_surface, text_rect)

            subfont = pygame.font.SysFont(None, 36)
            subtext_surface = subfont.render("Returning to main menu...", True, (255, 255, 255))
            subtext_rect = subtext_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(subtext_surface, subtext_rect)

            pygame.display.flip()
            pygame.time.delay(1800)
