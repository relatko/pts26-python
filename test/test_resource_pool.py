from power_grid.resource_market import ResourceMarket
import unittest
import json

from power_grid.simple_types import Resource
from power_grid.resource_pool import ResourcePool


class TestResourcePool(unittest.TestCase):

    # Kontrola dostatku surovin v sklade
    def test_enough_resources_in_storage(self) -> None:

        pool = ResourcePool(
            [],
            [Resource.COAL, Resource.OIL]
        )

        resources = [Resource.COAL, Resource.OIL]

        result = pool.can_take_resources_from_storage_space(resources)

        self.assertTrue(result)

    # Nedostatok surovin v sklade
    def test_not_enough_resources_in_storage(self) -> None:

        pool = ResourcePool(
            [],
            [Resource.COAL]
        )

        resources = [Resource.COAL, Resource.COAL]

        result = pool.can_take_resources_from_storage_space(resources)

        self.assertFalse(result)

    # Odobratie surovin zo skladu
    def test_get_from_storage(self) -> None:

        pool = ResourcePool(
            [],
            [Resource.COAL, Resource.OIL, Resource.OIL]
        )

        resources = [Resource.COAL, Resource.OIL]

        pool.get_from_storage_space(resources)

        self.assertEqual(pool.storage_space, [Resource.OIL])

    # Odobratie surovin z hlavnej zasoby
    def test_take_resources(self) -> None:

        pool = ResourcePool(
            [Resource.COAL, Resource.COAL, Resource.OIL],
            []
        )

        resources = [Resource.COAL, Resource.OIL]

        result = pool.take_resources(resources)

        self.assertEqual(result, resources)
        self.assertEqual(pool.resources, [Resource.COAL])

    # Ak nie je dost surovin
    def test_take_not_enough_resources(self) -> None:

        pool = ResourcePool(
            [Resource.COAL],
            []
        )

        resources = [Resource.COAL, Resource.COAL, Resource.OIL]

        result = pool.take_resources(resources)

        self.assertEqual(result, [Resource.COAL])
        self.assertEqual(pool.resources, [])

    # Pridanie surovin
    def test_put_resources(self) -> None:

        pool = ResourcePool(
            [Resource.COAL],
            []
        )

        pool.put_resources([Resource.OIL, Resource.URANIUM])

        self.assertEqual(
            pool.resources,
            [Resource.COAL, Resource.OIL, Resource.URANIUM]
        )

    # Kontrola textoveho vypisu
    def test_to_string(self) -> None:

        pool = ResourcePool(
            [Resource.COAL, Resource.OIL],
            [Resource.URANIUM]
        )

        result = json.loads(pool.to_string())

        self.assertEqual(result["resources"], ["COAL", "OIL"])
        self.assertEqual(result["storage_space"], ["URANIUM"])
    
    def test_with_resource_market(self) -> None:

        pool = ResourcePool(
            [Resource.COAL, Resource.COAL],
            [Resource.URANIUM]
        )

        step1 = {
            Resource.COAL: 1,
            Resource.OIL: 0,
            Resource.GARBAGE: 0,
            Resource.URANIUM: 0
        }

        step2 = {
            Resource.COAL: 0,
            Resource.OIL: 0,
            Resource.GARBAGE: 0,
            Resource.URANIUM: 0
        }

        step3 = {
            Resource.COAL: 0,
            Resource.OIL: 0,
            Resource.GARBAGE: 0,
            Resource.URANIUM: 0
        }

        refilling = {
            1: step1,
            2: step2,
            3: step3
        }

        market = ResourceMarket(
            pool,
            [Resource.OIL],
            refilling
        )

        market.refill()

        self.assertEqual(pool.resources, [Resource.COAL])

        price = market.get_price([Resource.URANIUM])

        self.assertEqual(price, 16)

        market.take_resources([Resource.URANIUM])

        self.assertEqual(pool.storage_space, [])

