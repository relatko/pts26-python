from collections.abc import Hashable, Mapping, Sequence
from itertools import combinations
from typing import TypeVar

from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource

MAX_POWER_PLANTS = 3
STORAGE_FACTOR = 2  # a plant can store up to 2x the resources it needs per run

Key = TypeVar("Key", bound=Hashable)


def _demands_can_be_met(demands: Sequence[tuple[int, frozenset[Key]]],
                        supply: Mapping[Key, int]) -> bool:
    """
    Checks whether every demand can be served from the supply.

    Each demand is (amount, set of keys it may take from). Supply is the capacity
    per key. The demands can all be met exactly when, for every group of demands,
    their total amount does not exceed the total supply of all keys they may use
    (Hall's condition). With at most 3 plants and 4 resources the groups are few.
    """
    for size in range(1, len(demands) + 1):
        for group in combinations(demands, size):
            needed = sum(amount for amount, _ in group)
            usable_keys: set[Key] = set()
            for _, keys in group:
                usable_keys |= keys
            if needed > sum(supply.get(key, 0) for key in usable_keys):
                return False
    return True


def _count(resources: Sequence[Resource]) -> dict[Resource, int]:
    """Counts how many units of each resource are in the list."""
    counts: dict[Resource, int] = {resource: 0 for resource in Resource}
    for resource in resources:
        counts[resource] += 1
    return counts


class PlayerPowerPlants:
    """Stores the power plants a player owns (at most MAX_POWER_PLANTS)."""

    def __init__(self, plants: Sequence[PowerPlant] = ()) -> None:
        self._plants: list[PowerPlant] = []
        for plant in plants:
            self.add_power_plant(plant)

    def can_add_power_plant(self) -> bool:
        """Returns True if the player is still below the power plant limit."""
        return len(self._plants) < MAX_POWER_PLANTS

    def add_power_plant(self, plant: PowerPlant) -> None:
        """
        Adds a power plant to the player's collection.

        Raises ValueError if the limit is reached or the plant is already owned.
        """
        if not self.can_add_power_plant():
            raise ValueError("Player already owns the maximum number of power plants")
        if any(owned.number == plant.number for owned in self._plants):
            raise ValueError(f"Power plant {plant.number.number} is already owned")
        self._plants.append(plant)

    def remove_power_plant(self, number: PowerPlantNumber) -> RequestError | None:
        """Removes the plant with the given number, or returns an error if not owned."""
        for plant in self._plants:
            if plant.number == number:
                self._plants.remove(plant)
                return None
        return RequestError(f"Power plant {number.number} is not owned")

    def get_power_plants(self) -> Sequence[PowerPlant]:
        """Returns the power plants owned by the player."""
        return list(self._plants)

    def best_power_plant(self) -> PowerPlantNumber | None:
        """Returns the highest plant number the player owns (None if no plants)."""
        if not self._plants:
            return None
        return max((plant.number for plant in self._plants),
                   key=lambda number: number.number)

    def can_store_resources(self, resources: Sequence[Resource]) -> bool:
        """
        Checks whether the given resources fit into the storage of the owned plants.

        A plant stores up to STORAGE_FACTOR * resourceAmount units, shared between
        all the resources it accepts (hybrid plants).
        """
        capacity = {index: STORAGE_FACTOR * plant.resourceAmount
                    for index, plant in enumerate(self._plants)}
        demands: list[tuple[int, frozenset[int]]] = []
        for resource, amount in _count(resources).items():
            if amount > 0:
                accepting = frozenset(
                    index for index, plant in enumerate(self._plants)
                    if resource in plant.acceptedResources)
                demands.append((amount, accepting))
        return _demands_can_be_met(demands, capacity)

    def number_of_connectable_cities(self, resources: Sequence[Resource]) -> int:
        """Returns the maximum number of cities the owned plants can power with the resources."""
        best = 0
        for size in range(len(self._plants) + 1):
            for chosen in combinations(self._plants, size):
                if self._can_run(chosen, resources):
                    best = max(best, sum(plant.numberOfCities for plant in chosen))
        return best

    def cities_powered_by(self, numbers: Sequence[PowerPlantNumber],
                          resources: Sequence[Resource]) -> int | RequestError:
        """
        Returns how many cities the chosen plants power with the given resources.

        Returns a RequestError if a plant is not owned, is listed twice, or the
        resources are not enough. Does not change any state: the caller removes the
        burned resources (PlayerResources.remove_resources).
        """
        chosen: list[PowerPlant] = []
        for number in numbers:
            owned = [plant for plant in self._plants if plant.number == number]
            if not owned:
                return RequestError(f"Power plant {number.number} is not owned")
            if owned[0] in chosen:
                return RequestError(f"Power plant {number.number} listed twice")
            chosen.append(owned[0])
        if not self._can_run(chosen, resources):
            return RequestError("Not enough resources to run the chosen power plants")
        return sum(plant.numberOfCities for plant in chosen)

    @staticmethod
    def _can_run(plants: Sequence[PowerPlant], resources: Sequence[Resource]) -> bool:
        """Checks whether the resources can fuel all the given plants at the same time."""
        demands = [(plant.resourceAmount, frozenset(plant.acceptedResources))
                   for plant in plants if plant.resourceAmount > 0]
        return _demands_can_be_met(demands, _count(resources))
