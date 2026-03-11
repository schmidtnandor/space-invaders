import pygame
import sys
from player import Player
from alien import Alien


class Game:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800

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

        # Initialize aliens
        self.aliens = pygame.sprite.Group()
        self.SPAWN_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_EVENT, 2000)  # Spawn alien every 2 seconds

        self.run()

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
            elif event.type == self.SPAWN_EVENT:
                new_alien = Alien(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                self.aliens.add(new_alien)

    def update(self) -> None:
        self.player.check_input()
        self.player.bullets.update()

        for alien in self.aliens:
            alien.mozgas()
            alien.check_screen()

        # Check collisions between bullets and aliens
        for bullet in self.player.bullets:
            hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, True)
            if hit_aliens:
                bullet.kill()

    def draw(self) -> None:
        self.screen.fill((30, 30, 30))  # Background color

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw aliens
        for alien in self.aliens:
            alien.blitme(self.screen)

        # Draw bullets
        self.player.bullets.draw(self.screen)

        pygame.display.flip()
