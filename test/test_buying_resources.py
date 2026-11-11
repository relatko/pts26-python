"""Tests for BuyingResources."""
import json
import unittest
from power_grid.buying_resources import BuyingResources
from power_grid.simple_types import PhaseStatus, RequestError, Resource
from test.fakes_phases import BLUE, COAL_PLANT, RED, FakeBoard, FakePool


class BuyingResourcesTest(unittest.TestCase):
    """BuyingResources against fake board and pool."""

    def setUp(self) -> None:
        self.red = FakeBoard(plants=[COAL_PLANT])
        self.blue = FakeBoard()
        self.pool = FakePool(price=3)
        self.phase = BuyingResources({RED: self.red, BLUE: self.blue}, self.pool)
        self.phase.start_phase([RED, BLUE])

    def test_purchase_moves_money_and_resources(self) -> None:
        result = self.phase.buy_resources(RED, [Resource.COAL, Resource.COAL])
        self.assertIs(result, PhaseStatus.CONTINUES)
        self.assertEqual(self.red.money, 47)
        self.assertEqual(self.red.resources, [Resource.COAL, Resource.COAL])
        self.assertEqual(self.pool.bought, [Resource.COAL, Resource.COAL])

    def test_wrong_player_gets_error(self) -> None:
        result = self.phase.buy_resources(BLUE, [Resource.COAL])
        self.assertIsInstance(result, RequestError)

    def test_not_enough_money(self) -> None:
        self.red.money = 2
        result = self.phase.buy_resources(RED, [Resource.COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.red.resources, [])
        self.assertEqual(self.pool.bought, [])

    def test_storage_limit_is_twice_requirement(self) -> None:
        result = self.phase.buy_resources(RED, [Resource.COAL] * 5)
        self.assertIsInstance(result, RequestError)

    def test_storage_counts_resources_already_owned(self) -> None:
        self.red.resources = [Resource.COAL] * 3
        result = self.phase.buy_resources(RED, [Resource.COAL] * 2)
        self.assertIsInstance(result, RequestError)

    def test_resource_without_matching_plant_rejected(self) -> None:
        result = self.phase.buy_resources(RED, [Resource.OIL])
        self.assertIsInstance(result, RequestError)

    def test_not_available_in_market(self) -> None:
        self.pool.price_value = None
        result = self.phase.buy_resources(RED, [Resource.COAL])
        self.assertIsInstance(result, RequestError)

    def test_pass_advances_and_last_player_ends_phase(self) -> None:
        self.assertIs(self.phase.buy_resources(RED, []), PhaseStatus.CONTINUES)
        self.assertIs(self.phase.buy_resources(BLUE, []), PhaseStatus.PHASE_ENDS)

    def test_error_keeps_turn(self) -> None:
        self.phase.buy_resources(RED, [Resource.OIL])
        state = json.loads(self.phase.get_state())
        self.assertEqual(state["current_player"], "RED")

    def test_no_moves_after_phase_end(self) -> None:
        self.phase.buy_resources(RED, [])
        self.phase.buy_resources(BLUE, [])
        self.assertIsInstance(self.phase.buy_resources(RED, []), RequestError)


if __name__ == "__main__":
    unittest.main()
