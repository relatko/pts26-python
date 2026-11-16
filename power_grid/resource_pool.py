# Storage with the resources that are not on the resource market.
import json
from collections import Counter
from collections.abc import Sequence

from power_grid.simple_types import Resource


class ResourcePool:
    # Resources waiting outside of the market; the market refills from here.

    def __init__(self, initial_resources: Sequence[Resource] = ()) -> None:
        self._amounts: Counter[Resource] = Counter(initial_resources)

    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        # True if the pool contains all the requested resources.
        return all(self._amounts[resource] >= amount
                   for resource, amount in Counter(resources).items())

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        # Removes exactly the requested resources.
        #
        # Raises ValueError (and changes nothing) if the pool does not contain them all.
        if not self.can_take_resources_from_storage_space(resources):
            raise ValueError("The pool does not contain the requested resources")
        self._amounts.subtract(resources)

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        # Removes as many of the requested resources as the pool has and returns them.
        taken: list[Resource] = []
        for resource in resources:
            if self._amounts[resource] > 0:
                self._amounts[resource] -= 1
                taken.append(resource)
        return taken

    def put_resources(self, resources: Sequence[Resource]) -> None:
        # Puts the resources into the pool.
        self._amounts.update(resources)

    def to_string(self) -> str:
        # JSON object with the amount of every resource.
        return json.dumps({resource.name.lower(): self._amounts[resource]
                           for resource in Resource})