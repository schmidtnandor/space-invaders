"""Block cover used for player protection."""

# pylint: disable=no-member,too-few-public-methods

import pygame
from config import Config


class Block(pygame.sprite.Sprite):

    _config: Config = Config()
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
        self._width = self._config.block_width
        self._height = self._config.block_height

        self._image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self._rect = self._image.get_rect(topleft=(x, y))

        self._cell_size = self._config.block_cell_size
        self._dead_color = self._config.block_dead_color

        self._cols = (self._width + self._cell_size - 1) // self._cell_size
        self._rows = (self._height + self._cell_size - 1) // self._cell_size
        # init 2d array of cells, where every single cell is set to true
        self._cells = [[True for _ in range(self._cols)] for _ in range(self._rows)]

        # Track remaining grid hits
        self._damage = 60
        self._update_image()

    def _alive_color(self) -> tuple[int, int, int]:
        # Color changes based on remaining health to visually indicate damage level
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
        # fill with black to clear previous state, then redraw all cells with their current color
        self._image.fill((0, 0, 0, 0))
        for row in range(self._rows):
            for col in range(self._cols):
                # 2 dimensional array of booleans, looks for if cell is alive it has alive_color otherwise it has dead_color
                # example: if 1st cell of 1st row got hit then row = 0, col = 0 and self._cells[0][0] will be false so it will get the dead_color
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
        # Convert global coordinates to local block coordinates, so the 1st cell in the 1st row and 1st col is at 0,0
        local_x: int = x - self._rect.left
        local_y: int = y - self._rect.top
        # if local coordinates are outside the block, ignore the hit
        if (
            local_x < 0
            or local_y < 0
            or local_x >= self._width
            or local_y >= self._height
        ):
            return False
        # Determine which cell was hit based on local coordinates and cell size
        col: int = local_x // self._cell_size
        row: int = local_y // self._cell_size

        # Check if the cell is already destroyed or if the calculated row/col is out of bounds, and ignore the hit if so
        if row < 0 or row >= self._rows or col < 0 or col >= self._cols:
            return False

        if not self._cells[row][col]:
            return False

        self._cells[row][col] = False
        self._damage = max(0, self._damage - 1)

        cell_rect: pygame.Rect = pygame.Rect(
            col * self._cell_size,
            row * self._cell_size,
            # width and height of the cell
            self._cell_size,
            self._cell_size,
        )
        pygame.draw.rect(self._image, self._dead_color, cell_rect)

        # Redraw alive cells with updated color after each hit.
        self._update_image()
        # all() - true if all arguments are true
        if all(not alive for row_cells in self._cells for alive in row_cells):
            self.kill()

        return True

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect
