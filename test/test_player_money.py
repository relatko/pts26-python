import unittest
from power_grid.player_money import PlayerMoney
from power_grid.simple_types import PlayerColor


class TestPlayerMoney(unittest.TestCase):
    def setUp(self) -> None:
        self.money: PlayerMoney = PlayerMoney(PlayerColor.RED)

    def test_initial_money(self) -> None:
        self.assertEqual(self.money.current_money, 50)

    def test_has_enough_money(self) -> None:
        self.assertTrue(self.money.has_enough_money(50))
        self.assertFalse(self.money.has_enough_money(51))

    def test_spend_money(self) -> None:
        self.money.spend_money(20)
        self.assertEqual(self.money.current_money, 30)

    def test_spend_too_much(self) -> None:
        with self.assertRaises(ValueError):
            self.money.spend_money(51)
        self.assertEqual(self.money.current_money, 50)

    def test_receive_money_no_towns(self) -> None:
        self.money.receive_money(0)
        self.assertEqual(self.money.current_money, 60)

    def test_receive_money_three_towns(self) -> None:
        self.money.receive_money(3)
        self.assertEqual(self.money.current_money, 94)

    def test_receive_money_more_than_max(self) -> None:
        self.money.receive_money(25)
        self.assertEqual(self.money.current_money, 200)


if __name__ == "__main__":
    unittest.main()