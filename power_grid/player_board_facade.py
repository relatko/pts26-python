from power_grid.player_money import PlayerMoney


class PlayerBoardFacade:
    def __init__(self, money: PlayerMoney) -> None:
        self._money: PlayerMoney = money

    def outstanding_money(self) -> int:
        return self._money.current_money

    def has_enough_money(self, amount: int) -> bool:
        return self._money.has_enough_money(amount)

    def spend_money(self, amount: int) -> None:
        self._money.spend_money(amount)

    def receive_money(self, number_of_towns: int) -> None:
        self._money.receive_money(number_of_towns)