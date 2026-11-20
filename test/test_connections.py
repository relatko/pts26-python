# pylint: disable=too-many-public-methods
import unittest

from power_grid.connections import Connections


class TestConnections(unittest.TestCase):

    def test_empty_to_towns(self) -> None:
        connections = Connections([("Berlin", "Hamburg", 17)])
        self.assertEqual(connections.calculate_connecting_cost(["Berlin"], []), 0)
        self.assertEqual(connections.calculate_connecting_cost([], []), 0)

    def test_first_town_costs_zero(self) -> None:
        connections = Connections([("Berlin", "Hamburg", 17)])
        self.assertEqual(connections.calculate_connecting_cost([], ["Berlin"]), 0)

        single_town_map = Connections([])
        self.assertEqual(single_town_map.calculate_connecting_cost([], ["Berlin"]), 0)

    def test_direct_connection_both_directions(self) -> None:
        connections = Connections([("Berlin", "Hamburg", 17)])
        self.assertEqual(
            connections.calculate_connecting_cost(["Berlin"], ["Hamburg"]), 17
        )
        self.assertEqual(
            connections.calculate_connecting_cost(["Hamburg"], ["Berlin"]), 17
        )

    def test_cheapest_path_through_intermediate_towns(self) -> None:
        connections = Connections([
            ("A", "B", 20),
            ("A", "X", 6),
            ("X", "Y", 5),
            ("Y", "B", 4),
        ])
        self.assertEqual(connections.calculate_connecting_cost(["A"], ["B"]), 15)

    def test_zero_cost_connection(self) -> None:
        connections = Connections([
            ("Duisburg", "Essen", 0),
            ("Essen", "Dortmund", 4),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["Duisburg"], ["Essen"]), 0
        )
        self.assertEqual(
            connections.calculate_connecting_cost(["Duisburg"], ["Dortmund"]), 4
        )
        self.assertEqual(
            connections.calculate_connecting_cost(
                [], ["Duisburg", "Essen", "Dortmund"]
            ),
            4,
        )

    def test_multiple_from_towns_picks_cheapest_source(self) -> None:
        connections = Connections([
            ("A", "C", 18),
            ("B", "C", 7),
            ("A", "B", 10),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["A", "B"], ["C"]), 7
        )

    def test_multiple_to_towns_chained_from_existing_network(self) -> None:
        connections = Connections([
            ("A", "B", 5),
            ("B", "C", 4),
            ("A", "C", 20),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B", "C"]), 9
        )

    def test_multiple_to_towns_order_independent(self) -> None:
        connections = Connections([
            ("A", "B", 5),
            ("B", "C", 4),
            ("A", "C", 20),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["C", "B"]), 9
        )

    def test_multiple_to_towns_from_empty_network(self) -> None:
        connections = Connections([
            ("A", "B", 5),
            ("B", "C", 4),
            ("A", "C", 20),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost([], ["A", "B", "C"]), 9
        )
        self.assertEqual(
            connections.calculate_connecting_cost([], ["C", "A", "B"]), 9
        )

    def test_branching_targets_from_different_owned_towns(self) -> None:
        connections = Connections([
            ("A", "X", 3),
            ("B", "Y", 5),
            ("A", "B", 100),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["A", "B"], ["X", "Y"]), 8
        )

    def test_unowned_intermediate_hub_not_shared_for_free(self) -> None:
        connections = Connections([
            ("A", "Hub", 10),
            ("Hub", "B", 2),
            ("Hub", "C", 2),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B", "C"]), 16
        )

    def test_already_owned_and_duplicate_targets(self) -> None:
        connections = Connections([("A", "B", 7)])
        self.assertEqual(connections.calculate_connecting_cost(["A"], ["A"]), 0)
        self.assertEqual(
            connections.calculate_connecting_cost(["A", "A"], ["A", "B", "B"]), 7
        )

    def test_parallel_edges_and_self_loops(self) -> None:
        connections = Connections([
            ("A", "A", 0),
            ("A", "A", 5),
            ("A", "B", 15),
            ("A", "B", 8),
            ("B", "A", 12),
        ])
        self.assertEqual(connections.calculate_connecting_cost(["A"], ["B"]), 8)

    def test_realistic_germany_map_subset(self) -> None:
        connections = Connections([
            ("Flensburg", "Kiel", 4),
            ("Kiel", "Lubeck", 4),
            ("Kiel", "Hamburg", 8),
            ("Lubeck", "Hamburg", 6),
            ("Lubeck", "Schwerin", 6),
            ("Hamburg", "Schwerin", 8),
            ("Hamburg", "Bremen", 11),
            ("Hamburg", "Hannover", 17),
            ("Bremen", "Hannover", 10),
            ("Schwerin", "Berlin", 18),
            ("Hannover", "Berlin", 28),
        ])
        self.assertEqual(
            connections.calculate_connecting_cost(["Flensburg"], ["Berlin"]), 32
        )
        self.assertEqual(
            connections.calculate_connecting_cost(
                ["Flensburg"], ["Bremen", "Hannover"]
            ),
            33,
        )

    def test_unreachable_town_raises_value_error(self) -> None:
        connections = Connections([
            ("A", "B", 5),
            ("C", "D", 5),
        ])
        with self.assertRaises(ValueError):
            connections.calculate_connecting_cost(["A"], ["C"])
        with self.assertRaises(ValueError):
            connections.calculate_connecting_cost([], ["A", "C"])
        with self.assertRaises(ValueError):
            connections.calculate_connecting_cost(["A"], ["Unknown"])

    def test_negative_distance_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            Connections([("A", "B", -1)])

    def test_distances_property_and_immutability(self) -> None:
        raw_distances = [("A", "B", 10)]
        connections = Connections(raw_distances)
        raw_distances.append(("B", "C", 5))
        self.assertEqual(connections.distances, [("A", "B", 10)])

        returned = connections.distances
        returned.append(("C", "D", 1))
        self.assertEqual(connections.distances, [("A", "B", 10)])

        from_towns = ["A"]
        to_towns = ["B"]
        self.assertEqual(
            connections.calculate_connecting_cost(from_towns, to_towns), 10
        )
        self.assertEqual(from_towns, ["A"])
        self.assertEqual(to_towns, ["B"])
