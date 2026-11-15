import unittest

from power_grid.simple_types import PlayerColor
from power_grid.steps import CheckAndBumpStep, DeterminePlayerOrder


class TestCheckAndBumpStep(unittest.TestCase):
    def setUp(self) -> None:
        self.steps: CheckAndBumpStep = CheckAndBumpStep()

    def test_starts_in_step_1(self) -> None:
        # The game always starts in Step 1
        self.assertEqual(self.steps.getStep(), 1)

    def test_stays_in_step_1_below_the_limit(self) -> None:
        # The game should remain in Step 1 with 6 cities
        self.assertFalse(self.steps.checkAndBumpToStep2(max_cities=6))
        self.assertEqual(self.steps.getStep(), 1)

    def test_bumps_to_step_2_when_player_reaches_7_cities(self) -> None:
        # The game should advance to Step 2 when a player reaches 7 cities
        self.assertTrue(self.steps.checkAndBumpToStep2(max_cities=7))
        self.assertEqual(self.steps.getStep(), 2)

    def test_step_2_is_bumped_only_once(self) -> None:
        # The second check must not report another change
        self.steps.checkAndBumpToStep2(max_cities=7)
        self.assertFalse(self.steps.checkAndBumpToStep2(max_cities=8))
        self.assertEqual(self.steps.getStep(), 2)

    def test_cannot_jump_from_step_1_to_step_3(self) -> None:
        # Step 3 can only follow Step 2, however many cities there are
        self.assertFalse(self.steps.checkAndBumpToStep3(max_cities=20))
        self.assertEqual(self.steps.getStep(), 1)

    # ---- Known problems. Remove @expectedFailure once the class is fixed. ----

    @unittest.expectedFailure
    def test_step_3_is_not_started_by_the_number_of_cities(self) -> None:
        # Step 3 starts when the Step 3 card is drawn from the power plant
        # deck (PowerPlantMarket.isStep3Start), not at a number of cities.
        self.steps.checkAndBumpToStep2(max_cities=7)
        self.assertFalse(self.steps.checkAndBumpToStep3(max_cities=14))


class TestDeterminePlayerOrder(unittest.TestCase):
    def setUp(self) -> None:
        self.order: DeterminePlayerOrder = DeterminePlayerOrder()

    def test_game_result_contains_every_player_once(self) -> None:
        # Assume RED has 5 cities, BLUE has 2, and GREEN has 8
        result = self.order.gameResult(
            {PlayerColor.RED: 5, PlayerColor.BLUE: 2, PlayerColor.GREEN: 8})
        # Nobody is lost and nobody is repeated
        self.assertCountEqual(
            result, [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN])

    # ---- Known problems. Remove @expectedFailure once the class is fixed. ----

    @unittest.expectedFailure
    def test_game_result_puts_the_winner_first(self) -> None:
        # Assume RED has 5 cities, BLUE has 2, and GREEN has 8
        result = self.order.gameResult(
            {PlayerColor.RED: 5, PlayerColor.BLUE: 2, PlayerColor.GREEN: 8})
        # The player who powers the most cities wins, so GREEN should be
        # first, RED second, BLUE third (right now the list is ascending)
        self.assertEqual(
            result, [PlayerColor.GREEN, PlayerColor.RED, PlayerColor.BLUE])

    @unittest.expectedFailure
    def test_reorder_exists(self) -> None:
        # GameController calls reorder(); the design also names it reorder().
        self.assertTrue(hasattr(self.order, "reorder"))