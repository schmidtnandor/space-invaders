"""Block cover used for player protection."""
# pylint: disable=no-member,too-few-public-methods

import pygame


class Block(pygame.sprite.Sprite):
    """A destructible cover block in front of the player.

    Each block is divided into 9x9 cells. Bullets destroy one cell at a time.
    """

    WIDTH = 108
    HEIGHT = 45
    CELL_SIZE = 9
    DEAD_COLOR = (0, 0, 0)

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.cols = (self.WIDTH + self.CELL_SIZE - 1) // self.CELL_SIZE
        self.rows = (self.HEIGHT + self.CELL_SIZE - 1) // self.CELL_SIZE
        self.cells = [[True for _ in range(self.cols)] for _ in range(self.rows)]

        # Track remaining grid hits (starting at 72 as requested).
        self.damage = 60
        self._update_image()

    def _alive_color(self) -> tuple[int, int, int]:
        if self.damage <= 12:
            return (255, 0, 0)
        if self.damage <= 20:
            return (255, 99, 0)
        if self.damage <= 30:
            return (255, 132, 0)
        if self.damage <= 40:
            return (255, 195, 0)
        if self.damage <= 50:
            return (191, 201, 0)
        return (60, 200, 60)

    def _update_image(self) -> None:
        alive_color = self._alive_color()
        self.image.fill((0, 0, 0, 0))
        for row in range(self.rows):
            for col in range(self.cols):
                color = alive_color if self.cells[row][col] else self.DEAD_COLOR
                cell_rect = pygame.Rect(
                    col * self.CELL_SIZE,
                    row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                pygame.draw.rect(self.image, color, cell_rect)

    def take_damage_at(self, x: int, y: int) -> bool:
        """Mark the block grid cell as damaged by an incoming projectile."""
        local_x = x - self.rect.left
        local_y = y - self.rect.top
        if local_x < 0 or local_y < 0 or local_x >= self.WIDTH or local_y >= self.HEIGHT:
            return False

        col = local_x // self.CELL_SIZE
        row = local_y // self.CELL_SIZE

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False

        if not self.cells[row][col]:
            return False

        self.cells[row][col] = False
        self.damage = max(0, self.damage - 1)

        cell_rect = pygame.Rect(
            col * self.CELL_SIZE,
            row * self.CELL_SIZE,
            self.CELL_SIZE,
            self.CELL_SIZE,
        )
        pygame.draw.rect(self.image, self.DEAD_COLOR, cell_rect)

        # Redraw alive cells with updated color after each hit.
        self._update_image()

        if all(not alive for row_cells in self.cells for alive in row_cells):
            self.kill()

        return True
