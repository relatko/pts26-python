"""Towns: houses of the players in the towns."""
from typing import Sequence, Union

from power_grid.connections import Connections
from power_grid.simple_types import PlayerColor, RequestError

HOUSE_COSTS = (10, 15, 20)  # the 1st, 2nd and 3rd house in one town


class Towns:
    """Players build houses; step 1/2/3 allow 1/2/3 houses in a town."""

    def __init__(self, connections: Connections) -> None:
        self._connections = connections
        self._houses: dict[str, list[PlayerColor]] = {t: [] for t in connections.towns}
        self._max_houses_in_town = 1

    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str], max_money: int
    ) -> Union[int, RequestError]:
        """Builds a house in every town (in the given order) and returns the total price.

        Nothing is changed when any town is not allowed or the price is above `max_money`.
        """
        if len(set(town_names)) != len(town_names):
            return RequestError("A town is listed more than once")
        total = self._calculate_price(player, town_names)
        if isinstance(total, RequestError):
            return total
        if total > max_money:
            return RequestError(f"Not enough money: {total} needed")
        for town in town_names:
            self._houses[town].append(player)
        return total

    def _calculate_price(
        self, player: PlayerColor, town_names: Sequence[str]
    ) -> Union[int, RequestError]:
        """Checks every town in the given order and returns the total price.

        Does not change any state.
        """
        network = [town for town, owners in self._houses.items() if player in owners]
        total = 0
        for town in town_names:
            if town not in self._houses:
                return RequestError(f"Unknown town {town}")
            owners = self._houses[town]
            if player in owners:
                return RequestError(f"You already have a house in {town}")
            if len(owners) >= self._max_houses_in_town:
                return RequestError(f"{town} is full in this step")
            try:
                connection = self._connections.calculate_connecting_cost(network, [town])
            except ValueError:
                return RequestError(f"{town} cannot be connected to your network")
            total += HOUSE_COSTS[len(owners)] + connection
            network.append(town)
        return total

    def get_number_of_houses(self, player: PlayerColor) -> int:
        """Houses of the player in all towns."""
        return sum(player in owners for owners in self._houses.values())

    def get_max_number_of_houses(self) -> int:
        """The biggest number of houses owned by one player (used for step and game end)."""
        players = {p for owners in self._houses.values() for p in owners}
        return max((self.get_number_of_houses(p) for p in players), default=0)

    def players_in(self, town: str) -> list[PlayerColor]:
        """Players with a house in the town (in the order of building)."""
        return list(self._houses[town])

    def start_step2(self) -> None:
        """Two houses fit into a town."""
        self._max_houses_in_town = 2

    def start_step3(self) -> None:
        """Three houses fit into a town."""
        self._max_houses_in_town = 3
        