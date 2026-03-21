class Config:
    _screen_width: int = 1920
    _screen_height: int = 1080
    _alien_rows: int = 3
    _alien_initial_row_y: int = 50
    _fleet_speed: float = 0.7
    _fleet_drop_distance: int = 35
    _fleet_drop_speed: float = 1.5
    _shoot_cooldown: int = 200

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
