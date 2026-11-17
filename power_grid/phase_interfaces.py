# pylint: disable=unused-argument, duplicate-code
from collections.abc import Sequence
from typing import Protocol

from power_grid.simple_types import (
    PhaseStatus,
    PlayerColor,
    PowerPlantNumber,
    RequestError,
    Resource,
)


class InterfaceDeterminePlayerOrderGameController(Protocol):
    """What GameController needs from DeterminePlayerOrder."""

    def reorder(self) -> list[PlayerColor]:
        """Returns the new player order."""
        ...

    def game_result(self) -> list[PlayerColor]:
        """Returns the final ranking of players."""
        ...


class InterfaceAuctionPowerPlantsGameController(Protocol):
    """What GameController needs from AuctionPowerPlants."""

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        ...

    def select_power_plant_to_bid(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            first_bid: int) -> PhaseStatus | RequestError:
        ...

    def do_not_want_power_plant(self, player: PlayerColor) -> PhaseStatus | RequestError:
        ...

    def bid_for_current_power_plant(
            self, player: PlayerColor, bid: int) -> PhaseStatus | RequestError:
        ...

    def do_not_bid_for_current_power_plant(
            self, player: PlayerColor) -> PhaseStatus | RequestError:
        ...

    def remove_power_plant(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            resources: Sequence[Resource]) -> PhaseStatus | RequestError:
        ...

    def get_state(self) -> str:
        ...


class InterfaceBuyingResourcesGameController(Protocol):
    """What GameController needs from BuyingResources."""

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        ...

    def buy_resources(
            self, player: PlayerColor,
            resources: Sequence[Resource]) -> PhaseStatus | RequestError:
        ...

    def get_state(self) -> str:
        ...


class InterfaceBuildingHousesGameController(Protocol):
    """What GameController needs from BuildingHouses."""

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        ...

    def build_houses(
            self, player: PlayerColor,
            town_names: Sequence[str]) -> PhaseStatus | RequestError:
        ...

    def get_state(self) -> str:
        ...


class InterfaceBureaucracyGameController(Protocol):
    """What GameController needs from Bureaucracy."""

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        ...

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> PhaseStatus | RequestError:
        ...

    def get_state(self) -> str:
        ...
        