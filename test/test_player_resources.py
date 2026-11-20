# pylint: disable=protected-access
import json
import unittest
from typing import Sequence

from power_grid.simple_types import Resource, PlayerColor, RequestError
from power_grid.power_plant import PowerPlant, PowerPlantNumber
from power_grid.store_resources import StoreResources
from power_grid.resource_market import ResourceMarket
from power_grid.player_money import PlayerMoney
from power_grid.interfaces import InterfaceResourcePoolResourceMarket
from power_grid.player_resources import PlayerRescources


class ResourcePoolFake(InterfaceResourcePoolResourceMarket):

    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        return False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        return []

    def to_string(self) -> str:
        return json.dumps("FakePool")


class TestPlayerResources(unittest.TestCase):

    def setUp(self) -> None:
        # coal plant: burns 2 coal, stores up to 4 coal, powers 2 cities
        self.coal_plant = PowerPlant(PowerPlantNumber(10), [Resource.COAL], 2, 2)
        # hybrid plant: burns 2 coal/oil, stores up to 4, powers 3 cities
        self.hybrid_plant = PowerPlant(
            PowerPlantNumber(13), [Resource.COAL, Resource.OIL], 2, 3)
        # wind plant: burns nothing, powers 1 city
        self.wind_plant = PowerPlant(PowerPlantNumber(18), [], 0, 1)

        self.plants = [self.coal_plant, self.hybrid_plant, self.wind_plant]
        self.money = PlayerMoney(PlayerColor.RED, 50)

        refilling_pattern = {step: {resource: 0 for resource in Resource}
                             for step in (1, 2, 3)}
        # market: 24 coal and 24 oil, cheapest coal/oil cost 1
        self.market = ResourceMarket(
            ResourcePoolFake(),
            24 * [Resource.COAL] + 24 * [Resource.OIL],
            refilling_pattern)

    def make_player(self, resources: list[Resource]) -> PlayerRescources:
        return PlayerRescources(resources, self.plants, StoreResources(),
                                self.market, self.money)

    # ---------- numberOfConnectableCities ----------

    def test_connectable_cities(self) -> None:
        player = self.make_player([])

        self.assertEqual(player.numberOfConnectableCities(), 6)

    def test_connectable_cities_no_power_plants(self) -> None:
        self.plants = []
        player = self.make_player([])

        self.assertEqual(player.numberOfConnectableCities(), 0)

    # ---------- buyResources ----------

    def test_buy_resources(self) -> None:
        player = self.make_player([])

        result = player.buyResources([Resource.COAL, Resource.COAL])

        self.assertIsNone(result)
        self.assertEqual(player._resources, [Resource.COAL, Resource.COAL])
        self.assertEqual(self.money.current_money, 48)
        self.assertEqual(self.market._resources[Resource.COAL], 22)

    def test_buy_resources_adds_to_existing(self) -> None:
        player = self.make_player([Resource.OIL])

        result = player.buyResources([Resource.COAL])

        self.assertIsNone(result)
        self.assertEqual(player._resources, [Resource.OIL, Resource.COAL])

    def test_buy_resources_fills_storage_exactly(self) -> None:
        # coal plant + hybrid plant can store 8 coal together
        player = self.make_player(4 * [Resource.COAL])

        result = player.buyResources(4 * [Resource.COAL])

        self.assertIsNone(result)
        self.assertEqual(len(player._resources), 8)

    def test_buy_resources_not_enough_space(self) -> None:
        player = self.make_player(8 * [Resource.COAL])

        result = player.buyResources([Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 8)
        self.assertEqual(self.money.current_money, 50)
        self.assertEqual(self.market._resources[Resource.COAL], 24)

    def test_buy_resources_wrong_type(self) -> None:
        player = self.make_player([])

        result = player.buyResources([Resource.URANIUM])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, [])
        self.assertEqual(self.money.current_money, 50)

    def test_buy_resources_market_cannot_supply(self) -> None:
        self.market = ResourceMarket(
            ResourcePoolFake(), [Resource.COAL],
            {step: {resource: 0 for resource in Resource} for step in (1, 2, 3)})
        player = self.make_player([])

        result = player.buyResources([Resource.COAL, Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, [])
        self.assertEqual(self.money.current_money, 50)
        self.assertEqual(self.market._resources[Resource.COAL], 1)

    def test_buy_resources_not_enough_money(self) -> None:
        self.money = PlayerMoney(PlayerColor.RED, 2)
        player = self.make_player([])

        result = player.buyResources(3 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, [])
        self.assertEqual(self.money.current_money, 2)
        self.assertEqual(self.market._resources[Resource.COAL], 24)

    def test_buy_resources_exactly_enough_money(self) -> None:
        self.money = PlayerMoney(PlayerColor.RED, 3)
        player = self.make_player([])

        result = player.buyResources(3 * [Resource.COAL])

        self.assertIsNone(result)
        self.assertEqual(self.money.current_money, 0)

    # ---------- removePowerPlant ----------

    def test_remove_power_plant(self) -> None:
        player = self.make_player([Resource.OIL])

        result = player.removePowerPlant(PowerPlantNumber(10), [])

        self.assertIsNone(result)
        self.assertNotIn(self.coal_plant, player._power_plants)
        self.assertEqual(len(player._power_plants), 2)
        self.assertEqual(player._resources, [Resource.OIL])

    def test_remove_power_plant_with_discarded_resources(self) -> None:
        # 8 coal fill both plants, after removing coal plant only 4 fit
        player = self.make_player(8 * [Resource.COAL])

        result = player.removePowerPlant(PowerPlantNumber(10), 4 * [Resource.COAL])

        self.assertIsNone(result)
        self.assertEqual(player._resources, 4 * [Resource.COAL])
        self.assertNotIn(self.coal_plant, player._power_plants)

    def test_remove_power_plant_not_owned(self) -> None:
        player = self.make_player([])

        result = player.removePowerPlant(PowerPlantNumber(99), [])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._power_plants), 3)

    def test_remove_power_plant_resources_not_owned(self) -> None:
        player = self.make_player([Resource.COAL])

        result = player.removePowerPlant(PowerPlantNumber(10), [Resource.OIL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, [Resource.COAL])
        self.assertEqual(len(player._power_plants), 3)

    def test_remove_power_plant_not_enough_discarded(self) -> None:
        player = self.make_player(8 * [Resource.COAL])

        result = player.removePowerPlant(PowerPlantNumber(10), 2 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 8)
        self.assertEqual(len(player._power_plants), 3)

    # ---------- usePowerPlant ----------

    def test_use_power_plant(self) -> None:
        player = self.make_player([Resource.COAL, Resource.COAL, Resource.OIL])

        result = player.usePowerPlant([PowerPlantNumber(10)],
                                      [Resource.COAL, Resource.COAL])

        self.assertEqual(result, 2)
        self.assertEqual(player._resources, [Resource.OIL])

    def test_use_hybrid_power_plant_mixed(self) -> None:
        player = self.make_player([Resource.COAL, Resource.OIL])

        result = player.usePowerPlant([PowerPlantNumber(13)],
                                      [Resource.OIL, Resource.COAL])

        self.assertEqual(result, 3)
        self.assertEqual(player._resources, [])

    def test_use_wind_power_plant(self) -> None:
        player = self.make_player([])

        result = player.usePowerPlant([PowerPlantNumber(18)], [])

        self.assertEqual(result, 1)

    def test_use_multiple_power_plants(self) -> None:
        player = self.make_player(3 * [Resource.COAL] + [Resource.OIL])

        result = player.usePowerPlant(
            [PowerPlantNumber(10), PowerPlantNumber(13), PowerPlantNumber(18)],
            [Resource.OIL, Resource.COAL, Resource.COAL, Resource.COAL])

        self.assertEqual(result, 6)
        self.assertEqual(player._resources, [])

    def test_use_no_power_plants(self) -> None:
        player = self.make_player([Resource.COAL])

        result = player.usePowerPlant([], [])

        self.assertEqual(result, 0)
        self.assertEqual(player._resources, [Resource.COAL])

    def test_use_power_plant_twice(self) -> None:
        player = self.make_player(4 * [Resource.COAL])

        result = player.usePowerPlant([PowerPlantNumber(10), PowerPlantNumber(10)],
                                      4 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 4)

    def test_use_power_plant_not_owned(self) -> None:
        player = self.make_player(2 * [Resource.COAL])

        result = player.usePowerPlant([PowerPlantNumber(99)], 2 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 2)

    def test_use_power_plant_resources_not_owned(self) -> None:
        player = self.make_player([Resource.COAL])

        result = player.usePowerPlant([PowerPlantNumber(10)], 2 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, [Resource.COAL])

    def test_use_power_plant_too_few_resources(self) -> None:
        player = self.make_player(2 * [Resource.COAL])

        result = player.usePowerPlant([PowerPlantNumber(10)], [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 2)

    def test_use_power_plant_too_many_resources(self) -> None:
        player = self.make_player(3 * [Resource.COAL])

        result = player.usePowerPlant([PowerPlantNumber(10)], 3 * [Resource.COAL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 3)

    def test_use_power_plant_wrong_resource(self) -> None:
        player = self.make_player(2 * [Resource.OIL])

        result = player.usePowerPlant([PowerPlantNumber(10)], 2 * [Resource.OIL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(player._resources, 2 * [Resource.OIL])

    def test_use_power_plant_resources_cannot_be_split(self) -> None:
        # hybrid could take oil, but coal plant gets no coal
        player = self.make_player(4 * [Resource.OIL])

        result = player.usePowerPlant([PowerPlantNumber(10), PowerPlantNumber(13)],
                                      4 * [Resource.OIL])

        self.assertIsInstance(result, RequestError)
        self.assertEqual(len(player._resources), 4)

    def test_use_power_plant_does_not_change_argument(self) -> None:
        player = self.make_player(2 * [Resource.COAL])
        to_burn = 2 * [Resource.COAL]

        player.usePowerPlant([PowerPlantNumber(10)], to_burn)

        self.assertEqual(to_burn, 2 * [Resource.COAL])


if __name__ == "__main__":
    unittest.main()
