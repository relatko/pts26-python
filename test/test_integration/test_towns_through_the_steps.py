"""Integration test: Towns + Connections through steps 1, 2 and 3 with three players."""
import unittest

from power_grid.connections import Connections
from power_grid.simple_types import PlayerColor, RequestError
from power_grid.towns import Towns

RED, BLUE, GREEN = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN

#   Berlin --4-- Hamburg --6-- Bremen --5-- Essen
#      \\______________12_______/
MAP = [("Berlin", "Hamburg", 4), ("Hamburg", "Bremen", 6), ("Berlin", "Bremen", 12),
       ("Bremen", "Essen", 5)]


class TestTownsThroughTheSteps(unittest.TestCase):
    """The map fills up while the game goes from step 1 to step 3."""

    def test_game_from_step_1_to_step_3(self) -> None:
        """Prices follow the number of houses in a town and the cheapest connection."""
        towns = Towns(Connections(MAP))
        money = {RED: 100, BLUE: 100, GREEN: 100}

        def build(player: PlayerColor, names: list[str]) -> object:
            result = towns.buy_houses(player, names, money[player])
            if isinstance(result, int):
                money[player] -= result
            return result

        # step 1: one house per town, the first house has no connection
        self.assertEqual(build(RED, ["Berlin", "Hamburg"]), 10 + (10 + 4))
        self.assertEqual(build(BLUE, ["Bremen"]), 10)
        self.assertIsInstance(build(GREEN, ["Berlin"]), RequestError)  # full
        self.assertEqual(build(GREEN, ["Essen"]), 10)
        self.assertEqual(towns.get_max_number_of_houses(), 2)

        # step 2: the second house in a town costs 15
        towns.start_step2()
        self.assertIsInstance(towns.buy_houses(BLUE, ["Berlin"], 15), RequestError)  # 19 needed
        self.assertEqual(build(BLUE, ["Hamburg"]), 15 + 6)  # Bremen - Hamburg
        self.assertEqual(build(GREEN, ["Bremen"]), 15 + 5)  # Essen - Bremen
        self.assertIsInstance(build(RED, ["Bremen"]), RequestError)  # BLUE and GREEN are there
        self.assertIsInstance(build(RED, ["Hamburg"]), RequestError)  # RED is there already
        self.assertEqual(build(BLUE, ["Berlin"]), 15 + 4)  # Hamburg - Berlin

        # step 3: the third house in a town costs 20
        towns.start_step3()
        self.assertEqual(build(RED, ["Bremen"]), 20 + 6)  # Hamburg - Bremen
        self.assertEqual(towns.players_in("Bremen"), [BLUE, GREEN, RED])
        self.assertEqual(towns.get_number_of_houses(GREEN), 2)
        self.assertEqual(towns.get_number_of_houses(BLUE), 3)
        self.assertEqual(towns.get_max_number_of_houses(), 3)
        self.assertEqual(money, {RED: 100 - 24 - 26, BLUE: 100 - 10 - 21 - 19,
                                 GREEN: 100 - 10 - 20})


if __name__ == "__main__":
    unittest.main()
