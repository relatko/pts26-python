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

    def numberOfSuppliableTowns(
        self, resources: Sequence[Resource], powerplants: Sequence[PowerPlant]
    ) -> int | RequestError:
        """Returns the number of towns that can be supplied or an error."""
        ...

    def numberOfSuppliebleTowns(
        self, resources: Sequence[Resource], powerplants: Sequence[PowerPlant]
    ) -> int:
        """Returns the number of towns that can be supplied."""
        ...


class UsePowerPlants(Protocol):
    """Interface for a class that manages a player's power plants."""

    def add_power_plant(self, plant: PowerPlant) -> None:
        """Adds a new power plant to the player's collection."""
        ...

    def get_power_plants(self) -> Sequence[PowerPlant]:
        """Returns the list of power plants owned by the player."""
        ...


class MaximumNumberOfUsablePowerPlants(Protocol):
    """Interface for calculating how many power plants can be powered."""

    def calculate_max_usable(
        self, plants: Sequence[PowerPlant], resources: Sequence[Resource]
    ) -> int:
        """Calculates the maximum number of power plants that can run with the given resources."""
        ...