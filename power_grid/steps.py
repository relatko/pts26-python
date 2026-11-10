from power_grid.simple_types import PlayerColor


class DeterminePlayerOrder:
    def __init__(self) -> None:
        self.firstRound: bool = True

    def startPhase(self, playerOrder: list[PlayerColor]) -> None:
        # Initialize the phase
        pass

    def gameResult(self, cities_count: dict[PlayerColor, int]) -> list[PlayerColor]:
        # Sort players by the number of cities in ascending order (fewest cities go first)
        return sorted(cities_count.keys(), key=lambda player: cities_count[player])


class CheckAndBumpStep:
    def __init__(self) -> None:
        self.step: int = 1

    def getStep(self) -> int:
        # Return the current game step
        return self.step

    def startStep1(self) -> None:
        # Initialize step 1
        self.step = 1

    def startStep2(self) -> None:
        # Initialize step 2
        self.step = 2

    def checkAndBumpToStep2(self, max_cities: int) -> bool:
        # If any player has 7 or more cities, advance the game to Step 2
        if max_cities >= 7 and self.step == 1:
            self.step = 2
            return True
        return False

    def checkAndBumpToStep3(self, max_cities: int) -> bool:
        # If any player has 14 or more cities, advance the game to Step 3
        if max_cities >= 14 and self.step == 2:
            self.step = 3
            return True
        return False