import unittest

from power_grid.player_resources import PlayerResources
from power_grid.simple_types import Resource


class TestPlayerResources(unittest.TestCase):
    def test_starts_empty(self) -> None:
        self.assertEqual(list(PlayerResources().get_resources()), [])

    def test_add_resources(self) -> None:
        storage = PlayerResources()
        storage.add_resources([Resource.COAL, Resource.COAL, Resource.OIL])
        self.assertEqual(storage.amount_of(Resource.COAL), 2)
        self.assertEqual(storage.amount_of(Resource.OIL), 1)
        self.assertEqual(storage.amount_of(Resource.URANIUM), 0)

    def test_remove_resources(self) -> None:
        storage = PlayerResources([Resource.COAL, Resource.COAL, Resource.OIL])
        storage.remove_resources([Resource.COAL])
        self.assertEqual(list(storage.get_resources()), [Resource.COAL, Resource.OIL])

    def test_remove_too_many_changes_nothing(self) -> None:
        storage = PlayerResources([Resource.COAL])
        with self.assertRaises(ValueError):
            storage.remove_resources([Resource.COAL, Resource.OIL])
        self.assertEqual(storage.amount_of(Resource.COAL), 1)

    def test_get_resources_returns_a_copy(self) -> None:
        storage = PlayerResources([Resource.GARBAGE])
        result = list(storage.get_resources())
        result.append(Resource.COAL)
        self.assertEqual(storage.amount_of(Resource.COAL), 0)


if __name__ == "__main__":
    unittest.main()
