from __future__ import annotations

from collections.abc import Mapping, Sequence

from power_grid.interfaces import (
    InterfaceDeterminePlayerOrder,
    InterfacePlayerBoardFacade,
    InterfaceTowns,
)
from power_grid.simple_types import PlayerColor


class DeterminePlayerOrder(InterfaceDeterminePlayerOrder):
    def __init__(
        self,
        players: Sequence[PlayerColor],
        towns: InterfaceTowns,
        player_boards: Mapping[PlayerColor, InterfacePlayerBoardFacade],
    ) -> None:
        self._players: list[PlayerColor] = list(players)
        self._towns: InterfaceTowns = towns
        self._player_boards: Mapping[PlayerColor, InterfacePlayerBoardFacade] = player_boards

    def reorder(self) -> list[PlayerColor]:
        # Order descending by connected cities, breaking ties by highest power plant number
        return sorted(
            self._players,
            key=lambda player: (
                self._towns.get_number_of_houses(player),
                self._player_boards[player].best_power_plant_number().number,
            ),
            reverse=True,
        )

    def game_result(self) -> list[PlayerColor]:
        # Rank descending by supplied cities, then remaining money, then built houses
        return sorted(
            self._players,
            key=lambda player: (
                self._supplied_cities(player),
                self._player_boards[player].outstanding_money(),
                self._towns.get_number_of_houses(player),
            ),
            reverse=True,
        )

    def _supplied_cities(self, player: PlayerColor) -> int:
        # Supplied cities cannot exceed the number of houses built in the player's network
        built = self._towns.get_number_of_houses(player)
        connectable = self._player_boards[player].number_of_connectable_cities()
        return min(built, connectable)
