from power_grid.simple_types import PlayerColor

INCOME_BY_TOWNS: tuple[int, ...] = (
    10, 22, 33, 44, 54, 64, 73, 82, 90, 98, 105,
    112, 118, 124, 129, 134, 138, 142, 145, 148, 150,
)


class PlayerMoney:
    def __init__(self, color: PlayerColor, current_money: int = 50) -> None:
        self.color: PlayerColor = color
        self.current_money: int = current_money

    def has_enough_money(self, amount: int) -> bool:
        return self.current_money >= amount

    def receive_money(self, number_of_towns: int) -> None:
        index = max(0, min(number_of_towns, len(INCOME_BY_TOWNS) - 1))
        self.current_money += INCOME_BY_TOWNS[index]

    def spend_money(self, amount: int) -> None:
        if not self.has_enough_money(amount):
            raise ValueError("Not enough money")
        self.current_money -= amount