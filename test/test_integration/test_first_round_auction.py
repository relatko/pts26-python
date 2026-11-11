"""Integration test: GameController + AuctionPowerPlants + PowerPlantMarket (first round)."""
# pylint: disable=too-few-public-methods
import unittest
from typing import Sequence
from unittest.mock import MagicMock

from power_grid.auction_power_plants import AuctionPowerPlants
from power_grid.game_controller import GameController
from power_grid.power_plant_market import PowerPlantMarket
from power_grid.simple_types import (GamePhase, PlayerColor, PowerPlant, PowerPlantNumber,
                                     RequestError, Resource)

RED, BLUE, GREEN = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN


def plants(*numbers: int) -> list[PowerPlant]:
    """Plants with the given numbers."""
    return [PowerPlant(n, Resource.COAL, 1, 1) for n in numbers]


def ppn(number: int) -> PowerPlantNumber:
    """Shortcut."""
    return PowerPlantNumber(number)


class SimpleBoard:
    """In-memory player board (replace with PlayerBoardFacade when its constructor is known)."""

    def __init__(self, money: int) -> None:
        self.money = money
        self.plants: list[int] = []

    def has_enough_money(self, amount: int) -> bool:
        """True if the player can pay."""
        return self.money >= amount

    def receive_power_plant(self, number: PowerPlantNumber, price: int) -> bool:
        """Pays and takes the plant."""
        self.money -= price
        self.plants.append(number.number)
        return len(self.plants) <= 3

    def remove_power_plant(
        self, number: PowerPlantNumber, removed_resources: Sequence[Resource]
    ) -> None:
        """Scraps a plant."""
        del removed_resources  # not needed by this simple board
        self.plants.remove(number.number)


class FixedOrder:
    """DeterminePlayerOrder that returns a given order."""

    def __init__(self, order: list[PlayerColor]) -> None:
        self.order = order
        self.calls = 0

    def reorder(self) -> list[PlayerColor]:
        """The new order."""
        self.calls += 1
        return list(self.order)

    def game_result(self) -> list[PlayerColor]:
        """Not needed here."""
        return []


class TestFirstRoundAuction(unittest.TestCase):
    """A whole first auction played through the GameController."""

    def test_three_players_buy_one_plant_each(self) -> None:
        """Bidding, passing, the discount, the last player and the move to buying resources."""
        market = PowerPlantMarket(plants(3, 4, 5, 6), plants(7, 8, 9, 10), plants(11, 12),
                                  plants(13), lambda cards: None)
        boards = {color: SimpleBoard(50) for color in (RED, BLUE, GREEN)}
        auction = AuctionPowerPlants(market, boards)
        order = FixedOrder([GREEN, RED, BLUE])
        buying = MagicMock()
        game = GameController([RED, BLUE, GREEN], order, auction, buying, MagicMock(),
                              MagicMock())

        # RED offers the discounted plant 3 for 1, BLUE outbids, BLUE wins for 2
        self.assertIsNone(game.select_power_plant_to_bid(RED, ppn(3), 1))
        self.assertIsNone(game.bid_for_current_power_plant(BLUE, 2))
        self.assertIsNone(game.do_not_bid_for_current_power_plant(GREEN))
        self.assertIsNone(game.do_not_bid_for_current_power_plant(RED))
        self.assertEqual((boards[BLUE].plants, boards[BLUE].money), ([3], 48))
        # in the first round nobody may skip
        self.assertIsInstance(game.do_not_want_power_plant(RED), RequestError)
        # RED offers 5, GREEN passes, RED pays 5
        self.assertIsNone(game.select_power_plant_to_bid(RED, ppn(5), 5))
        self.assertIsNone(game.do_not_bid_for_current_power_plant(GREEN))
        self.assertEqual((boards[RED].plants, boards[RED].money), ([5], 45))
        self.assertEqual(game.game_phase, GamePhase.AUCTION)
        # GREEN is the last one: offers plant 4 for 9 but pays the minimum, 4
        self.assertIsNone(game.select_power_plant_to_bid(GREEN, ppn(4), 9))
        self.assertEqual((boards[GREEN].plants, boards[GREEN].money), ([4], 46))

        # the auction is over: new order, buying starts in reverse order
        self.assertEqual(game.game_phase, GamePhase.BUY_RESOURCES)
        self.assertEqual(order.calls, 1)
        buying.start_phase.assert_called_once_with([BLUE, RED, GREEN])
        self.assertIsInstance(game.select_power_plant_to_bid(RED, ppn(6), 6), RequestError)
        # the market was refilled after every purchase
        self.assertEqual([p.number for p in market.current_market], [6, 7, 8, 9])
        self.assertEqual([p.number for p in market.future_market], [10, 11, 12])
        # the third purchase drew the Step 3 card (the deck above it was empty)
        self.assertTrue(market.is_step3_start())


if __name__ == "__main__":
    unittest.main()
