# pylint: disable=unused-argument, duplicate-code
from typing import Sequence, Protocol
from power_grid.simple_types import Resource, PowerPlant, RequestError


class InterfaceResourcePoolResourceMarket(Protocol):
    """Interface for the resource market in the game (provided by the teacher)."""

    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        """Checks if the requested resources can be taken from the market's storage."""
        ...

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        """Takes the specified resources from the market's storage."""
        ...

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        """Takes resources from the market (logic depends on implementation)."""
        ...

    def to_string(self) -> str:
        """Returns a string representation of the resource market."""
        ...


class StoreResources(Protocol):
    """Interface for a class that stores and manages a player's resources."""

    def canStoreResources(
        self, resources: Sequence[Resource], powerplants: Sequence[PowerPlant]
    ) -> bool:
        """Checks if the player can store the given resources."""
        ...


class UsePowerPlants(Protocol):
    """Interface for a class that manages a player's power plants."""

    def numberOfSuppliableTowns(
        self, resources: Sequence[Resource], powerplants: Sequence[PowerPlant]
    ) -> int | RequestError:
        """Returns the number of towns that can be supplied or an error."""
        ...


class MaximumNumberOfUsablePowerPlants(Protocol):
    """Interface for calculating how many power plants can be powered."""

    def numberOfUsablePowerPlants(
        self, resources: Sequence[Resource], powerplants: Sequence[PowerPlant]
    ) -> int:
        """Calculates the number of usable power plants with the given resources."""
        ...