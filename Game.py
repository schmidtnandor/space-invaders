"""Main game loop and object orchestration for Space Invaders clone."""

# pylint: disable=invalid-name,too-many-instance-attributes,no-member,too-many-branches

from typing import Any, cast

import pygame
from config import Config
from player import Player
from alien import Alien

from block import Block
from boss import Boss


class Game:
    config: Config = Config()
    """Game engine state and logic."""

    _screen: pygame.Surface
    _clock: pygame.time.Clock
    _running: bool
    _player: Player
    _screen_width: int
    _screen_height: int
    _alien_rows: int
    _alien_initial_row_y: int
    _fleet_drop_distance: int
    _fleet_drop_speed: float
    _shoot_cooldown: int
    _blocks: Any
    _aliens: Any
    _alien_bullets: Any
    _boss_minions: Any
    _fleet_moving_right: bool
    _fleet_is_dropping: bool
    _fleet_drop_progress: float
    _fleet_edge_cooldown: int
    _fleet_speed: float
    _current_wave: int
    _boss: Boss | None
    _game_over: bool
    _game_over_message: str
    _last_shot_time: int

    def __init__(self) -> None:
        self._screen_width = self.config.screen_width
        self._screen_height = self.config.screen_height
        self._screen = pygame.display.set_mode(
            (self._screen_width, self._screen_height)
        )
        pygame.display.set_caption("Space Invaders")
        self._clock = pygame.time.Clock()
        self._running = True

        # Initialize player
        self._player = Player()

        # Cache frequently used config values as typed attributes.

        self._alien_rows = self.config.alien_rows
        self._alien_initial_row_y = self.config.alien_initial_row_y
        self._fleet_drop_distance = self.config.fleet_drop_distance
        self._fleet_drop_speed = self.config.fleet_drop_speed
        self._shoot_cooldown = self.config.shoot_cooldown

        # Initialize blocks (cover/bunkers)
        self._blocks = pygame.sprite.Group()
        self._create_blocks()

        # Initialize aliens
        self._aliens = pygame.sprite.Group()
        self._alien_bullets = pygame.sprite.Group()  # Alien projectiles (max 3)

        # Boss minions for wave 3
        self._boss_minions = pygame.sprite.Group()

        # Global fleet state (synchronized across all aliens when boundary is hit)
        self._fleet_moving_right = True
        self._fleet_is_dropping = False
        self._fleet_drop_progress = 0.0
        self._fleet_edge_cooldown = 0
        self._fleet_speed = self.config.fleet_speed

        # Wave management: start on wave 1 and allow exactly 3 waves total
        self._current_wave = 1
        self._boss = None

        # Start in wave 1: no boss, create initial alien rows.
        self._boss = None
        self._create_initial_aliens()

        # Game over state (stops the loop and allows a final draw)
        self._game_over = False
        self._game_over_message = ""

        # Shoot cooldown tracking
        self._last_shot_time = 0

    def _create_boss(self) -> None:
        """Create the boss for wave 3."""
        self._boss = Boss()
        self._boss.set_alien_bullets_group(self._alien_bullets)

    def _create_initial_aliens(self) -> None:
        """Create five full rows of aliens at game start."""
        # Get image dimensions to calculate proper spacing
        temp_alien: Alien = Alien(0, 0, 0)
        alien_width: int = temp_alien.rect.width
        alien_height: int = temp_alien.rect.height
        temp_alien.kill()  # Remove temporary alien

        # Calculate spacing with strict minimum gap to prevent any touching
        min_gap: int = 8  # Match MIN_SPACING in Alien class to ensure no overlaps
        total_width_per_alien: int = alien_width + min_gap
        row_spacing: int = alien_height + min_gap  # Vertical spacing between rows

        # Create five full rows of aliens
        for row in range(self._alien_rows):
            x: int = 30  # Start position from left edge with padding
            y: int = self._alien_initial_row_y + (row * row_spacing)

            # Fill each row with properly spaced aliens (full rows, not reduced)
            while (
                x + alien_width < self._screen_width - 30
            ):  # Leave padding on right edge
                alien: Alien = Alien(x, y, row)

                # Wave 2 entry: start off-screen and glide into place invulnerable
                if self._current_wave == 2:
                    alien.entry_animating = True
                    alien.invulnerable = True
                    alien.entry_target_y = float(y)
                    alien.y = -alien_height - 20.0  # Start just above the top
                    alien.rect.y = int(alien.y)

                self._aliens.add(alien)
                x += total_width_per_alien

        # Set group references and speed for all aliens
        for alien in self._aliens:
            alien.set_aliens_group(self._aliens)
            alien.set_alien_bullets_group(self._alien_bullets)
            alien.alien_speed = self._fleet_speed

    def _prepare_wave(self) -> None:
        """Prepare state for the next wave of aliens."""
        self._aliens.empty()
        self._alien_bullets.empty()
        self._boss_minions.empty()
        self._boss = None
        self._fleet_moving_right = True
        self._fleet_is_dropping = False
        self._fleet_drop_progress = 0.0
        self._fleet_edge_cooldown = 0
        self._fleet_speed = self.config.fleet_speed

    def _start_next_wave(self) -> None:
        """Start the next wave if within allowed limits, otherwise win."""
        if self._current_wave < self.config.max_waves:
            # Heal player by 10 HP at wave transition (capped by heal() max).
            self._player.heal(10)

            self._current_wave += 1
            self._prepare_wave()

            # Wave 3 is the boss fight
            if self._current_wave == 3:
                self._create_boss()
            else:
                self._create_initial_aliens()

            print(f"Starting wave {self._current_wave}/{self.config.max_waves}")
        else:
            self._trigger_game_over("YOU WIN!")

    def run(self) -> None:
        """Main game loop."""
        while self._running:
            self.handle_events()
            self.update()
            self.draw()
            self._clock.tick(60)

        # Do not quit pygame here: return to menu for replay or exit.
        # pygame.quit() is managed by the menu/app level.

    def handle_events(self) -> None:
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time - self._last_shot_time >= self._shoot_cooldown:
                        self._player.shoot()
                        self._last_shot_time = current_time
                elif event.key == pygame.K_k:
                    # Kill switch: destroy all enemies in current wave
                    self._aliens.empty()
                    if self._boss:
                        self._boss.kill()
                        self._boss = None
                    self._boss_minions.empty()

    def _update_wave_entry(self) -> bool:
        """Animate wave entry for new wave allies, return True if any still animating."""
        entry_speed: float = 3.0
        still_animating: bool = False

        for alien in self._aliens:
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
        if self._fleet_edge_cooldown > 0:
            self._fleet_edge_cooldown -= 1

        if self._fleet_is_dropping:
            self._fleet_drop_progress += self._fleet_drop_speed

            if self._fleet_drop_progress >= self._fleet_drop_distance:
                self._fleet_is_dropping = False
                self._fleet_drop_progress = 0.0

            return

        # Only check boundary hit when not currently dropping and cooldown has passed
        if self._fleet_edge_cooldown > 0:
            return

        boundary_hit: bool = False
        for alien in self._aliens:
            if self._fleet_moving_right and alien.rect.right >= self._screen_width - 2:
                boundary_hit = True
                break
            if not self._fleet_moving_right and alien.rect.left <= 2:
                boundary_hit = True
                break

        if boundary_hit:
            self._fleet_moving_right = not self._fleet_moving_right
            self._fleet_is_dropping = True
            self._fleet_drop_progress = 0.0
            self._fleet_edge_cooldown = (
                10  # Give fleet a short pause before next boundary check
            )

            # Speed up slightly as aliens are killed (optional classic feel)
            self._fleet_speed = min(6.0, self._fleet_speed + 0.05)
            for alien in self._aliens:
                alien.alien_speed = self._fleet_speed

    def _create_blocks(self) -> None:
        """Create protective blocks in front of the player."""
        # Create four larger blocks with more spacing, placed closer to the player.
        block_count: int = 6
        spacing: int = 175
        block_width: int = self.config.block_width
        total_width: int = block_count * block_width + (block_count - 1) * spacing
        start_x: int = (self.config.screen_width - total_width) // 2
        # Place blocks very close to the player (player bullets still stop at the blocks).
        start_y: int = self._player.rect.top - 60

        for i in range(block_count):
            x: int = start_x + i * (block_width + spacing)
            self._blocks.add(Block(x, start_y))

    def _trigger_game_over(self, message: str) -> None:
        """End the game and set the game-over message."""
        if not self._game_over:
            self._game_over = True
            self._game_over_message = message
            print("Game Over:", message)
            self._running = False

    def update(self) -> None:
        """Update all game objects and collisions."""
        self._player.check_input()
        self._player.bullets.update()

        # Wave entry animation: second wave flies in from top and is invulnerable while moving.
        if self._update_wave_entry():
            self._alien_bullets.update()
            for bullet in list(self._alien_bullets):
                if (
                    bullet.rect.top < 0
                    or bullet.rect.bottom > self.config.screen_height
                ):
                    bullet.kill()
            return

        # Update global fleet state (detects any boundary hit and reverses entire fleet)
        self._update_global_fleet_state()

        # Update each alien with global fleet state
        for alien in self._aliens:
            alien.update_global_movement(
                self._fleet_moving_right,
                self._fleet_is_dropping,
                self.config.fleet_drop_speed,
            )
            alien.update_cooldown()  # Handle shooting
            alien.check_screen_boundaries()
            alien.check_collision_with_aliens(self._aliens)

        # End game if any alien reaches 700px from the top
        # (instead of colliding with the blocks)
        for alien in self._aliens:
            if alien.rect.top >= 800:
                self._trigger_game_over("Aliens reached the danger zone")
                break

        # Update boss on wave 3
        if self._boss:
            self._boss.update_movement()
            self._boss.update_cooldown()

        # Update boss minions
        for minion in self._boss_minions:
            minion.update_movement()
            minion.update_cooldown()

        # Update alien bullets
        self._alien_bullets.update()

        # Remove alien bullets that have left the screen
        for bullet in list(self._alien_bullets):
            if bullet.rect.top < 0 or bullet.rect.bottom > self.config.screen_height:
                bullet.kill()

        # Player bullets should not pass through blocks.
        # The blocks don't take damage from the player, but they still stop bullets.
        for bullet in list(self._player.bullets):
            hit_blocks = pygame.sprite.spritecollide(bullet, self._blocks, False)
            if hit_blocks:
                bullet.kill()
                continue

            # Check collision with boss first (wave 3)
            if self._boss and bullet.rect.colliderect(self._boss.rect):
                boss_alive, minions = self._boss.take_damage(1)
                if minions:
                    for minion in minions:
                        self._boss_minions.add(minion)
                if not boss_alive:
                    self._boss = None  # Boss defeated
                bullet.kill()
                continue

            hit_aliens = pygame.sprite.spritecollide(bullet, self._aliens, False)
            vulnerable_aliens: list[Alien] = [
                alien for alien in hit_aliens if not alien.invulnerable
            ]
            if vulnerable_aliens:
                for alien in vulnerable_aliens:
                    alien.kill()
                bullet.kill()
                continue

            # Check collision with boss minions
            hit_minions = pygame.sprite.spritecollide(bullet, self._boss_minions, False)
            if hit_minions:
                for minion in hit_minions:
                    if not minion.take_damage(1):
                        minion.kill()
                bullet.kill()
                continue

        # Alien bullets should also collide with blocks and damage 9x9 cells.
        for bullet in list(self._alien_bullets):
            blocked = False
            for block in self._blocks:
                if block.rect.colliderect(bullet.rect):
                    if block.take_damage_at(bullet.rect.centerx, bullet.rect.centery):
                        bullet.kill()
                        blocked = True
                        break
            if blocked:
                continue

            # Check collision with player after block handling.
            if self._player.rect.colliderect(bullet.rect):
                bullet.kill()
                self._player.take_damage(1)
                if self._player.health <= 0:
                    self._running = False

        # If all aliens are dead, spawn the next wave or end the game.
        # For wave 3 (boss), check if boss is defeated instead.
        if not self._game_over:
            if self._current_wave == 3 and not self._boss:
                self._start_next_wave()
            elif not self._boss and not self._aliens and self._current_wave < 3:
                self._start_next_wave()

        # Check if any minions reached the player
        if pygame.sprite.spritecollide(
            cast(Any, self._player), self._boss_minions, False
        ):
            self._player.take_damage(1)

    def _draw_health_bar(self) -> None:
        """Draw the player's health bar at the top of the screen."""
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20

        # Draw background (dark)
        pygame.draw.rect(
            self._screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height)
        )

        # Draw health fill
        health_fill_width: float = (self._player.health / 20) * bar_width
        health_color: tuple[int, int, int] = self._player.get_health_color()
        pygame.draw.rect(
            self._screen, health_color, (bar_x, bar_y, health_fill_width, bar_height)
        )

        # Draw border
        pygame.draw.rect(
            self._screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Draw health text
        font: pygame.font.Font = pygame.font.Font(None, 24)
        health_text = font.render(
            f"Health: {self._player.health}/20", True, (200, 200, 200)
        )
        self._screen.blit(health_text, (bar_x + bar_width + 15, bar_y + 2))

    def _draw_boss_health_bar(self) -> None:
        """Draw the boss's health bar at the top right of the screen."""
        if not self._boss:
            return

        bar_width: int = 300
        bar_height: int = 30
        bar_x: float = self.config.screen_width - bar_width - 20
        bar_y: int = 20

        # Draw background (dark)
        pygame.draw.rect(
            self._screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height)
        )

        # Draw health fill (yellow to red gradient based on health)
        health_fill_width: float = (
            self._boss.boss_health / self._boss.max_health
        ) * bar_width
        health_percent: float = self._boss.get_health_percent()

        if health_percent <= 20:
            health_color = (255, 0, 0)  # Red
        elif health_percent <= 40:
            health_color = (255, 100, 0)  # Orange
        elif health_percent <= 60:
            health_color = (255, 200, 0)  # Yellow
        else:
            health_color = (100, 255, 100)  # Green

        pygame.draw.rect(
            self._screen, health_color, (bar_x, bar_y, health_fill_width, bar_height)
        )

        # Draw border
        pygame.draw.rect(
            self._screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Draw health text
        font: pygame.font.Font = pygame.font.Font(None, 24)
        health_text = font.render(
            f"Boss: {self._boss.boss_health}/{self._boss.max_health}",
            True,
            (255, 255, 255),
        )
        self._screen.blit(health_text, (bar_x + 10, bar_y + 5))

    def draw(self) -> None:
        """Draw all renderable elements to the screen."""
        self._screen.fill((0, 0, 0))  # Background color set to black

        # Draw blocks
        self._blocks.draw(self._screen)

        # Draw player
        self._screen.blit(self._player.image, self._player.rect)

        # Draw player hitbox for debugging
        # pygame.draw.rect(self.screen, (0, 255, 0), self.player.hitbox, 2)

        # Draw aliens
        for alien in self._aliens:
            alien.blitme(self._screen)

        # Draw boss on wave 3
        if self._boss:
            self._boss.blitme(self._screen)

        # Draw boss minions
        for minion in self._boss_minions:
            minion.blitme(self._screen)

        # Draw alien bullets
        self._alien_bullets.draw(self._screen)

        # Draw player bullets
        self._player.bullets.draw(self._screen)

        # Draw health bar
        self._draw_health_bar()

        # Draw boss health bar if boss exists
        self._draw_boss_health_bar()

        # Draw current wave indicator
        wave_font: pygame.font.Font = pygame.font.Font(None, 24)
        wave_text = wave_font.render(
            f"Wave: {self._current_wave}/{self.config.max_waves}",
            True,
            (255, 255, 255),
        )
        self._screen.blit(wave_text, (20, 50))

        pygame.display.flip()

        if self._game_over:
            font: pygame.font.Font = pygame.font.SysFont(None, 72)
            title_text: str = (
                "YOU WIN!" if self._game_over_message == "YOU WIN!" else "GAME OVER"
            )
            title_color: tuple[int, int, int] = (
                (60, 200, 60) if self._game_over_message == "YOU WIN!" else (255, 0, 0)
            )
            text_surface = font.render(title_text, True, title_color)
            text_rect = text_surface.get_rect(
                center=(self.config.screen_width // 2, self.config.screen_height // 2)
            )
            self._screen.blit(text_surface, text_rect)

            subfont: pygame.font.Font = pygame.font.SysFont(None, 36)
            subtext_surface = subfont.render(
                "Returning to main menu...", True, (255, 255, 255)
            )
            subtext_rect = subtext_surface.get_rect(
                center=(
                    self.config.screen_width // 2,
                    self.config.screen_height // 2 + 60,
                )
            )
            self._screen.blit(subtext_surface, subtext_rect)

            pygame.display.flip()
            pygame.time.delay(1800)
