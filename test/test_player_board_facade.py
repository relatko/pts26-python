import unittest

from power_grid.phase_dependencies import PlayerBoardForPhases
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.player_money import PlayerMoney
from power_grid.simple_types import (
    PlayerColor,
    PowerPlant,
    PowerPlantNumber,
    RequestError,
    Resource,
)


def make_plant(number: int) -> PowerPlant:
    return PowerPlant(PowerPlantNumber(number), [Resource.COAL], 1, 2)


class TestPlayerBoardFacade(unittest.TestCase):
    def setUp(self) -> None:
        self.facade: PlayerBoardFacade = PlayerBoardFacade(
            PlayerMoney(PlayerColor.BLUE, 30))

    def test_outstanding_money(self) -> None:
        self.assertEqual(self.facade.outstanding_money(), 30)

    def test_has_enough_money(self) -> None:
        self.assertTrue(self.facade.has_enough_money(30))
        self.assertFalse(self.facade.has_enough_money(31))

    def test_spend_money(self) -> None:
        self.facade.spend_money(10)
        self.assertEqual(self.facade.outstanding_money(), 20)

    def test_spend_too_much(self) -> None:
        with self.assertRaises(ValueError):
            self.facade.spend_money(31)

    def test_receive_money(self) -> None:
        self.facade.receive_money(1)
        self.assertEqual(self.facade.outstanding_money(), 52)

    def test_fits_phases_interface(self) -> None:
        board: PlayerBoardForPhases = self.facade
        self.assertEqual(board.outstanding_money(), 30)

    def test_add_and_get_resources(self) -> None:
        self.facade.add_resources([Resource.COAL, Resource.OIL, Resource.COAL])
        self.assertCountEqual(
            self.facade.get_resources(),
            [Resource.COAL, Resource.OIL, Resource.COAL])

    def test_remove_resources(self) -> None:
        self.facade.add_resources([Resource.COAL, Resource.COAL])
        self.facade.remove_resources([Resource.COAL])
        self.assertEqual(list(self.facade.get_resources()), [Resource.COAL])

    def test_remove_too_many_resources(self) -> None:
        self.facade.add_resources([Resource.COAL])
        with self.assertRaises(ValueError):
            self.facade.remove_resources([Resource.COAL, Resource.COAL])
        self.assertEqual(list(self.facade.get_resources()), [Resource.COAL])

    def test_receive_power_plant(self) -> None:
        plant = make_plant(5)
        self.assertTrue(self.facade.receive_power_plant(plant, 10))
        self.assertEqual(self.facade.outstanding_money(), 20)
        self.assertEqual(list(self.facade.get_power_plants()), [plant])

    def test_receive_power_plant_not_enough_money(self) -> None:
        self.assertFalse(self.facade.receive_power_plant(make_plant(5), 31))
        self.assertEqual(self.facade.outstanding_money(), 30)
        self.assertEqual(list(self.facade.get_power_plants()), [])

    def test_receive_power_plant_over_limit(self) -> None:
        for number in (3, 4, 5):
            self.assertTrue(self.facade.receive_power_plant(make_plant(number), 1))
        self.assertFalse(self.facade.receive_power_plant(make_plant(6), 1))
        self.assertEqual(self.facade.outstanding_money(), 27)
        self.assertEqual(len(self.facade.get_power_plants()), 3)

    def test_remove_power_plant(self) -> None:
        self.facade.receive_power_plant(make_plant(5), 10)
        self.facade.add_resources([Resource.COAL, Resource.COAL])
        result = self.facade.remove_power_plant(
            PowerPlantNumber(5), [Resource.COAL])
        self.assertIsNone(result)
        self.assertEqual(list(self.facade.get_power_plants()), [])
        self.assertEqual(list(self.facade.get_resources()), [Resource.COAL])

    def test_remove_power_plant_not_owned(self) -> None:
        self.facade.add_resources([Resource.COAL])
        result = self.facade.remove_power_plant(
            PowerPlantNumber(5), [Resource.COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(list(self.facade.get_resources()), [Resource.COAL])

    def test_remove_power_plant_missing_resources(self) -> None:
        plant = make_plant(5)
        self.facade.receive_power_plant(plant, 10)
        result = self.facade.remove_power_plant(
            PowerPlantNumber(5), [Resource.COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(list(self.facade.get_power_plants()), [plant])


if __name__ == "__main__":
    unittest.main()