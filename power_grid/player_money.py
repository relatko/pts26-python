
from power_grid.simple_types import PlayerColor


class PlayerMoney:
    # initialize player money, color
    def __init__(self, color: PlayerColor, money: int = 50) -> None:
        self.color = color

        if money >= 0:
            self.current_money = money
        else:
            self.current_money = 0

    # Check if player has enough money
    def has_enough_money(self, amount: int) -> bool:
        if amount < 0:
            return False

        if self.current_money >= amount:
            return True
        else:
            return False

    # Add money to player
    def receive_money(self, amount: int) -> None:
        if amount >= 0:
            self.current_money = self.current_money + amount

    # Remove money from player
    def spend_money(self, amount: int) -> None:
        if amount >= 0:
            if self.has_enough_money(amount):
                self.current_money = self.current_money - amount
