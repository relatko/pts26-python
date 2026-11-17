import unittest

from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


def make_plant(number: int, resources: list[Resource], cities: int,
               amount: int = 0) -> PowerPlant:
    return PowerPlant(number=PowerPlantNumber(number), acceptedResources=resources,
                      numberOfCities=cities, resourceAmount=amount)


COAL_PLANT = make_plant(4, [Resource.COAL], 1, 2)
OIL_PLANT = make_plant(10, [Resource.OIL], 2, 1)
ECO_PLANT = make_plant(13, [], 1)
URANIUM_PLANT = make_plant(20, [Resource.URANIUM], 3, 1)
HYBRID_PLANT = make_plant(5, [Resource.COAL, Resource.OIL], 1, 2)


class TestPlayerPowerPlants(unittest.TestCase):
    def test_add_and_get(self) -> None:
        plants = PlayerPowerPlants()
        plants.add_power_plant(COAL_PLANT)
        self.assertEqual(list(plants.get_power_plants()), [COAL_PLANT])

    def test_limit_is_three(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT, ECO_PLANT])
        self.assertFalse(plants.can_add_power_plant())
        with self.assertRaises(ValueError):
            plants.add_power_plant(URANIUM_PLANT)

    def test_duplicate_plant_rejected(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        with self.assertRaises(ValueError):
            plants.add_power_plant(COAL_PLANT)

    def test_remove_power_plant(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.assertIsNone(plants.remove_power_plant(PowerPlantNumber(4)))
        self.assertEqual(list(plants.get_power_plants()), [OIL_PLANT])
        self.assertIsInstance(plants.remove_power_plant(PowerPlantNumber(99)), RequestError)

    def test_best_power_plant(self) -> None:
        self.assertIsNone(PlayerPowerPlants().best_power_plant())
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.assertEqual(plants.best_power_plant(), PowerPlantNumber(10))

    def test_can_store_resources(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, ECO_PLANT])
        self.assertTrue(plants.can_store_resources([Resource.COAL] * 4))
        self.assertFalse(plants.can_store_resources([Resource.COAL] * 5))
        self.assertFalse(plants.can_store_resources([Resource.OIL]))

    def test_can_store_resources_hybrid_shares_storage(self) -> None:
        plants = PlayerPowerPlants([HYBRID_PLANT])
        self.assertTrue(plants.can_store_resources(
            [Resource.COAL, Resource.COAL, Resource.OIL, Resource.OIL]))
        self.assertFalse(plants.can_store_resources([Resource.COAL] * 3 + [Resource.OIL] * 2))

    def test_can_store_resources_hybrid_plus_regular(self) -> None:
        plants = PlayerPowerPlants([HYBRID_PLANT, COAL_PLANT])
        self.assertTrue(plants.can_store_resources([Resource.COAL] * 6 + [Resource.OIL] * 2))
        self.assertFalse(plants.can_store_resources([Resource.COAL] * 9))

    def test_number_of_connectable_cities(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT, ECO_PLANT])
        self.assertEqual(plants.number_of_connectable_cities([]), 1)
        self.assertEqual(plants.number_of_connectable_cities([Resource.OIL]), 3)
        self.assertEqual(
            plants.number_of_connectable_cities(
                [Resource.COAL, Resource.COAL, Resource.OIL]), 4)

    def test_number_of_connectable_cities_hybrid(self) -> None:
        plants = PlayerPowerPlants([HYBRID_PLANT, OIL_PLANT])
        self.assertEqual(plants.number_of_connectable_cities([Resource.OIL] * 3), 3)
        self.assertEqual(plants.number_of_connectable_cities([Resource.COAL] * 2), 1)

    def test_cities_powered_by(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        result = plants.cities_powered_by(
            [PowerPlantNumber(10)], [Resource.OIL])
        self.assertEqual(result, 2)

    def test_cities_powered_by_errors(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        self.assertIsInstance(
            plants.cities_powered_by([PowerPlantNumber(99)], []), RequestError)
        self.assertIsInstance(
            plants.cities_powered_by([PowerPlantNumber(4)], [Resource.COAL]), RequestError)
        self.assertIsInstance(
            plants.cities_powered_by(
                [PowerPlantNumber(4), PowerPlantNumber(4)], [Resource.COAL] * 4),
            RequestError)


if __name__ == "__main__":
    unittest.main()
