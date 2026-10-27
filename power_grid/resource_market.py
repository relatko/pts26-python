from __future__ import annotations
import json
from collections import Counter
from typing import Mapping, Sequence, Any
from power_grid.simple_types import Resource
from power_grid.interfaces import InterfaceResourcePoolResourceMarket


class ResourceMarket:
    _step: int
    _resources: dict[Resource, int]
    _pool: InterfaceResourcePoolResourceMarket
    _expanded_prices: dict[Resource, list[int]]
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
        self._expanded_prices = {
            Resource.COAL: sorted(3*[1, 2, 3, 4, 5, 6, 7, 8]),
            Resource.OIL: sorted(3*[1, 2, 3, 4, 5, 6, 7, 8]),
            Resource.GARBAGE: sorted(3*[1, 2, 3, 4, 5, 6, 7, 8]),
            Resource.URANIUM: [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16]
        }
        assert all(ResourceMarket.MAX_RESOURCES[x] == len(
            self._expanded_prices[x]) for x in Resource)
        self._pool = pool
        starting_counts = Counter(starting_resources)
        assert all(0 <= starting_counts[x] <= ResourceMarket.MAX_RESOURCES[x]
                   for x in Resource)
        self._resources = {x: starting_counts[x] for x in Resource}
        assert len(refilling_pattern) == 3
        self._refilling_pattern = {}
        for step in (1, 2, 3):
            pattern: Mapping[Resource, int] = refilling_pattern[step]
            assert len(pattern) == 4
            assert all(0 <= pattern[x] <= ResourceMarket.MAX_RESOURCES[x]
                       for x in Resource)
            self._refilling_pattern[step] = dict(pattern)

    def start_step2(self) -> None:
        assert self._step == 1
        self._step = 2

    def start_step3(self) -> None:
        assert self._step < 3
        self._step = 3

    def refill(self) -> None:
        for resource in Resource:
            refill_count = self._refilling_pattern[self._step][resource]
            from_pool = self._pool.take_resources(refill_count*[resource,])
            assert all(x == resource for x in from_pool)
            self._resources[resource] += len(from_pool)
            assert self._resources[resource] <= ResourceMarket.MAX_RESOURCES[resource]

    def get_price(self, desired: list[Resource]) -> int | None:
        total_price = 0
        unavailable: list[Resource] = []
        desired_counts = Counter(desired)
        for resource in Resource:
            required: int = desired_counts[resource]
            available: int = self._resources[resource]
            prices = self._expanded_prices[resource]
            if required <= available:
                total_price += sum(prices[len(prices)-available:
                                          len(prices)-available+required])
            else:
                total_price += sum(prices[len(prices)-available:])
                from_storage: int = required-available
                total_price += from_storage*prices[-1]
                unavailable += from_storage*[resource,]
        if not unavailable:
            return total_price
        if self._pool.can_take_resources_from_storage_space(unavailable):
            return total_price
        return None

    def take_resources(self, resources: list[Resource]) -> None:
        to_take_counts = Counter(resources)
        for resource in Resource:
            to_take = to_take_counts[resource]
            from_storage = to_take - self._resources[resource]
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
