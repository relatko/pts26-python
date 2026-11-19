# pylint: disable=unused-argument, duplicate-code
from typing import Sequence
from power_grid.simple_types import (
    PlayerColor,
    PowerPlant,
    PowerPlantNumber,
    RequestError,
    Resource,
)


class InterfaceResourcePoolResourceMarket:
    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        assert False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        assert False

    def to_string(self) -> str:
        assert False


class InterfacePlayerBoardFacade:
    """Boundary between phases/controllers and a player's board state"""

    def best_power_plant_number(self) -> PowerPlantNumber:
        assert False

    def outstanding_money(self) -> int:
        assert False

    def spend_money(self, amount: int) -> None:
        assert False

    def number_of_connectable_cities(self) -> int:
        assert False

    def has_enough_money(self, amount: int) -> bool:
        assert False

    def receive_power_plant(self, ppn: PowerPlantNumber, price: int) -> bool:
        assert False

    def remove_power_plant(
        self, ppn: PowerPlantNumber, removed_resources: Sequence[Resource]
    ) -> RequestError | None:
        assert False

    def buy_resources(self, resources: Sequence[Resource]) -> RequestError | None:
        assert False

    def use_power_plants(
        self, ppns: Sequence[PowerPlantNumber], resources_to_burn: Sequence[Resource]
    ) -> RequestError | None:
        assert False

    def state(self) -> str:
        assert False


class InterfaceTowns:
    """Boundary for city ownership and house placement"""

    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str], max_money: int
    ) -> int | RequestError:
        assert False

    def get_number_of_houses(self, player: PlayerColor) -> int:
        assert False

    def get_max_number_of_houses(self) -> int:
        assert False

    def start_step_2(self) -> None:
        assert False

    def start_step_3(self) -> None:
        assert False


class InterfacePowerPlantMarket:
    """Boundary for market queries and end of turn card updates"""

    def can_take_power_plant(
        self, ppn: PowerPlantNumber, price: int
    ) -> RequestError | None:
        assert False

    def take_power_plant(self, ppn: PowerPlantNumber) -> PowerPlant:
        assert False

    def remove_discounted_power_plant(self, value: int) -> None:
        assert False

    def remove_power_plants_cheaper_than(self, value: int) -> None:
        assert False

    def prepare_next_turn(self) -> None:
        assert False

    def is_step_3_start(self) -> bool:
        assert False

    def start_step_3(self) -> None:
        assert False


class InterfaceResourceMarket:
    """Boundary for refilling and querying the resource market"""

    def start_step_2(self) -> None:
        assert False

    def start_step_3(self) -> None:
        assert False

    def refill(self) -> None:
        assert False

    def get_price(self, resources: Sequence[Resource]) -> int | None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> None:
        assert False


class InterfaceCheckAndBumpStep:
    """Boundary for checking and advancing game steps (1 -> 2 -> 3)"""

    def get_step(self) -> int:
        assert False

    def check_and_bump_to_step_2(self) -> None:
        assert False

    def check_and_bump_to_step_3(self) -> None:
        assert False


class InterfaceDeterminePlayerOrder:
    """Boundary for round player ordering and final game ranking"""

    def reorder(self) -> list[PlayerColor]:
        assert False

    def game_result(self) -> list[PlayerColor]:
        assert False
