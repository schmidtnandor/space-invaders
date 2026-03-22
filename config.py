class Config:
    _screen_width: int = 1920
    _screen_height: int = 1080
    _alien_rows: int = 3
    _alien_initial_row_y: int = 50
    _fleet_speed: float = 0.7
    _fleet_drop_distance: int = 35
    _fleet_drop_speed: float = 1.5
    _shoot_cooldown: int = 200
    _player_health: int = 20
    _player_speed: int = 15
    _max_waves: int = 3
    _bullet_speed: int = 15
    _minion_speed: float = 1.5
    _minion_health: int = 3
    _boss_health: int = 30
    _max_boss_health: int = 30
    _boss_shoot_cooldown: int = 0
    _boss_speed: float = 2.0
    _alien_bullet_speed: int = 8
    _alien_speed: float = 1.0
    _alien_shoot_cooldown: int = 0
    _alien_shoot_intensity: int = 1
    _alien_shoot_damage: int = 1
    _alien_hp: int = 1
    _min_alien_spacing_px: int = 8
    _block_width: int = 108
    _block_height: int = 45
    _block_cell_size: int = 9
    _block_dead_color: tuple[int, int, int] = (0, 0, 0)

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height

    @property
    def alien_rows(self) -> int:
        return self._alien_rows

    @property
    def alien_initial_row_y(self) -> int:
        return self._alien_initial_row_y

    @property
    def fleet_speed(self) -> float:
        return self._fleet_speed

    @property
    def fleet_drop_distance(self) -> int:
        return self._fleet_drop_distance

    @property
    def fleet_drop_speed(self) -> float:
        return self._fleet_drop_speed

    @property
    def shoot_cooldown(self) -> int:
        return self._shoot_cooldown

    @property
    def max_waves(self) -> int:
        return self._max_waves

    @property
    def player_health(self) -> int:
        return self._player_health

    @property
    def player_speed(self) -> int:
        return self._player_speed

    @property
    def bullet_speed(self) -> int:
        return self._bullet_speed

    @property
    def minion_speed(self) -> float:
        return self._minion_speed

    @property
    def minion_health(self) -> int:
        return self._minion_health

    @property
    def boss_health(self) -> int:
        return self._boss_health

    @property
    def max_boss_health(self) -> int:
        return self._max_boss_health

    @property
    def boss_shoot_cooldown(self) -> int:
        return self._boss_shoot_cooldown

    @property
    def alien_speed(self) -> float:
        return self._alien_speed

    @property
    def alien_shoot_cooldown(self) -> int:
        return self._alien_shoot_cooldown

    @property
    def alien_shoot_intensity(self) -> int:
        return self._alien_shoot_intensity

    @property
    def alien_shoot_damage(self) -> int:
        return self._alien_shoot_damage

    @property
    def alien_hp(self) -> int:
        return self._alien_hp

    @property
    def boss_speed(self) -> float:
        return self._boss_speed

    @property
    def alien_bullet_speed(self) -> int:
        return self._alien_bullet_speed

    @property
    def min_alien_spacing_px(self) -> int:
        return self._min_alien_spacing_px

    @property
    def block_width(self) -> int:
        return self._block_width

    @property
    def block_height(self) -> int:
        return self._block_height

    @property
    def block_cell_size(self) -> int:
        return self._block_cell_size

    @property
    def block_dead_color(self) -> tuple[int, int, int]:
        return self._block_dead_color
