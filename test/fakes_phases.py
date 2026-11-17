# pylint: disable=unused-argument
"""Fakes shared by the tests of BuyingResources, BuildingHouses, Bureaucracy."""
from collections.abc import Sequence

from power_grid.simple_types import (
    PlayerColor,
    PowerPlant,
    PowerPlantNumber,
    RequestError,
    Resource,
)

BLUE = PlayerColor.BLUE
RED = PlayerColor.RED
COAL_PLANT = PowerPlant(
    number=PowerPlantNumber(5),
    acceptedResources=[Resource.COAL],
    numberOfCities=2,
    resourceAmount=2
)
ECO_PLANT = PowerPlant(
    number=PowerPlantNumber(13),
    acceptedResources=[],
    numberOfCities=1
)


class FakeBoard:
    """Player board that records everything done to it."""

    def __init__(self, money: int = 50, resources: Sequence[Resource] = (),
                 plants: Sequence[PowerPlant] = ()) -> None:
        self.money = money
        self.resources = list(resources)
        self.plants = list(plants)
        self.income_towns: list[int] = []

    def outstanding_money(self) -> int:
        return self.money

    def spend_money(self, amount: int) -> None:
        self.money -= amount

    def receive_money(self, number_of_towns: int) -> None:
        self.income_towns.append(number_of_towns)

    def add_resources(self, resources: Sequence[Resource]) -> None:
        self.resources.extend(resources)

    def remove_resources(self, resources: Sequence[Resource]) -> None:
        for resource in resources:
            self.resources.remove(resource)

    def get_resources(self) -> Sequence[Resource]:
        return list(self.resources)

    def get_power_plants(self) -> Sequence[PowerPlant]:
        return list(self.plants)


class FakePool:
    """Resource pool with a fixed price."""

    def __init__(self, price: int | None = 3) -> None:
        self.price_value = price
        self.bought: list[Resource] = []
        self.refills: list[tuple[int, int]] = []

    def price(self, resources: Sequence[Resource]) -> int | None:
        return self.price_value

    def buy(self, resources: Sequence[Resource]) -> None:
        self.bought.extend(resources)

    def refill(self, step: int, number_of_players: int) -> None:
        self.refills.append((step, number_of_players))


class FakeTowns:
    """Towns with a fixed building cost."""

    def __init__(self) -> None:
        self.cost: int | RequestError = 10
        self.max = 0
        self.counts: dict[PlayerColor, int] = {RED: 3, BLUE: 3}
        self.step2_started = 0

    def buy_houses(self, player: PlayerColor, town_names: Sequence[str],
                   max_money: int) -> int | RequestError:
        return self.cost

    def number_of_towns(self, player: PlayerColor) -> int:
        return self.counts[player]

    def get_max_number_of_houses(self) -> int:
        return self.max

    def start_step2(self) -> None:
        self.step2_started += 1


class FakeMarket:
    """Power plant market that counts calls."""

    def __init__(self) -> None:
        self.removed_below: list[int] = []
        self.step3_started = 0
        self.prepared = 0

    def remove_power_plants_cheaper_than(self, value: int) -> None:
        self.removed_below.append(value)

    def start_step3(self) -> None:
        self.step3_started += 1

    def prepare_next_turn(self) -> None:
        self.prepared += 1
