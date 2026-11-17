import unittest

from power_grid.simple_types import PlayerColor
from power_grid.steps import CheckAndBumpStep, DeterminePlayerOrder

RED, BLUE, GREEN = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN


class FakeStandings:
    # Standings with numbers set by the test.

    def __init__(self) -> None:
        self.houses: dict[PlayerColor, int] = {}
        self.plants: dict[PlayerColor, int] = {}
        self.powered: dict[PlayerColor, int] = {}
        self.money: dict[PlayerColor, int] = {}

    def number_of_houses(self, player: PlayerColor) -> int:
        return self.houses.get(player, 0)

    def best_power_plant_number(self, player: PlayerColor) -> int:
        return self.plants.get(player, 0)

    def powered_cities(self, player: PlayerColor) -> int:
        return self.powered.get(player, 0)

    def outstanding_money(self, player: PlayerColor) -> int:
        return self.money.get(player, 0)


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

    def test_limit_for_step_2_can_be_changed(self) -> None:
        # In a game with other player count the limit differs
        steps = CheckAndBumpStep(cities_for_step2=10)
        self.assertFalse(steps.checkAndBumpToStep2(max_cities=7))
        self.assertTrue(steps.checkAndBumpToStep2(max_cities=10))

    def test_step_2_is_bumped_only_once(self) -> None:
        # The second check must not report another change
        self.steps.checkAndBumpToStep2(max_cities=7)
        self.assertFalse(self.steps.checkAndBumpToStep2(max_cities=8))
        self.assertEqual(self.steps.getStep(), 2)

    def test_step_3_starts_when_the_card_is_drawn(self) -> None:
        # Step 3 follows Step 2 as soon as the Step 3 card is drawn
        self.steps.startStep2()
        self.assertTrue(self.steps.checkAndBumpToStep3(step3_card_drawn=True))
        self.assertEqual(self.steps.getStep(), 3)

    def test_step_3_does_not_start_without_the_card(self) -> None:
        # The number of cities does not matter for Step 3
        self.steps.checkAndBumpToStep2(max_cities=20)
        self.assertFalse(self.steps.checkAndBumpToStep3(step3_card_drawn=False))
        self.assertEqual(self.steps.getStep(), 2)

    def test_cannot_jump_from_step_1_to_step_3(self) -> None:
        # Step 3 can only follow Step 2
        self.assertFalse(self.steps.checkAndBumpToStep3(step3_card_drawn=True))
        self.assertEqual(self.steps.getStep(), 1)

    def test_step_3_is_bumped_only_once(self) -> None:
        self.steps.startStep2()
        self.steps.checkAndBumpToStep3(step3_card_drawn=True)
        self.assertFalse(self.steps.checkAndBumpToStep3(step3_card_drawn=True))


class TestDeterminePlayerOrder(unittest.TestCase):
    def setUp(self) -> None:
        self.standings: FakeStandings = FakeStandings()
        self.order: DeterminePlayerOrder = DeterminePlayerOrder(
            [RED, BLUE, GREEN], self.standings)

    def test_reorder_puts_the_player_with_most_houses_first(self) -> None:
        # Assume RED has 5 houses, BLUE has 2, and GREEN has 8
        self.standings.houses = {RED: 5, BLUE: 2, GREEN: 8}
        # GREEN should be first, RED second, BLUE third
        self.assertEqual(self.order.reorder(), [GREEN, RED, BLUE])

    def test_reorder_breaks_a_tie_by_the_best_power_plant(self) -> None:
        # RED and BLUE have the same houses, BLUE owns the higher plant
        self.standings.houses = {RED: 3, BLUE: 3, GREEN: 1}
        self.standings.plants = {RED: 10, BLUE: 25, GREEN: 40}
        self.assertEqual(self.order.reorder(), [BLUE, RED, GREEN])

    def test_reorder_without_houses_uses_the_best_power_plant(self) -> None:
        # At the start of the game nobody has houses
        self.standings.plants = {RED: 4, BLUE: 13, GREEN: 7}
        self.assertEqual(self.order.reorder(), [BLUE, GREEN, RED])

    def test_game_result_puts_the_winner_first(self) -> None:
        # The player who powers the most cities wins
        self.standings.powered = {RED: 5, BLUE: 2, GREEN: 8}
        self.assertEqual(self.order.game_result(), [GREEN, RED, BLUE])

    def test_game_result_breaks_a_tie_by_money(self) -> None:
        # RED and BLUE power the same cities, BLUE has more money
        self.standings.powered = {RED: 6, BLUE: 6, GREEN: 3}
        self.standings.money = {RED: 10, BLUE: 70, GREEN: 500}
        self.assertEqual(self.order.game_result(), [BLUE, RED, GREEN])