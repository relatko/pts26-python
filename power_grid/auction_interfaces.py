"""Interfaces that AuctionPowerPlants needs from the market and from the player boards."""
# pylint: disable=unused-argument, duplicate-code
from typing import Optional, Protocol, Sequence

from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


class InterfacePowerPlantMarketAuctionPowerPlants(Protocol):
    """What the auction needs from PowerPlantMarket."""

    def can_take_power_plant(
        self, ppn: PowerPlantNumber, price: int
    ) -> Optional[RequestError]:
        """None if the plant is in the current market and `price` is an allowed bid."""
        ...

    def minimum_bid(self, ppn: PowerPlantNumber) -> int:
        """The lowest allowed bid for the plant (1 for the discounted plant)."""
        ...

    def take_power_plant(self, ppn: PowerPlantNumber) -> PowerPlant:
        """Removes the plant from the market and refills the market."""
        ...

    def remove_discounted_power_plant(self) -> None:
        """End of the auction phase: removes the discounted plant if nobody bought it."""
        ...


class InterfacePlayerBoardFacadeAuctionPowerPlants(Protocol):
    """What the auction needs from PlayerBoardFacade."""

    def has_enough_money(self, amount: int) -> bool:
        """True if the player can pay `amount`."""
        ...

    def receive_power_plant(self, ppn: PowerPlantNumber, price: int) -> bool:
        """Pays `price` and takes the plant. False if the player is above the plant limit."""
        ...

    def remove_power_plant(
        self, ppn: PowerPlantNumber, removed_resources: Sequence[Resource]
    ) -> Optional[RequestError]:
        """Scraps a plant (and possibly some resources)."""
        ...
