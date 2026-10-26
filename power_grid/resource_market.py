from __future__ import annotations
import json
from typing import Mapping, Sequence, Optional, Any
from power_grid.simple_types import Resource
from power_grid.interfaces import InterfaceResourcePoolResourceMarket


class ResourceMarket:
    _step: int
    _resources: dict[Resource, int]
    _pool: InterfaceResourcePoolResourceMarket
    _price_breaks: dict[Resource, list[int]]
    _prices: dict[Resource, list[int]]
    _refilling_pattern: dict[int, dict[Resource, int]]
    MAX_RESOURCES: dict[Resource, int] = {
        Resource.COAL: 24,
        Resource.OIL: 24,
        Resource.GARBAGE: 24,
        Resource.URANIUM: 12,
    }

    def __init__(self, pool: InterfaceResourcePoolResourceMarket,
                 starting_resources: Sequence[Resource],
                 refilling_pattern: Mapping[int, Mapping[Resource, int]]):
        self._step = 1
        self._price_breaks = {
            Resource.COAL: 8*[3,], Resource.OIL: 8*[3,],
            Resource.GARBAGE: 8*[3,], Resource.URANIUM: 12*[1,]}
        assert (all(
            sum(self._price_breaks[x]) == ResourceMarket.MAX_RESOURCES[x] for x in Resource))
        self._prices = {Resource.COAL: [1, 2, 3, 4, 5, 6, 7, 8],
                        Resource.OIL: [1, 2, 3, 4, 5, 6, 7, 8],
                        Resource.GARBAGE: [1, 2, 3, 4, 5, 6, 7, 8],
                        Resource.URANIUM: [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16]}
        assert all(len(self._price_breaks[x]) == len(self._prices[x])
                   for x in Resource)
        self._pool = pool
        self._resources = {x: starting_resources.count(x) for x in Resource}
        assert all(0 <= self._resources[x] <= sum(self._price_breaks[x])
                   for x in Resource)
        assert len(refilling_pattern) == 3
        self._refilling_pattern = {}
        for step in (1, 2, 3):
            pattern: Mapping[Resource, int] = refilling_pattern[step]
            assert len(pattern) == 4
            assert all((0 <= pattern[x] <= sum(self._price_breaks[x])
                        for x in Resource))
            self._refilling_pattern[step] = dict(pattern)

    def start_step2(self) -> None:
        assert self._step == 1
        self._step = 2

    def start_step3(self) -> None:
        assert self._step < 3
        self._step = 3

    def refill(self) -> None:
        for resource in Resource:
            refill_count: int = self._refilling_pattern[self._step][resource]
            from_pool = self._pool.take_resources(refill_count*[resource,])
            assert all(x == resource for x in from_pool)
            self._resources[resource] += len(from_pool)
            assert self._resources[resource] <= sum(
                self._price_breaks[resource])

    def get_price(self, desired: list[Resource]) -> Optional[int]:
        price = 0
        unavailable: list[Resource] = []
        for resource in Resource:
            required: int = desired.count(resource)
            available: int = self._resources[resource]
            prices: list[int] = [y for (x, y) in zip(
                self._price_breaks[resource], self._prices[resource]) for _ in range(x)]
            if required <= available:
                price += sum(prices[len(prices) -
                             available:len(prices)-(available-required)])
            else:
                price += sum(prices[len(prices)-available:])
                from_storage: int = required-available
                price += from_storage*prices[-1]
                unavailable += from_storage*[resource,]
        if not unavailable:
            return price
        if self._pool.can_take_resources_from_storage_space(unavailable):
            return price
        return None

    def take_resources(self, resources: list[Resource]) -> None:
        for resource in Resource:
            to_take: int = resources.count(resource)
            from_storage: int = to_take - self._resources[resource]
            if from_storage > 0:
                self._pool.get_from_storage_space(from_storage*[resource, ])
                self._resources[resource] = 0
            else:
                self._resources[resource] -= to_take

    def to_string(self) -> str:
        state: Any = {
            "coal": self._resources[Resource.COAL],
            "oil": self._resources[Resource.OIL],
            "garbage": self._resources[Resource.GARBAGE],
            "uranium": self._resources[Resource.URANIUM],
            "pool": json.loads(self._pool.to_string()),
        }
        return json.dumps(state)
