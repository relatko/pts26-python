"""Tests for Bureaucracy."""
import unittest
from power_grid.bureaucracy import Bureaucracy
from power_grid.simple_types import (
    PhaseStatus, PowerPlantNumber, RequestError, Resource)
from power_grid.steps import CheckAndBumpStep
from test.fakes_phases import (
    BLUE, COAL_PLANT, ECO_PLANT, RED, FakeBoard, FakeMarket, FakePool,
    FakeTowns)


class BureaucracyTest(unittest.TestCase):
    """Bureaucracy against fake board, towns, pool and market."""

    def setUp(self) -> None:
        self.red = FakeBoard(resources=[Resource.COAL] * 2,
                             plants=[COAL_PLANT, ECO_PLANT])
        self.blue = FakeBoard()
        self.towns = FakeTowns()
        self.pool = FakePool()
        self.market = FakeMarket()
        self.steps = CheckAndBumpStep()
        self.phase = Bureaucracy(
            {RED: self.red, BLUE: self.blue}, self.towns, self.pool,
            self.market, self.steps, towns_to_end_game=17)
        self.phase.start_phase([RED, BLUE])

    def test_income_is_limited_by_towns(self) -> None:
        self.towns.counts[RED] = 2
        ppns = [PowerPlantNumber(5), PowerPlantNumber(13)]
        result = self.phase.use_power_plants(RED, ppns, [Resource.COAL] * 2)
        self.assertIs(result, PhaseStatus.CONTINUES)
        self.assertEqual(self.red.income_towns, [2])
        self.assertEqual(self.red.resources, [])

    def test_income_is_limited_by_plant_capacity(self) -> None:
        self.towns.counts[RED] = 10
        self.phase.use_power_plants(RED, [PowerPlantNumber(13)], [])
        self.assertEqual(self.red.income_towns, [1])

    def test_passing_pays_income_for_zero_towns(self) -> None:
        self.phase.use_power_plants(RED, [], [])
        self.assertEqual(self.red.income_towns, [0])

    def test_wrong_resources_rejected(self) -> None:
        result = self.phase.use_power_plants(
            RED, [PowerPlantNumber(5)], [Resource.COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.red.income_towns, [])

    def test_resources_not_owned_rejected(self) -> None:
        self.red.resources = [Resource.COAL]
        result = self.phase.use_power_plants(
            RED, [PowerPlantNumber(5)], [Resource.COAL] * 2)
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.red.resources, [Resource.COAL])

    def test_foreign_plant_rejected(self) -> None:
        result = self.phase.use_power_plants(RED, [PowerPlantNumber(40)], [])
        self.assertIsInstance(result, RequestError)

    def test_duplicate_plant_rejected(self) -> None:
        ppns = [PowerPlantNumber(13), PowerPlantNumber(13)]
        result = self.phase.use_power_plants(RED, ppns, [])
        self.assertIsInstance(result, RequestError)

    def test_wrong_player_gets_error(self) -> None:
        result = self.phase.use_power_plants(BLUE, [], [])
        self.assertIsInstance(result, RequestError)

    def test_end_of_round_refills_and_prepares(self) -> None:
        self.phase.use_power_plants(RED, [], [])
        result = self.phase.use_power_plants(BLUE, [], [])
        self.assertIs(result, PhaseStatus.PHASE_ENDS)
        self.assertEqual(self.pool.refills, [(1, 2)])
        self.assertEqual(self.market.prepared, 1)

    def test_game_ends_at_town_limit(self) -> None:
        self.towns.max = 17
        self.phase.use_power_plants(RED, [], [])
        result = self.phase.use_power_plants(BLUE, [], [])
        self.assertIs(result, PhaseStatus.GAME_ENDS)
        self.assertEqual(self.market.prepared, 0)
        self.assertEqual(self.pool.refills, [])


if __name__ == "__main__":
    unittest.main()
