# Player order and game steps.
from collections.abc import Sequence
from typing import Protocol

from power_grid.simple_types import PlayerColor


class PlayerStandings(Protocol):
    # What DeterminePlayerOrder needs to know about the players.

    def number_of_houses(self, player: PlayerColor) -> int:
        # Number of houses (cities) the player has built.
        ...

    def best_power_plant_number(self, player: PlayerColor) -> int:
        # Number of the player's highest power plant, 0 if the player has none.
        ...

    def powered_cities(self, player: PlayerColor) -> int:
        # Number of cities the player powered in the last bureaucracy.
        ...

    def outstanding_money(self, player: PlayerColor) -> int:
        # Money the player has.
        ...


class DeterminePlayerOrder:
    # Orders the players for a new round and for the final ranking.

    def __init__(self, players: Sequence[PlayerColor], standings: PlayerStandings) -> None:
        self._players: list[PlayerColor] = list(players)
        self._standings: PlayerStandings = standings

    def reorder(self) -> list[PlayerColor]:
        # Order for the next round: most houses first, then the highest power plant.
        #
        # Players that are still tied keep their current relative order.
        return sorted(
            self._players,
            key=lambda player: (-self._standings.number_of_houses(player),
                                -self._standings.best_power_plant_number(player)))

    def game_result(self) -> list[PlayerColor]:
        # Final ranking, the winner first: most powered cities, then most money.
        return sorted(
            self._players,
            key=lambda player: (-self._standings.powered_cities(player),
                                -self._standings.outstanding_money(player)))


class CheckAndBumpStep:
    # Keeps the current game step (1, 2 or 3) and moves it forward.

    def __init__(self, cities_for_step2: int = 7) -> None:
        self.step: int = 1
        self._cities_for_step2: int = cities_for_step2

    def getStep(self) -> int:
        # Return the current game step.
        return self.step

    def startStep2(self) -> None:
        # Switch to Step 2.
        self.step = 2

    def startStep3(self) -> None:
        # Switch to Step 3.
        self.step = 3

    def checkAndBumpToStep2(self, max_cities: int) -> bool:
        # Step 2 starts when a player has enough cities. True if the step changed.
        if max_cities >= self._cities_for_step2 and self.step == 1:
            self.startStep2()
            return True
        return False

    def checkAndBumpToStep3(self, step3_card_drawn: bool) -> bool:
        # Step 3 starts when the Step 3 card is drawn. True if the step changed.
        if step3_card_drawn and self.step == 2:
            self.startStep3()
            return True
        return False