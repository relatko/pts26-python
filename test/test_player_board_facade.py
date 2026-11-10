import unittest
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.player_money import PlayerMoney
from power_grid.simple_types import PlayerColor


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


if __name__ == "__main__":
    unittest.main()