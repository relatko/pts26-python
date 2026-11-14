import json
import unittest

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
            ResourcePool().canTakeResourcesFromStorageSpace([Resource.COAL]))

    def test_can_take_available_resources(self) -> None:
        # Check if it can take resources
        self.assertTrue(self.pool.canTakeResourcesFromStorageSpace(
            [Resource.COAL, Resource.OIL]))
        # Taking nothing is always possible
        self.assertTrue(self.pool.canTakeResourcesFromStorageSpace([]))

    def test_cannot_take_missing_or_too_many_resources(self) -> None:
        # There is no uranium in the pool
        self.assertFalse(
            self.pool.canTakeResourcesFromStorageSpace([Resource.URANIUM]))
        # There are only 2 coal in the pool, not 3
        self.assertFalse(self.pool.canTakeResourcesFromStorageSpace(
            [Resource.COAL] * 3))

    def test_take_resources_removes_them(self) -> None:
        # Take resources
        self.pool.takeResources([Resource.COAL])
        # One coal is left, so 1 coal is available but 2 are not
        self.assertTrue(
            self.pool.canTakeResourcesFromStorageSpace([Resource.COAL]))
        self.assertFalse(self.pool.canTakeResourcesFromStorageSpace(
            [Resource.COAL, Resource.COAL]))

    def test_put_resources_adds_them(self) -> None:
        # Put resources into the pool and check that they can be taken
        self.pool.putResources([Resource.URANIUM])
        self.assertTrue(
            self.pool.canTakeResourcesFromStorageSpace([Resource.URANIUM]))

    def test_constructor_copies_the_initial_list(self) -> None:
        # Changing the list after creating the pool must not change the pool
        initial = [Resource.OIL]
        pool = ResourcePool(initial)
        initial.append(Resource.OIL)
        self.assertFalse(pool.canTakeResourcesFromStorageSpace(
            [Resource.OIL, Resource.OIL]))

    # ---- Known problems. Remove @expectedFailure once the class is fixed. ----

    @unittest.expectedFailure
    def test_get_from_storage_space_removes_resources(self) -> None:
        # ResourceMarket.take_resources calls this to take the resources
        # out of the pool, so they must be gone afterwards.
        taken = self.pool.getFromStorageSpace([Resource.COAL])
        self.assertEqual(taken, [Resource.COAL])
        self.assertFalse(self.pool.canTakeResourcesFromStorageSpace(
            [Resource.COAL, Resource.COAL]))

    @unittest.expectedFailure
    def test_to_string_is_json(self) -> None:
        # ResourceMarket.to_string calls json.loads on the pool's string.
        json.loads(self.pool.toString())

    @unittest.expectedFailure
    def test_pool_works_inside_resource_market(self) -> None:
        # ResourceMarket expects snake_case methods (take_resources, ...),
        # but ResourcePool has camelCase ones, so refill() fails.
        pattern = {step: {resource: 1 for resource in Resource}
                   for step in (1, 2, 3)}
        market = ResourceMarket(
            self.pool,  # type: ignore[arg-type]
            [Resource.COAL] * 3, pattern)
        market.refill()
        json.loads(market.to_string())