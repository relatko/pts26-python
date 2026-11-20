
import unittest

from power_grid.player_money import PlayerMoney
from power_grid.simple_types import PlayerColor


class TestPlayerMoney(unittest.TestCase):

    def test_starting_money(self) -> None:
        player = PlayerMoney(PlayerColor.RED)
        self.assertEqual(player.current_money, 50)

    def test_receive_money(self) -> None:
        player = PlayerMoney(PlayerColor.BLUE)
        player.receive_money(20)
        self.assertEqual(player.current_money, 70)

    def test_spend_money(self) -> None:
        player = PlayerMoney(PlayerColor.GREEN)
        player.spend_money(30)
        self.assertEqual(player.current_money, 20)

    def test_enough_money(self) -> None:
        player = PlayerMoney(PlayerColor.RED)

        self.assertTrue(player.has_enough_money(40))
        self.assertFalse(player.has_enough_money(60))

    def test_not_enough_money(self) -> None:
        player = PlayerMoney(PlayerColor.YELLOW)
        player.spend_money(100)

        self.assertEqual(player.current_money, 50)

    def test_negative_money(self) -> None:
        player = PlayerMoney(PlayerColor.BLUE)

        player.receive_money(-10)
        player.spend_money(-20)

        self.assertEqual(player.current_money, 50)
        self.assertFalse(player.has_enough_money(-5))
