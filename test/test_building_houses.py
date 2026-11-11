"""Tests for BuildingHouses."""
import json
import unittest
from power_grid.building_houses import BuildingHouses
from power_grid.simple_types import PhaseStatus, RequestError
from power_grid.steps import CheckAndBumpStep
from test.fakes_phases import BLUE, RED, FakeBoard, FakeMarket, FakeTowns


class BuildingHousesTest(unittest.TestCase):
    """BuildingHouses against fake towns and market and the real step checker."""

    def setUp(self) -> None:
        self.red = FakeBoard()
        self.blue = FakeBoard()
        self.towns = FakeTowns()
        self.market = FakeMarket()
        self.steps = CheckAndBumpStep()
        self.phase = BuildingHouses(
            {RED: self.red, BLUE: self.blue}, self.towns, self.market, self.steps)
        self.phase.start_phase([BLUE, RED])

    def test_build_spends_cost_and_continues(self) -> None:
        self.towns.max = 2
        result = self.phase.build_houses(BLUE, ["Berlin"])
        self.assertIs(result, PhaseStatus.CONTINUES)
        self.assertEqual(self.blue.money, 40)
        self.assertEqual(self.market.removed_below, [3])

    def test_wrong_player_gets_error(self) -> None:
        result = self.phase.build_houses(RED, ["Berlin"])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.red.money, 50)

    def test_error_from_towns_keeps_turn(self) -> None:
        self.towns.cost = RequestError("Town is full")
        result = self.phase.build_houses(BLUE, ["Berlin"])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.blue.money, 50)
        self.assertEqual(json.loads(self.phase.get_state())["current_player"],
                         "BLUE")

    def test_pass_does_not_touch_markets(self) -> None:
        self.phase.build_houses(BLUE, [])
        self.assertEqual(self.market.removed_below, [])
        self.assertEqual(self.blue.money, 50)

    def test_seventh_house_starts_step2_once(self) -> None:
        self.towns.max = 7
        self.phase.build_houses(BLUE, ["Berlin"])
        self.phase.build_houses(RED, ["Essen"])
        self.assertEqual(self.towns.step2_started, 1)
        self.assertEqual(self.steps.getStep(), 2)

    def test_step3_starts_market_step3(self) -> None:
        self.steps.startStep2()
        self.towns.max = 14
        self.phase.build_houses(BLUE, ["Berlin"])
        self.assertEqual(self.market.step3_started, 1)

    def test_last_player_ends_phase(self) -> None:
        self.phase.build_houses(BLUE, [])
        self.assertIs(self.phase.build_houses(RED, []), PhaseStatus.PHASE_ENDS)


if __name__ == "__main__":
    unittest.main()
