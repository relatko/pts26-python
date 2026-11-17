from collections.abc import Sequence

from power_grid.simple_types import Resource


class PlayerResources:
    """Stores the resources a player currently holds."""

    def __init__(self, resources: Sequence[Resource] = ()) -> None:
        self._amounts: dict[Resource, int] = {resource: 0 for resource in Resource}
        self.add_resources(resources)

    def add_resources(self, resources: Sequence[Resource]) -> None:
        """Adds the given resources to the player's storage."""
        for resource in resources:
            self._amounts[resource] += 1

    def remove_resources(self, resources: Sequence[Resource]) -> None:
        """
        Removes the given resources from the player's storage.

        Raises ValueError (and changes nothing) if the player does not own them all.
        """
        needed: dict[Resource, int] = {resource: 0 for resource in Resource}
        for resource in resources:
            needed[resource] += 1
        for resource, amount in needed.items():
            if amount > self._amounts[resource]:
                raise ValueError(f"Not enough {resource.name}: need {amount}, "
                                 f"have {self._amounts[resource]}")
        for resource, amount in needed.items():
            self._amounts[resource] -= amount

    def get_resources(self) -> Sequence[Resource]:
        """Returns all stored resources as a list (one entry per unit)."""
        result: list[Resource] = []
        for resource, amount in self._amounts.items():
            result.extend([resource] * amount)
        return result

    def amount_of(self, resource: Resource) -> int:
        """Returns how many units of the given resource the player holds."""
        return self._amounts[resource]
