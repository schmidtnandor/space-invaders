import pygame


class Block(pygame.sprite.Sprite):
    """A destructible cover block in front of the player.

    Each block has a limited number of hit points. When a bullet hits the
    block, the hit points decrease and the block changes appearance.
    """

    # Made larger so there are three substantial cover pieces in front of the player.
    WIDTH = 100
    HEIGHT = 50
    MAX_HP = 5

    # Colors keyed by remaining hit points (1..MAX_HP)
    COLORS = {
        5: (60, 200, 60),
        4: (120, 200, 60),
        3: (200, 200, 60),
        2: (200, 120, 60),
        1: (200, 60, 60),
    }

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.hp = self.MAX_HP
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._update_image()

    def _update_image(self) -> None:
        """Redraw the block based on its remaining hit points."""
        color = self.COLORS.get(self.hp, (50, 50, 50))
        self.image.fill(color)

        # Draw a subtle outline to make it easier to see at low HP.
        pygame.draw.rect(self.image, (40, 40, 40), self.image.get_rect(), 2)

    def hit(self) -> None:
        """Apply damage to the block and destroy it when HP reaches zero."""
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
        else:
            self._update_image()
