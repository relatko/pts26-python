from __future__ import annotations

from power_grid.interfaces import InterfacePlayerBoardFacade, InterfaceTowns
from power_grid.phases.determine_player_order import DeterminePlayerOrder
from power_grid.simple_types import PlayerColor, PowerPlantNumber


class StubTowns(InterfaceTowns):
    def __init__(self, houses: dict[PlayerColor, int]) -> None:
        self._houses = houses

    def get_number_of_houses(self, player: PlayerColor) -> int:
        return self._houses[player]


class StubPlayerBoard(InterfacePlayerBoardFacade):
    def __init__(self, best_plant: int, connectable: int, money: int) -> None:
        self._best_plant = PowerPlantNumber(best_plant)
        self._connectable = connectable
        self._money = money

    def best_power_plant_number(self) -> PowerPlantNumber:
        return self._best_plant

    def number_of_connectable_cities(self) -> int:
        return self._connectable

    def outstanding_money(self) -> int:
        return self._money


def test_reorder_by_cities_and_plant_tiebreaker() -> None:
    players = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN]
    towns = StubTowns({PlayerColor.RED: 4, PlayerColor.BLUE: 5, PlayerColor.GREEN: 5})
    boards = {
        PlayerColor.RED: StubPlayerBoard(best_plant=30, connectable=4, money=20),
        PlayerColor.BLUE: StubPlayerBoard(best_plant=12, connectable=5, money=20),
        PlayerColor.GREEN: StubPlayerBoard(best_plant=18, connectable=5, money=20),
    }

    order = DeterminePlayerOrder(players, towns, boards).reorder()
    assert order == [PlayerColor.GREEN, PlayerColor.BLUE, PlayerColor.RED]


def test_reorder_preserves_initial_order_on_complete_tie() -> None:
    players = [PlayerColor.YELLOW, PlayerColor.RED, PlayerColor.BLACK]
    towns = StubTowns({PlayerColor.YELLOW: 0, PlayerColor.RED: 0, PlayerColor.BLACK: 0})
    boards = {
        PlayerColor.YELLOW: StubPlayerBoard(best_plant=0, connectable=0, money=50),
        PlayerColor.RED: StubPlayerBoard(best_plant=0, connectable=0, money=50),
        PlayerColor.BLACK: StubPlayerBoard(best_plant=0, connectable=0, money=50),
    }

    assert DeterminePlayerOrder(players, towns, boards).reorder() == players


def test_reorder_round_one_after_auction_uses_plants_only() -> None:
    players = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN]
    towns = StubTowns({PlayerColor.RED: 0, PlayerColor.BLUE: 0, PlayerColor.GREEN: 0})
    boards = {
        PlayerColor.RED: StubPlayerBoard(best_plant=4, connectable=1, money=46),
        PlayerColor.BLUE: StubPlayerBoard(best_plant=13, connectable=1, money=37),
        PlayerColor.GREEN: StubPlayerBoard(best_plant=7, connectable=2, money=43),
    }

    order = DeterminePlayerOrder(players, towns, boards).reorder()
    assert order == [PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.RED]


def test_game_result_caps_supplied_cities_and_breaks_ties_by_money() -> None:
    players = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN]
    towns = StubTowns({PlayerColor.RED: 6, PlayerColor.BLUE: 5, PlayerColor.GREEN: 5})
    boards = {
        PlayerColor.RED: StubPlayerBoard(best_plant=20, connectable=4, money=90),
        PlayerColor.BLUE: StubPlayerBoard(best_plant=25, connectable=7, money=30),
        PlayerColor.GREEN: StubPlayerBoard(best_plant=22, connectable=5, money=45),
    }

    ranking = DeterminePlayerOrder(players, towns, boards).game_result()
    assert ranking == [PlayerColor.GREEN, PlayerColor.BLUE, PlayerColor.RED]


def test_game_result_zero_built_cities_and_full_tie_fallback() -> None:
    players = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN]
    towns = StubTowns({PlayerColor.RED: 0, PlayerColor.BLUE: 2, PlayerColor.GREEN: 1})
    boards = {
        PlayerColor.RED: StubPlayerBoard(best_plant=30, connectable=6, money=100),
        PlayerColor.BLUE: StubPlayerBoard(best_plant=10, connectable=1, money=10),
        PlayerColor.GREEN: StubPlayerBoard(best_plant=12, connectable=1, money=10),
    }

    ranking = DeterminePlayerOrder(players, towns, boards).game_result()
    assert ranking == [PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.RED]
