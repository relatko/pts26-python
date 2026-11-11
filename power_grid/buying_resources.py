"""BuyingResources phase."""
from collections import Counter
from typing import Mapping, Sequence, Union
from power_grid.phase_dependencies import (
    PlayerBoardForPhases, ResourcePoolForPhases, TurnOrder)
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlant, RequestError, Resource)


def _capacity(plants: Sequence[PowerPlant]) -> Counter[Resource]:
    capacity: Counter[Resource] = Counter()
    for plant in plants:
        if plant.resource is not None:
            capacity[plant.resource] += 2 * plant.required_resources
    return capacity


class BuyingResources:
    """Players buy resources one by one in the given order."""

    def __init__(self, players: Mapping[PlayerColor, PlayerBoardForPhases],
                 pool: ResourcePoolForPhases) -> None:
        self._players = players
        self._pool = pool
        self._turn = TurnOrder()

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Starts the phase; an empty purchase means passing."""
        self._turn.start(player_order)

    def buy_resources(
            self, player: PlayerColor,
            resources: Sequence[Resource]) -> Union[PhaseStatus, RequestError]:
        """Buys the whole set for the player on turn."""
        error = self._turn.check_turn(player)
        if error is not None:
            return error
        board = self._players[player]
        if resources:
            price = self._price_of(board, resources)
            if isinstance(price, RequestError):
                return price
            self._pool.buy(resources)
            board.spend_money(price)
            board.add_resources(resources)
        return self._turn.advance()

    def get_state(self) -> str:
        """Serialized state of the phase."""
        return self._turn.state("BUY_RESOURCES")

    def _price_of(self, board: PlayerBoardForPhases,
                  resources: Sequence[Resource]) -> Union[int, RequestError]:
        price = self._pool.price(resources)
        if price is None:
            return RequestError("Resources are not available in the market")
        if price > board.outstanding_money():
            return RequestError("Not enough money")
        capacity = _capacity(board.get_power_plants())
        total = Counter(board.get_resources()) + Counter(resources)
        if any(count > capacity[res] for res, count in total.items()):
            return RequestError("Power plants cannot store that many resources")
        return price
