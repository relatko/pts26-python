
import unittest

from power_grid.simple_types import Resource
from power_grid.power_plant import PowerPlant, PowerPlantNumber
from power_grid.store_resources import StoreResources


class TestStoreResources(unittest.TestCase):

    def test_enough_space(self) -> None:
        plant = PowerPlant(PowerPlantNumber(10), [Resource.COAL], 2, 2)

        store = StoreResources()

        resources = [Resource.COAL, Resource.COAL]

        result = store.can_store_resources(resources, [plant])

        self.assertTrue(result)

    def test_not_enough_space(self) -> None:
        plant = PowerPlant(PowerPlantNumber(10), [Resource.COAL], 2, 2)

        store = StoreResources()

        resources = [
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.COAL
        ]

        result = store.can_store_resources(resources, [plant])

        self.assertFalse(result)

    def test_wrong_resource(self) -> None:
        plant = PowerPlant(PowerPlantNumber(10), [Resource.COAL], 2, 2)

        store = StoreResources()

        resources = [Resource.OIL]

        result = store.can_store_resources(resources, [plant])

        self.assertFalse(result)

    def test_hybrid_power_plant(self) -> None:
        plant = PowerPlant(
            PowerPlantNumber(5),
            [Resource.COAL, Resource.OIL],
            2,
            3
        )

        store = StoreResources()

        resources = [
            Resource.COAL,
            Resource.COAL,
            Resource.OIL,
            Resource.OIL
        ]

        result = store.can_store_resources(resources, [plant])

        self.assertTrue(result)

    def test_empty_resources(self) -> None:
        plant = PowerPlant(
            PowerPlantNumber(10),
            [Resource.COAL],
            2,
            2
        )

        store = StoreResources()

        result = store.can_store_resources([], [plant])

        self.assertTrue(result)

    def test_no_power_plants(self) -> None:
        store = StoreResources()

        resources = [Resource.COAL]

        result = store.can_store_resources(resources, [])

        self.assertFalse(result)
    
    def test_multiple_power_plants(self) -> None:
        plant1 = PowerPlant(
            PowerPlantNumber(10),
            [Resource.COAL],
            2,
            2
        )

        plant2 = PowerPlant(
            PowerPlantNumber(5),
            [Resource.COAL, Resource.OIL],
            2,
            3
        )

        store = StoreResources()

        resources = [
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.COAL,
            Resource.OIL,
            Resource.OIL
        ]

        result = store.can_store_resources(
            resources, [plant1, plant2]
        )

        self.assertTrue(result)

