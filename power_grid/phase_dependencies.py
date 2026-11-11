# pylint: disable=unused-argument, invalid-name
"""What BuyingResources, BuildingHouses and Bureaucracy need from other classes."""
import json
from typing import Optional, Protocol, Sequence, Union
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlant, RequestError, Resource)


class PlayerBoardForPhases(Protocol):
    """Player board as seen by the three phases."""

    def outstanding_money(self) -> int:
        ...

    def spend_money(self, amount: int) -> None:
        ...

    def receive_money(self, number_of_towns: int) -> None:
        ...

    def add_resources(self, resources: Sequence[Resource]) -> None:
        ...

    def remove_resources(self, resources: Sequence[Resource]) -> None:
        ...

    def get_resources(self) -> Sequence[Resource]:
        ...

    def get_power_plants(self) -> Sequence[PowerPlant]:
        ...


class ResourcePoolForPhases(Protocol):
    """ResourcePool (issue #15) as seen by the three phases."""

    def price(self, resources: Sequence[Resource]) -> Optional[int]:
        """Price of the whole set, None if the market cannot supply it."""
        ...

    def buy(self, resources: Sequence[Resource]) -> None:
        ...

    def refill(self, step: int, number_of_players: int) -> None:
        ...


class TownsForPhases(Protocol):
    """Towns as seen by the three phases."""

    def buy_houses(
            self, player: PlayerColor, town_names: Sequence[str],
            max_money: int) -> Union[int, RequestError]:
        """Returns the total cost or an error."""
        ...

    def number_of_towns(self, player: PlayerColor) -> int:
        ...

    def get_max_number_of_houses(self) -> int:
        ...

    def start_step2(self) -> None:
        ...


class PowerPlantMarketForPhases(Protocol):
    """PowerPlantMarket as seen by the three phases."""

    def remove_power_plants_cheaper_than(self, value: int) -> None:
        """Removes plants strictly below value."""
        ...

    def start_step3(self) -> None:
        ...

    def prepare_next_turn(self) -> None:
        ...


class StepChecker(Protocol):
    """CheckAndBumpStep as seen by the three phases."""

    def getStep(self) -> int:
        ...

    def checkAndBumpToStep2(self, max_cities: int) -> bool:
        ...

    def checkAndBumpToStep3(self, max_cities: int) -> bool:
        ...


class TurnOrder:
    """Tracks whose turn it is inside a phase."""

    def __init__(self) -> None:
        self._order: list[PlayerColor] = []
        self._index: int = 0

    def start(self, order: Sequence[PlayerColor]) -> None:
        """Starts a new pass over the given order."""
        self._order = list(order)
        self._index = 0

    def current(self) -> Optional[PlayerColor]:
        """Returns the player on turn, None if everybody has played."""
        if self._index < len(self._order):
            return self._order[self._index]
        return None

    def check_turn(self, player: PlayerColor) -> Optional[RequestError]:
        """Returns an error if it is not the player's turn."""
        if self.current() != player:
            return RequestError("It is not your turn")
        return None

    def advance(self) -> PhaseStatus:
        """Moves to the next player; PHASE_ENDS after the last one."""
        self._index += 1
        if self._index >= len(self._order):
            return PhaseStatus.PHASE_ENDS
        return PhaseStatus.CONTINUES

    def state(self, phase: str) -> str:
        """Serialized state for get_state()."""
        current = self.current()
        return json.dumps({
            "phase": phase,
            "current_player": current.name if current else None,
        })
