
from power_grid.simple_types import Resource


class ResourcePool:
    def __init__(self, initial_resources: list[Resource] | None = None) -> None:
        # Initialize the pool with a list of resources
        self._resources: list[Resource] = initial_resources.copy() if initial_resources else []

    def canTakeResourcesFromStorageSpace(self, resources: list[Resource]) -> bool:
        # Check if there are enough resources in the pool to take
        needed: dict[Resource, int] = {}
        for res in resources:
            needed[res] = needed.get(res, 0) + 1
            
        available: dict[Resource, int] = {}
        for res in self._resources:
            available[res] = available.get(res, 0) + 1
            
        for res, count in needed.items():
            if available.get(res, 0) < count:
                return False
        return True

    def getFromStorageSpace(self, resources: list[Resource]) -> list[Resource]:
        # Returns the list of requested resources
        return resources.copy()

    def takeResources(self, resources: list[Resource]) -> None:
        # Takes resources from the pool
        for res in resources:
            if res in self._resources:
                self._resources.remove(res)

    def putResources(self, resources: list[Resource]) -> None:
        # Puts resources into the pool
        self._resources.extend(resources)

    def toString(self) -> str:
        # Returns a string representation (for game saving)
        return str(self._resources)