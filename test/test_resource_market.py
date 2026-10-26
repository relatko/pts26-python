# pylint: disable=too-many-instance-attributes, too-many-public-methods
from typing import Any, Sequence
import unittest
import json
from power_grid.resource_market import ResourceMarket
from power_grid.simple_types import Resource
from power_grid.interfaces import InterfaceResourcePoolResourceMarket


class ResourcePoolFake(InterfaceResourcePoolResourceMarket):
    pool: list[Resource]
    storage_resource: Resource
    storage_count: int

    def __init__(self) -> None:
        self.pool = []
        self.storage_resource = Resource.URANIUM
        self.storage_count = 1000

    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        res: list[Resource] = list(resources)
        if all(x == self.storage_resource for x in res):
            return len(res) <= self.storage_count
        return False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        res: list[Resource] = list(resources)
        assert all({x == self.storage_resource for x in res})
        self.storage_count -= len(res)
        assert self.storage_count >= 0

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        to_return: list[Resource] = []
        to_take: list[Resource] = list(resources)
        for resource in to_take:
            if resource in self.pool:
                self.pool.remove(resource)
                to_return.append(resource)
        return to_return

    def to_string(self) -> str:
        return json.dumps("FakePool")


if __name__ == "__main__":
    unittest.main()


class TestResourceMarket(unittest.TestCase):
    def setUp(self) -> None:
        self.pool: ResourcePoolFake = ResourcePoolFake()
        refilling_pattern = {
            1: {
                Resource.COAL: 0,
                Resource.OIL: 2,
                Resource.GARBAGE: 9,
                Resource.URANIUM: 1
            },
            2: {
                Resource.COAL: 8,
                Resource.OIL: 2,
                Resource.GARBAGE: 0,
                Resource.URANIUM: 3
            },
            3: {
                Resource.COAL: 0,
                Resource.OIL: 2,
                Resource.GARBAGE: 0,
                Resource.URANIUM: 8
            },
        }
        resources_to_market: list[Resource] = [
            Resource.COAL, Resource.OIL, Resource.GARBAGE]
        self.pool.pool = (ResourceMarket.MAX_RESOURCES[Resource.COAL]-1)*[Resource.COAL,] \
            + (ResourceMarket.MAX_RESOURCES[Resource.OIL]-1)*[Resource.OIL,] \
            + (ResourceMarket.MAX_RESOURCES[Resource.GARBAGE]-1)*[Resource.GARBAGE,] \
            + ResourceMarket.MAX_RESOURCES[Resource.URANIUM]*[Resource.URANIUM,]
        self.market: ResourceMarket = ResourceMarket(
            self.pool, resources_to_market, refilling_pattern)

    def check_resources(self, coal: int, oil: int, garbage: int, uranium: int) -> None:
        state: Any = json.loads(self.market.to_string())
        self.assertEqual(state["coal"], coal)
        self.assertEqual(state["oil"], oil)
        self.assertEqual(state["garbage"], garbage)
        self.assertEqual(state["uranium"], uranium)

    def test_refill_with_enough_resources(self) -> None:
        self.check_resources(1, 1, 1, 0)
        self.market.refill()
        self.check_resources(1, 3, 10, 1)
        self.market.start_step2()
        self.market.refill()
        self.check_resources(9, 5, 10, 4)
        self.market.start_step3()
        self.market.refill()
        self.check_resources(9, 7, 10, 12)

    def test_refill_with_not_enough_resources(self) -> None:
        self.check_resources(1, 1, 1, 0)
        self.market.refill()
        self.market.refill()
        self.market.refill()
        self.check_resources(1, 7, 24, 3)
        self.market.start_step2()
        self.market.start_step3()
        self.market.refill()
        self.market.refill()
        self.check_resources(1, 11, 24, 12)

    def test_price_calculation_without_storage(self) -> None:
        self.market.refill()
        self.check_resources(1, 3, 10, 1)
        price = self.market.get_price(
            7*[Resource.GARBAGE,]+[Resource.URANIUM,])
        self.assertEqual(price, 1*5+3*6+3*7+16)

    def test_price_calculation_with_storage(self) -> None:
        self.market.refill()
        self.market.refill()
        self.check_resources(1, 5, 19, 2)
        price = self.market.get_price(4*[Resource.URANIUM,])
        self.assertEqual(price, 14+16+2*16)

    def test_price_calculation_not_enough_resources(self) -> None:
        self.market.refill()
        self.market.refill()
        self.check_resources(1, 5, 19, 2)
        price = self.market.get_price(2*[Resource.COAL,])
        self.assertIsNone(price)

    def test_take_resources_sucess(self) -> None:
        self.market.refill()
        self.check_resources(1, 3, 10, 1)
        self.market.take_resources(
            [Resource.COAL, Resource.GARBAGE, Resource.GARBAGE, Resource.URANIUM])
        self.check_resources(0, 3, 8, 0)
        self.assertEqual(self.pool.storage_count, 1000)

    def test_take_resources_sucess_using_storage(self) -> None:
        self.market.refill()
        self.check_resources(1, 3, 10, 1)
        self.market.take_resources(
            [Resource.COAL, Resource.GARBAGE, Resource.URANIUM, Resource.URANIUM])
        self.check_resources(0, 3, 9, 0)
        self.assertEqual(self.pool.storage_count, 999)

    def test_take_resources_failure(self) -> None:
        self.market.refill()
        self.check_resources(1, 3, 10, 1)
        with self.assertRaises(AssertionError):
            self.market.take_resources([Resource.COAL, Resource.COAL])
