# pylint: disable=missing-class-docstring, missing-function-docstring, unused-argument
# pylint: disable=duplicate-code, too-many-instance-attributes
import unittest
from typing import Sequence, Union

from power_grid.game_controller import GameController
from power_grid.simple_types import (
    GamePhase, PhaseStatus, PlayerColor, PowerPlantNumber, RequestError, Resource)

Result = Union[PhaseStatus, RequestError]
RED, BLUE, GREEN = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN
PPN = PowerPlantNumber(3)


class FakeOrder:
    def __init__(self) -> None:
        self.new_order = [BLUE, GREEN, RED]
        self.reorder_calls = 0

    def reorder(self) -> list[PlayerColor]:
        self.reorder_calls += 1
        return list(self.new_order)

    def game_result(self) -> list[PlayerColor]:
        return []


class FakeAuction:
    def __init__(self) -> None:
        self.started_with: list[list[PlayerColor]] = []
        self.result: Result = PhaseStatus.CONTINUES
        self.requests = 0

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        self.started_with.append(list(player_order))

    def select_power_plant_to_bid(
            self, player: PlayerColor, ppn: PowerPlantNumber, first_bid: int) -> Result:
        self.requests += 1
        return self.result

    def do_not_want_power_plant(self, player: PlayerColor) -> Result:
        self.requests += 1
        return self.result

    def bid_for_current_power_plant(self, player: PlayerColor, bid: int) -> Result:
        self.requests += 1
        return self.result

    def do_not_bid_for_current_power_plant(self, player: PlayerColor) -> Result:
        self.requests += 1
        return self.result

    def remove_power_plant(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            resources: Sequence[Resource]) -> Result:
        self.requests += 1
        return self.result

    def get_state(self) -> str:
        return ""


class FakeBuying:
    def __init__(self) -> None:
        self.started_with: list[list[PlayerColor]] = []
        self.result: Result = PhaseStatus.CONTINUES
        self.requests = 0

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        self.started_with.append(list(player_order))

    def buy_resources(self, player: PlayerColor, resources: Sequence[Resource]) -> Result:
        self.requests += 1
        return self.result

    def get_state(self) -> str:
        return ""


class FakeBuilding:
    def __init__(self) -> None:
        self.started_with: list[list[PlayerColor]] = []
        self.result: Result = PhaseStatus.CONTINUES
        self.requests = 0

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        self.started_with.append(list(player_order))

    def build_houses(self, player: PlayerColor, town_names: Sequence[str]) -> Result:
        self.requests += 1
        return self.result

    def get_state(self) -> str:
        return ""


class FakeBureaucracy:
    def __init__(self) -> None:
        self.started_with: list[list[PlayerColor]] = []
        self.result: Result = PhaseStatus.CONTINUES
        self.requests = 0

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        self.started_with.append(list(player_order))

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> Result:
        self.requests += 1
        return self.result

    def get_state(self) -> str:
        return ""


class TestGameController(unittest.TestCase):
    def setUp(self) -> None:
        self.order = FakeOrder()
        self.auction = FakeAuction()
        self.buying = FakeBuying()
        self.building = FakeBuilding()
        self.bureaucracy = FakeBureaucracy()
        self.controller = GameController(
            [RED, BLUE, GREEN], self.order, self.auction, self.buying,
            self.building, self.bureaucracy)

    def _finish_auction(self) -> None:
        self.auction.result = PhaseStatus.PHASE_ENDS
        self.assertIsNone(self.controller.select_power_plant_to_bid(RED, PPN, 3))

    def _play_until_bureaucracy(self) -> None:
        self._finish_auction()
        self.buying.result = PhaseStatus.PHASE_ENDS
        self.assertIsNone(self.controller.buy_resources(GREEN, []))
        self.building.result = PhaseStatus.PHASE_ENDS
        self.assertIsNone(self.controller.buy_houses(GREEN, []))

    def test_game_starts_with_auction_in_initial_order(self) -> None:
        self.assertEqual(self.controller.game_phase, GamePhase.AUCTION)
        self.assertEqual(self.auction.started_with, [[RED, BLUE, GREEN]])

    def test_request_in_wrong_phase_is_rejected_and_not_forwarded(self) -> None:
        err = self.controller.buy_resources(RED, [Resource.COAL])
        self.assertIsInstance(err, RequestError)
        self.assertEqual(self.buying.requests, 0)

    def test_request_error_from_phase_is_returned_and_phase_stays(self) -> None:
        self.auction.result = RequestError("Not your turn")
        result = self.controller.do_not_want_power_plant(BLUE)
        self.assertEqual(result, RequestError("Not your turn"))
        self.assertEqual(self.controller.game_phase, GamePhase.AUCTION)
        self.assertEqual(self.order.reorder_calls, 0)

    def test_phase_continues_keeps_phase(self) -> None:
        self.assertIsNone(self.controller.bid_for_current_power_plant(BLUE, 5))
        self.assertEqual(self.controller.game_phase, GamePhase.AUCTION)
        self.assertEqual(self.auction.requests, 1)

    def test_first_auction_reorders_and_buying_starts_in_reverse_order(self) -> None:
        self._finish_auction()
        self.assertEqual(self.order.reorder_calls, 1)
        self.assertEqual(self.controller.game_phase, GamePhase.BUY_RESOURCES)
        self.assertEqual(self.buying.started_with, [[RED, GREEN, BLUE]])

    def test_houses_start_in_reverse_order_and_bureaucracy_in_normal_order(self) -> None:
        self._play_until_bureaucracy()
        self.assertEqual(self.building.started_with, [[RED, GREEN, BLUE]])
        self.assertEqual(self.controller.game_phase, GamePhase.BUREAUCRACY)
        self.assertEqual(self.bureaucracy.started_with, [[BLUE, GREEN, RED]])

    def test_end_of_round_reorders_and_starts_new_auction(self) -> None:
        self._play_until_bureaucracy()
        self.order.new_order = [GREEN, RED, BLUE]
        self.bureaucracy.result = PhaseStatus.PHASE_ENDS
        self.assertIsNone(self.controller.use_power_plants(RED, [PPN], []))
        self.assertFalse(self.controller.is_first_turn)
        self.assertEqual(self.order.reorder_calls, 2)
        self.assertEqual(self.controller.game_phase, GamePhase.AUCTION)
        self.assertEqual(self.auction.started_with[-1], [GREEN, RED, BLUE])

    def test_later_auction_does_not_reorder_before_buying(self) -> None:
        self._play_until_bureaucracy()
        self.bureaucracy.result = PhaseStatus.PHASE_ENDS
        self.controller.use_power_plants(RED, [PPN], [])
        calls = self.order.reorder_calls
        self.auction.result = PhaseStatus.PHASE_ENDS
        self.controller.select_power_plant_to_bid(GREEN, PPN, 4)
        self.assertEqual(self.order.reorder_calls, calls)
        self.assertEqual(self.controller.game_phase, GamePhase.BUY_RESOURCES)

    def test_game_ends(self) -> None:
        self._play_until_bureaucracy()
        self.bureaucracy.result = PhaseStatus.GAME_ENDS
        self.assertIsNone(self.controller.use_power_plants(RED, [PPN], []))
        self.assertTrue(self.controller.game_over)
        self.assertIsInstance(self.controller.do_not_want_power_plant(RED), RequestError)
        self.assertIsInstance(self.controller.use_power_plants(RED, [PPN], []), RequestError)


if __name__ == "__main__":
    unittest.main()
    