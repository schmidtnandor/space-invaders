import pygame
from player import Player

class Game:
    def __init__(self) -> None:
        pygame.init()
        screen: pygame.Surface = pygame.display.set_mode((1920, 1080))
        clock: pygame.time.Clock = pygame.time.Clock()
        running: bool = True
        background: pygame.Surface = pygame.Surface((1920, 1080))
        pygame.draw.rect(background, (0, 0, 0), background.get_rect())
        player = Player()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # fire a bullet on spacebar press
                    if event.key == pygame.K_SPACE:
                        player.shoot()

            screen.blit(background, (0, 0))
            screen.blit(player.image, player.rect)

            # draw hitbox (optional – useful for collision debugging)
            #pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2)

            # player movement and bullet handling
            player.check_input()
            player.bullets.update()
            player.bullets.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        # clean up after the loop exits
        pygame.quit()
