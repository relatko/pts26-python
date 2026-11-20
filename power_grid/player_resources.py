from power_grid.simple_types import Resource, RequestError
from power_grid.power_plant import PowerPlant, PowerPlantNumber
from power_grid.store_resources import StoreResources
from power_grid.resource_market import ResourceMarket
from power_grid.player_money import PlayerMoney
from typing import Optional


class PlayerRescources:
    def __init__(self, # pylint: disable=too-many-arguments
                 resources: list[Resource],
                 power_plants: list[PowerPlant],
                 store: StoreResources,
                 market: ResourceMarket,
                 money: PlayerMoney) -> None:
        self._resources = list(resources)
        self._power_plants = power_plants
        self._store = store
        self._market = market
        self._money = money

    def removePowerPlant(self,ppn: PowerPlantNumber, removedResources: list[Resource])-> Optional[RequestError]:
        power_plants = self._power_plants.copy()

        #Finds correct power plant
        for plant in power_plants:
            if ppn.number == plant.number.number:
                found = plant
                power_plants.remove(plant)
                break
        else:
            return RequestError("player does not own this power plant")

        rescources = self._resources.copy()

        #removes rescources
        for r in removedResources:
            try:
                rescources.remove(r)
            except ValueError:
                return RequestError("player does not have these resources")

        #can store
        if not self._store.can_store_resources(rescources, power_plants):
            return RequestError("remaining resources do not fit on power plants")

        self._resources = rescources
        self._power_plants.remove(found)
        return None

    def numberOfConnectableCities(self) -> int:
        result = 0

        for plant in self._power_plants:
            result += plant.number_of_cities
        return result


    def buyResources(self,resources: list[Resource]) -> Optional[RequestError]:
        #if there's not enough space in power plants

        if not self._store.can_store_resources(self._resources + resources, self._power_plants):
            return RequestError("not enough space on power plants")

        price = self._market.get_price(resources)

        if price is None:
            return RequestError("market can't supply resources")


        if not self._money.has_enough_money(price):
            return RequestError("player doesn't have enough money")

        self._market.take_resources(resources)
        self._money.spend_money(price)
        self._resources += resources
        return None

    def usePowerPlant(self, ppns: list[PowerPlantNumber],
                      resourcesToBurn: list[Resource]) -> int | RequestError:

        #each power plant can be used only once
        numbers = [ppn.number for ppn in ppns]
        if len(numbers) != len(set(numbers)):
            return RequestError("power plant used more than once")

        #finds the chosen power plants
        chosen: list[PowerPlant] = []
        for ppn in ppns:
            for plant in self._power_plants:
                if ppn.number == plant.number.number:
                    chosen.append(plant)
                    break
            else:
                return RequestError("player does not own this power plant")

        #player must have all the resources he wants to burn
        resources = self._resources.copy()
        for r in resourcesToBurn:
            try:
                resources.remove(r)
            except ValueError:
                return RequestError("player does not have these resources")

        #resources must match what the power plants need
        if not self._canBurn(chosen, resourcesToBurn):
            return RequestError("resources do not match power plants")

        self._resources = resources
        return sum(plant.number_of_cities for plant in chosen)

    def _canBurn(self, plants: list[PowerPlant], resourcesToBurn: list[Resource]) -> bool:
        needed = sum(plant.resource_amount for plant in plants)
        if len(resourcesToBurn) != needed:
            return False

        remaining = resourcesToBurn.copy()

        #power plants with one type of resource first
        for plant in plants:
            if len(plant.accepted_resources) == 1:
                resource_type = plant.accepted_resources[0]
                for _ in range(plant.resource_amount):
                    if resource_type not in remaining:
                        return False
                    remaining.remove(resource_type)

        #hybrid power plants
        for plant in plants:
            if len(plant.accepted_resources) > 1:
                for _ in range(plant.resource_amount):
                    for resource_type in plant.accepted_resources:
                        if resource_type in remaining:
                            remaining.remove(resource_type)
                            break
                    else:
                        return False
        return len(remaining) == 0
