import unittest

from power_grid.connections import Connections

# A-B-C is a chain, A-C is a more expensive shortcut, C-D continues the chain,
# X-Y is a separate island that is not connected to the rest.
DISTANCES = [
    ("A", "B", 5),
    ("B", "C", 7),
    ("A", "C", 15),
    ("C", "D", 3),
    ("X", "Y", 1),
]


class TestConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.connections: Connections = Connections(DISTANCES)

    def test_towns_are_collected_from_the_distances(self) -> None:
        # Every town that appears in some connection is known
        self.assertEqual(self.connections.towns, {"A", "B", "C", "D", "X", "Y"})

    def test_direct_connection_cost(self) -> None:
        # A and B are connected directly for 5
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["B"]), 5)

    def test_connection_is_undirected(self) -> None:
        # The price is the same in both directions
        self.assertEqual(
            self.connections.calculate_connecting_cost(["B"], ["A"]), 5)

    def test_cheaper_path_through_another_town_wins(self) -> None:
        # A-B-C costs 5 + 7 = 12, the direct A-C road costs 15
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["C"]), 12)

    def test_cheapest_start_town_is_used(self) -> None:
        # The player owns A and C; D is 3 away from C, much farther from A
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A", "C"], ["D"]), 3)

    def test_cheapest_target_town_is_used(self) -> None:
        # Of the two targets B is closer to A than C is
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["C", "B"]), 5)

    def test_first_house_is_free(self) -> None:
        # A player without houses pays nothing for the first town
        self.assertEqual(
            self.connections.calculate_connecting_cost([], ["D"]), 0)

    def test_town_already_in_network_costs_nothing(self) -> None:
        # B is already part of the network
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A", "B"], ["B"]), 0)

    def test_unknown_town_raises(self) -> None:
        # A town that is not on the map is an error
        with self.assertRaises(ValueError):
            self.connections.calculate_connecting_cost(["A"], ["Nowhere"])

    def test_towns_without_a_path_raise(self) -> None:
        # X is on a different island than A
        with self.assertRaises(ValueError):
            self.connections.calculate_connecting_cost(["A"], ["X"])

    def test_negative_cost_is_rejected(self) -> None:
        # A road cannot have a negative price
        with self.assertRaises(ValueError):
            Connections([("A", "B", -1)])