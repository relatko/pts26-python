from power_grid.simple_types import PlayerColor

class DeterminePlayerOrder:
    def get_order(self, cities_count: dict[PlayerColor, int]) -> list[PlayerColor]:
        # Sort players by the number of cities in ascending order (fewest cities go first)
        return sorted(cities_count.keys(), key=lambda player: cities_count[player])

class CheckAndBumpStep:
    def __init__(self) -> None:
        self._current_step: int = 1

    def check_and_bump(self, max_cities: int) -> int:
        # If any player has 7 or more cities, advance the game to Step 2
        if max_cities >= 7 and self._current_step == 1:
            self._current_step = 2
        return self._current_step