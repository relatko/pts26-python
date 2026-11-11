"""Sociable unit tests of Towns: the real Connections is used."""
import unittest

from power_grid.connections import Connections
from power_grid.simple_types import PlayerColor, RequestError
from power_grid.towns import Towns

RED, BLUE, GREEN = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN

#  A -5- B -7- C -3- D      (A-C costs 20)     E -1- F is a separate island
MAP = [("A", "B", 5), ("B", "C", 7), ("A", "C", 20), ("C", "D", 3), ("E", "F", 1)]


class TestTowns(unittest.TestCase):
    """Building houses: prices, steps, errors."""

    def setUp(self) -> None:
        self.towns = Towns(Connections(MAP))

    def test_first_house_costs_only_the_house(self) -> None:
        """No connection is paid for the first house."""
        self.assertEqual(self.towns.buy_houses(RED, ["A"], 100), 10)
        self.assertEqual(self.towns.get_number_of_houses(RED), 1)

    def test_next_house_pays_the_connection(self) -> None:
        """House 10 plus the connection from the network."""
        self.towns.buy_houses(RED, ["A"], 100)
        self.assertEqual(self.towns.buy_houses(RED, ["B"], 100), 15)

    def test_several_towns_in_one_request(self) -> None:
        """C is connected through B (7) and not directly (20)."""
        self.assertEqual(self.towns.buy_houses(RED, ["A", "B", "C"], 100), 10 + 15 + 17)

    def test_cheapest_path_is_used(self) -> None:
        """A-B-C-D costs 15 for the connection."""
        self.towns.buy_houses(RED, ["A"], 100)
        self.assertEqual(self.towns.buy_houses(RED, ["D"], 100), 10 + 15)

    def test_empty_list_is_free(self) -> None:
        """A player may build nothing."""
        self.assertEqual(self.towns.buy_houses(RED, [], 0), 0)

    def test_not_enough_money_changes_nothing(self) -> None:
        """The price is checked before the houses are built."""
        result = self.towns.buy_houses(RED, ["A", "B"], 24)
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.towns.get_number_of_houses(RED), 0)

    def test_errors(self) -> None:
        """Unknown town, own house, duplicate town and an unreachable town."""
        self.towns.buy_houses(RED, ["A"], 100)
        self.assertIsInstance(self.towns.buy_houses(RED, ["X"], 100), RequestError)
        self.assertIsInstance(self.towns.buy_houses(RED, ["A"], 100), RequestError)
        self.assertIsInstance(self.towns.buy_houses(RED, ["B", "B"], 100), RequestError)
        self.assertIsInstance(self.towns.buy_houses(RED, ["E"], 100), RequestError)
        self.assertEqual(self.towns.get_number_of_houses(RED), 1)

    def test_steps_decide_how_many_houses_fit_into_a_town(self) -> None:
        """Step 1: one, step 2: two (second costs 15), step 3: three (third costs 20)."""
        self.towns.buy_houses(RED, ["A"], 100)
        self.assertIsInstance(self.towns.buy_houses(BLUE, ["A"], 100), RequestError)
        self.towns.start_step2()
        self.assertEqual(self.towns.buy_houses(BLUE, ["A"], 100), 15)
        self.assertIsInstance(self.towns.buy_houses(GREEN, ["A"], 100), RequestError)
        self.towns.start_step3()
        self.assertEqual(self.towns.buy_houses(GREEN, ["A"], 100), 20)
        self.assertEqual(self.towns.players_in("A"), [RED, BLUE, GREEN])

    def test_max_number_of_houses(self) -> None:
        """The player with the most houses decides."""
        self.assertEqual(self.towns.get_max_number_of_houses(), 0)
        self.towns.buy_houses(RED, ["A", "B", "C"], 100)
        self.towns.start_step2()
        self.towns.buy_houses(BLUE, ["A"], 100)
        self.assertEqual(self.towns.get_max_number_of_houses(), 3)
        self.assertEqual(self.towns.get_number_of_houses(BLUE), 1)


if __name__ == "__main__":
    unittest.main()
