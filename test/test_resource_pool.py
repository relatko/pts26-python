import json
import unittest

from power_grid.interfaces import InterfaceResourcePoolResourceMarket
from power_grid.resource_market import ResourceMarket
from power_grid.resource_pool import ResourcePool
from power_grid.simple_types import Resource


class TestResourcePool(unittest.TestCase):
    def setUp(self) -> None:
        # The pool holds 2 coal and 1 oil
        self.pool: ResourcePool = ResourcePool(
            [Resource.COAL, Resource.COAL, Resource.OIL])

    def test_empty_pool_by_default(self) -> None:
        # A pool created without resources cannot give anything
        self.assertFalse(
            ResourcePool().can_take_resources_from_storage_space([Resource.COAL]))

    def test_can_take_available_resources(self) -> None:
        # Check if it can take resources
        self.assertTrue(self.pool.can_take_resources_from_storage_space(
            [Resource.COAL, Resource.OIL]))
        # Taking nothing is always possible
        self.assertTrue(self.pool.can_take_resources_from_storage_space([]))

    def test_cannot_take_missing_or_too_many_resources(self) -> None:
        # There is no uranium in the pool
        self.assertFalse(
            self.pool.can_take_resources_from_storage_space([Resource.URANIUM]))
        # There are only 2 coal in the pool, not 3
        self.assertFalse(self.pool.can_take_resources_from_storage_space(
            [Resource.COAL] * 3))

    def test_get_from_storage_space_removes_resources(self) -> None:
        # Take resources
        self.pool.get_from_storage_space([Resource.COAL])
        # One coal is left, so 1 coal is available but 2 are not
        self.assertTrue(
            self.pool.can_take_resources_from_storage_space([Resource.COAL]))
        self.assertFalse(self.pool.can_take_resources_from_storage_space(
            [Resource.COAL, Resource.COAL]))

    def test_get_from_storage_space_fails_without_changes(self) -> None:
        # The oil is there but the uranium is not: nothing may be removed
        with self.assertRaises(ValueError):
            self.pool.get_from_storage_space([Resource.OIL, Resource.URANIUM])
        self.assertTrue(
            self.pool.can_take_resources_from_storage_space([Resource.OIL]))

    def test_take_resources_returns_what_it_took(self) -> None:
        self.assertEqual(
            self.pool.take_resources([Resource.COAL, Resource.OIL]),
            [Resource.COAL, Resource.OIL])

    def test_take_resources_takes_only_what_is_available(self) -> None:
        # 3 coal were requested but only 2 are in the pool
        taken = self.pool.take_resources([Resource.COAL] * 3)
        self.assertEqual(taken, [Resource.COAL, Resource.COAL])
        self.assertFalse(
            self.pool.can_take_resources_from_storage_space([Resource.COAL]))

    def test_put_resources_adds_them(self) -> None:
        # Put resources into the pool and check that they can be taken
        self.pool.put_resources([Resource.URANIUM])
        self.assertTrue(
            self.pool.can_take_resources_from_storage_space([Resource.URANIUM]))

    def test_constructor_copies_the_initial_list(self) -> None:
        # Changing the list after creating the pool must not change the pool
        initial = [Resource.OIL]
        pool = ResourcePool(initial)
        initial.append(Resource.OIL)
        self.assertFalse(pool.can_take_resources_from_storage_space(
            [Resource.OIL, Resource.OIL]))

    def test_to_string_is_json_with_amounts(self) -> None:
        self.assertEqual(
            json.loads(self.pool.to_string()),
            {"coal": 2, "oil": 1, "garbage": 0, "uranium": 0})

    def test_pool_can_be_used_as_the_resource_market_pool(self) -> None:
        # mypy checks that the pool has everything the market needs
        pool: InterfaceResourcePoolResourceMarket = self.pool
        self.assertIsNotNone(pool)


class TestResourcePoolInResourceMarket(unittest.TestCase):
    def setUp(self) -> None:
        # Every refill puts 1 resource of each kind on the market
        pattern = {step: {resource: 1 for resource in Resource}
                   for step in (1, 2, 3)}
        self.pool: ResourcePool = ResourcePool(
            [Resource.COAL] * 5 + [Resource.OIL] * 5 + [Resource.GARBAGE] * 5)
        self.market: ResourceMarket = ResourceMarket(self.pool, [], pattern)

    def test_refill_takes_resources_from_the_pool(self) -> None:
        self.market.refill()
        # The pool had no uranium, so only 3 kinds were refilled
        state = json.loads(self.market.to_string())
        self.assertEqual(
            (state["coal"], state["oil"], state["garbage"], state["uranium"]),
            (1, 1, 1, 0))
        self.assertEqual(state["pool"]["coal"], 4)

    def test_buying_more_than_the_market_has_uses_the_pool(self) -> None:
        # Market is empty, so the coal comes from the pool
        self.market.take_resources([Resource.COAL])
        self.assertEqual(json.loads(self.market.to_string())["pool"]["coal"], 4)