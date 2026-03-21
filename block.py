"""Block cover used for player protection."""

# pylint: disable=no-member,too-few-public-methods

import pygame
from config import Config


class Block(pygame.sprite.Sprite):
    """A destructible cover block in front of the player.

    Each block is divided into 9x9 cells. Bullets destroy one cell at a time.
    """

    config: Config = Config()
    _width: int
    _height: int
    _cell_size: int
    _dead_color: tuple[int, int, int]

    _image: pygame.Surface
    _rect: pygame.Rect
    _cols: int
    _rows: int
    _cells: list[list[bool]]
    _damage: int

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self._width = self.config.block_width
        self._height = self.config.block_height

        self._image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self._rect = self._image.get_rect(topleft=(x, y))

        self._cell_size = self.config.block_cell_size
        self._dead_color = self.config.block_dead_color

        self._cols = (self._width + self._cell_size - 1) // self._cell_size
        self._rows = (self._height + self._cell_size - 1) // self._cell_size
        self._cells = [[True for _ in range(self._cols)] for _ in range(self._rows)]

        # Track remaining grid hits (starting at 72 as requested).
        self._damage = 60
        self._update_image()

    def _alive_color(self) -> tuple[int, int, int]:
        if self._damage <= 12:
            return (255, 0, 0)
        if self._damage <= 20:
            return (255, 99, 0)
        if self._damage <= 30:
            return (255, 132, 0)
        if self._damage <= 40:
            return (255, 195, 0)
        if self._damage <= 50:
            return (191, 201, 0)
        return (60, 200, 60)

    def _update_image(self) -> None:
        alive_color: tuple[int, int, int] = self._alive_color()
        self._image.fill((0, 0, 0, 0))
        for row in range(self._rows):
            for col in range(self._cols):
                color: tuple[int, int, int] = (
                    alive_color if self._cells[row][col] else self._dead_color
                )
                cell_rect: pygame.Rect = pygame.Rect(
                    col * self._cell_size,
                    row * self._cell_size,
                    self._cell_size,
                    self._cell_size,
                )
                pygame.draw.rect(self._image, color, cell_rect)

    def take_damage_at(self, x: int, y: int) -> bool:
        """Mark the block grid cell as damaged by an incoming projectile."""
        local_x: int = x - self._rect.left
        local_y: int = y - self._rect.top
        if (
            local_x < 0
            or local_y < 0
            or local_x >= self._width
            or local_y >= self._height
        ):
            return False

        col: int = local_x // self._cell_size
        row: int = local_y // self._cell_size

        if row < 0 or row >= self._rows or col < 0 or col >= self._cols:
            return False

        if not self._cells[row][col]:
            return False

        self._cells[row][col] = False
        self._damage = max(0, self._damage - 1)

        cell_rect: pygame.Rect = pygame.Rect(
            col * self._cell_size,
            row * self._cell_size,
            self._cell_size,
            self._cell_size,
        )
        pygame.draw.rect(self._image, self._dead_color, cell_rect)

        # Redraw alive cells with updated color after each hit.
        self._update_image()

        if all(not alive for row_cells in self._cells for alive in row_cells):
            self.kill()

        return True
