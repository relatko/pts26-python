import unittest

from power_grid.simple_types import Resource, RequestError
from power_grid.power_plant import PowerPlant, PowerPlantNumber
from power_grid.use_power_plants import UsePowerPlants


class TestUsePowerPlants(unittest.TestCase):

    def test_single_power_plant(self) -> None:
        plant = PowerPlant(PowerPlantNumber(8), [Resource.COAL], 3, 2)
        use_plants = UsePowerPlants()
        resources = [Resource.COAL, Resource.COAL, Resource.COAL]

        result = use_plants.number_of_suppliable_towns(resources, [plant])

        self.assertEqual(result, 2)

    def test_not_enough_resources(self) -> None:
        plant = PowerPlant(PowerPlantNumber(8), [Resource.COAL], 3, 2)
        use_plants = UsePowerPlants()
        resources = [Resource.COAL, Resource.COAL]

        result = use_plants.number_of_suppliable_towns(resources, [plant])

        self.assertIsInstance(result, RequestError)

    def test_too_many_resources(self) -> None:
        plant = PowerPlant(PowerPlantNumber(4), [Resource.COAL], 2, 1)
        use_plants = UsePowerPlants()
        resources = [Resource.COAL, Resource.COAL, Resource.COAL]

        result = use_plants.number_of_suppliable_towns(resources, [plant])

        self.assertIsInstance(result, RequestError)

    def test_wrong_resource_type(self) -> None:
        plant = PowerPlant(PowerPlantNumber(6), [Resource.GARBAGE], 1, 1)
        use_plants = UsePowerPlants()
        resources = [Resource.URANIUM]

        result = use_plants.number_of_suppliable_towns(resources, [plant])

        self.assertIsInstance(result, RequestError)

    def test_hybrid_power_plant(self) -> None:
        plant = PowerPlant(
            PowerPlantNumber(5), [Resource.COAL, Resource.OIL], 2, 1
        )
        use_plants = UsePowerPlants()
        resources = [Resource.COAL, Resource.OIL]

        result = use_plants.number_of_suppliable_towns(resources, [plant])

        self.assertEqual(result, 1)

    def test_ecological_power_plant(self) -> None:
        plant = PowerPlant(PowerPlantNumber(13), [], 0, 1)
        use_plants = UsePowerPlants()

        result = use_plants.number_of_suppliable_towns([], [plant])

        self.assertEqual(result, 1)

    def test_empty_plants_and_resources(self) -> None:
        use_plants = UsePowerPlants()

        result = use_plants.number_of_suppliable_towns([], [])

        self.assertEqual(result, 0)

    def test_no_power_plants_with_resources(self) -> None:
        use_plants = UsePowerPlants()

        result = use_plants.number_of_suppliable_towns([Resource.OIL], [])

        self.assertIsInstance(result, RequestError)

    def test_multiple_power_plants_with_hybrid(self) -> None:
        hybrid_plant = PowerPlant(
            PowerPlantNumber(5), [Resource.COAL, Resource.OIL], 2, 1
        )
        coal_plant = PowerPlant(PowerPlantNumber(4), [Resource.COAL], 2, 1)
        eco_plant = PowerPlant(PowerPlantNumber(18), [], 0, 2)
        use_plants = UsePowerPlants()
        resources = 2 * [Resource.COAL] + 2 * [Resource.OIL]

        result = use_plants.number_of_suppliable_towns(
            resources, [hybrid_plant, coal_plant, eco_plant]
        )

        self.assertEqual(result, 4)
