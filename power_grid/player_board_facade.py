from collections.abc import Sequence

from power_grid.player_money import PlayerMoney
from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.player_resources import PlayerResources
from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


class PlayerBoardFacade:
    """Gives other classes access to the player's money, resources and power plants."""

    def __init__(self, money: PlayerMoney,
                 resources: PlayerResources | None = None,
                 power_plants: PlayerPowerPlants | None = None) -> None:
        self._money: PlayerMoney = money
        self._resources: PlayerResources = (
            resources if resources is not None else PlayerResources())
        self._power_plants: PlayerPowerPlants = (
            power_plants if power_plants is not None else PlayerPowerPlants())

    def outstanding_money(self) -> int:
        return self._money.current_money

    def has_enough_money(self, amount: int) -> bool:
        return self._money.has_enough_money(amount)

    def spend_money(self, amount: int) -> None:
        self._money.spend_money(amount)

    def receive_money(self, number_of_towns: int) -> None:
        self._money.receive_money(number_of_towns)

    def add_resources(self, resources: Sequence[Resource]) -> None:
        self._resources.add_resources(resources)

    def remove_resources(self, resources: Sequence[Resource]) -> None:
        """Raises ValueError (and changes nothing) if the player lacks the resources."""
        self._resources.remove_resources(resources)

    def get_resources(self) -> Sequence[Resource]:
        return self._resources.get_resources()

    def get_power_plants(self) -> Sequence[PowerPlant]:
        return self._power_plants.get_power_plants()

    def receive_power_plant(self, plant: PowerPlant, price: int) -> bool:
        """Pays `price` and takes the plant. False if the player cannot take it."""
        if not self._power_plants.can_add_power_plant():
            return False
        if not self._money.has_enough_money(price):
            return False
        self._money.spend_money(price)
        self._power_plants.add_power_plant(plant)
        return True

    def remove_power_plant(self, ppn: PowerPlantNumber,
                           removed_resources: Sequence[Resource]) -> RequestError | None:
        """Scraps a plant and the given resources. Changes nothing on error."""
        if all(plant.number != ppn for plant in self._power_plants.get_power_plants()):
            return RequestError(f"Power plant {ppn.number} is not owned")
        try:
            self._resources.remove_resources(removed_resources)
        except ValueError as error:
            return RequestError(str(error))
        return self._power_plants.remove_power_plant(ppn)