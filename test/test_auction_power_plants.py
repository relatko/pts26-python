"""Solitary unit tests of AuctionPowerPlants: the market and the boards are fakes."""
# pylint: disable=too-few-public-methods, too-many-public-methods, attribute-defined-outside-init
import json
import unittest
from typing import Optional, Sequence

from power_grid.auction_power_plants import AuctionPowerPlants
from power_grid.simple_types import (PhaseStatus, PlayerColor, PowerPlant, PowerPlantNumber,
                                     RequestError, Resource)

A, B, C = PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN
CONTINUES, ENDS = PhaseStatus.CONTINUES, PhaseStatus.PHASE_ENDS


def ppn(number: int) -> PowerPlantNumber:
    """Shortcut."""
    return PowerPlantNumber(number)


class FakeMarket:
    """Market with given minimal bids (plant number -> minimal bid)."""

    def __init__(self, min_prices: dict[int, int]) -> None:
        self.min_prices = dict(min_prices)
        self.taken: list[int] = []
        self.discount_removals = 0

    def can_take_power_plant(self, number: PowerPlantNumber, price: int) -> Optional[RequestError]:
        """Rejects unknown plants and too low bids."""
        if number.number not in self.min_prices:
            return RequestError("Not in market")
        if price < self.min_prices[number.number]:
            return RequestError("Bid too low")
        return None

    def minimum_bid(self, number: PowerPlantNumber) -> int:
        """Minimal bid of the plant."""
        return self.min_prices[number.number]

    def take_power_plant(self, number: PowerPlantNumber) -> PowerPlant:
        """Removes the plant from the market."""
        del self.min_prices[number.number]
        self.taken.append(number.number)
        return PowerPlant(number.number, Resource.COAL, 1, 1)

    def remove_discounted_power_plant(self) -> None:
        """Only counts the calls."""
        self.discount_removals += 1


class FakeBoard:
    """Player board with money and a limit of power plants."""

    def __init__(self, money: int, plants: Optional[list[int]] = None) -> None:
        self.money = money
        self.plants: list[int] = list(plants or [])

    def has_enough_money(self, amount: int) -> bool:
        """True if the player can pay."""
        return self.money >= amount

    def receive_power_plant(self, number: PowerPlantNumber, price: int) -> bool:
        """Pays and takes the plant; False when above the limit of 3."""
        self.money -= price
        self.plants.append(number.number)
        return len(self.plants) <= 3

    def remove_power_plant(
        self, number: PowerPlantNumber, removed_resources: Sequence[Resource] # pylint: disable=unused-argument
    ) -> Optional[RequestError]:
        """Scraps an owned plant."""
        if number.number not in self.plants:
            return RequestError("You do not own it")
        self.plants.remove(number.number)
        return None


class TestAuctionPowerPlants(unittest.TestCase):
    """Choosing, bidding, passing, scrapping and the end of the phase."""

    def make(self, players: list[PlayerColor], first_round: bool = False, money: int = 100,
             plants: Optional[dict[PlayerColor, list[int]]] = None) -> AuctionPowerPlants:
        """A started auction; self.market and self.boards are available for checks."""
        self.market = FakeMarket({3: 3, 4: 4, 5: 5, 6: 6, 7: 1})
        self.boards = {p: FakeBoard(money, (plants or {}).get(p, [])) for p in players}
        auction = AuctionPowerPlants(self.market, self.boards, first_round)
        auction.start_phase(players)
        return auction

    def test_requests_before_start_are_rejected(self) -> None:
        """The phase must be started first."""
        auction = AuctionPowerPlants(FakeMarket({3: 3}), {A: FakeBoard(10)})
        self.assertIsInstance(auction.select_power_plant_to_bid(A, ppn(3), 3), RequestError)

    def test_wrong_player_cannot_select(self) -> None:
        """Only the player on turn may choose a plant."""
        auction = self.make([A, B])
        self.assertIsInstance(auction.select_power_plant_to_bid(B, ppn(3), 3), RequestError)
        self.assertEqual(auction.current_player(), A)
        self.assertEqual(self.market.taken, [])

    def test_select_rejected_by_market(self) -> None:
        """Unknown plant and too low first bid are rejected."""
        auction = self.make([A, B])
        self.assertIsInstance(auction.select_power_plant_to_bid(A, ppn(99), 5), RequestError)
        self.assertIsInstance(auction.select_power_plant_to_bid(A, ppn(5), 4), RequestError)
        self.assertEqual(auction.current_player(), A)

    def test_select_without_money(self) -> None:
        """The first bid must be affordable."""
        auction = self.make([A, B], money=2)
        self.assertIsInstance(auction.select_power_plant_to_bid(A, ppn(3), 3), RequestError)
        self.assertEqual(auction.current_player(), A)

    def test_select_moves_turn_to_next_bidder(self) -> None:
        """After the first bid the next player decides."""
        auction = self.make([A, B, C])
        self.assertEqual(auction.select_power_plant_to_bid(A, ppn(3), 3), CONTINUES)
        self.assertEqual(auction.current_player(), B)

    def test_cannot_select_during_running_auction(self) -> None:
        """Only one auction at a time."""
        auction = self.make([A, B])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        self.assertIsInstance(auction.select_power_plant_to_bid(B, ppn(4), 4), RequestError)

    def test_pass_wins_for_starter_at_first_bid(self) -> None:
        """The starter wins when the other player passes and then the other chooses."""
        auction = self.make([A, B])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        self.assertEqual(auction.do_not_bid_for_current_power_plant(B), CONTINUES)
        self.assertEqual((self.boards[A].plants, self.boards[A].money), ([3], 97))
        self.assertEqual(self.market.taken, [3])
        self.assertEqual(auction.current_player(), B)

    def test_bidding_round_trip(self) -> None:
        """The winner pays the highest bid."""
        auction = self.make([A, B])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        self.assertEqual(auction.bid_for_current_power_plant(B, 4), CONTINUES)
        self.assertEqual(auction.bid_for_current_power_plant(A, 6), CONTINUES)
        self.assertEqual(auction.do_not_bid_for_current_power_plant(B), CONTINUES)
        self.assertEqual((self.boards[A].plants, self.boards[A].money), ([3], 94))
        self.assertEqual(self.boards[B].money, 100)

    def test_bid_must_be_higher_and_affordable(self) -> None:
        """An equal bid and a bid above the money are rejected."""
        auction = self.make([A, B], money=10)
        auction.select_power_plant_to_bid(A, ppn(3), 5)
        self.assertIsInstance(auction.bid_for_current_power_plant(B, 5), RequestError)
        self.assertIsInstance(auction.bid_for_current_power_plant(B, 11), RequestError)
        self.assertEqual(auction.current_player(), B)

    def test_bid_out_of_turn_rejected(self) -> None:
        """Bidding and passing are only possible on turn."""
        auction = self.make([A, B, C])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        self.assertIsInstance(auction.bid_for_current_power_plant(C, 10), RequestError)
        self.assertIsInstance(auction.do_not_bid_for_current_power_plant(A), RequestError)

    def test_passed_bidder_cannot_return(self) -> None:
        """A player who passed is skipped and cannot bid again."""
        auction = self.make([A, B, C])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        auction.do_not_bid_for_current_power_plant(B)
        auction.bid_for_current_power_plant(C, 4)
        auction.bid_for_current_power_plant(A, 5)
        self.assertEqual(auction.current_player(), C)
        self.assertIsInstance(auction.bid_for_current_power_plant(B, 20), RequestError)
        auction.do_not_bid_for_current_power_plant(C)
        self.assertEqual(self.boards[A].plants, [3])

    def test_starter_chooses_again_after_losing(self) -> None:
        """If somebody else wins, the starter may choose another plant."""
        auction = self.make([A, B, C])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        auction.bid_for_current_power_plant(B, 4)
        auction.do_not_bid_for_current_power_plant(C)
        auction.do_not_bid_for_current_power_plant(A)
        self.assertEqual(self.boards[B].plants, [3])
        self.assertEqual(auction.current_player(), A)

    def test_last_chooser_pays_the_minimum_bid(self) -> None:
        """Nobody can outbid him, so a higher first bid is not paid."""
        auction = self.make([A, B])
        auction.do_not_want_power_plant(A)
        self.assertEqual(auction.select_power_plant_to_bid(B, ppn(4), 10), ENDS)
        self.assertEqual((self.boards[B].plants, self.boards[B].money), ([4], 96))

    def test_cannot_pass_in_first_round(self) -> None:
        """Every player must buy a plant in the first round."""
        auction = self.make([A, B], first_round=True)
        self.assertIsInstance(auction.do_not_want_power_plant(A), RequestError)
        self.assertEqual(auction.current_player(), A)

    def test_pass_allowed_later_and_player_is_skipped(self) -> None:
        """After the first round a player may opt out and does not bid."""
        auction = self.make([A, B, C])
        self.assertEqual(auction.do_not_want_power_plant(A), CONTINUES)
        self.assertEqual(auction.current_player(), B)
        auction.select_power_plant_to_bid(B, ppn(3), 3)
        self.assertEqual(auction.current_player(), C)

    def test_fourth_plant_requires_removal(self) -> None:
        """A 4th plant must be followed by scrapping another plant."""
        auction = self.make([A, B], plants={A: [10, 11, 12]})
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        auction.do_not_bid_for_current_power_plant(B)
        self.assertEqual(auction.current_player(), A)
        self.assertIsInstance(auction.select_power_plant_to_bid(B, ppn(4), 4), RequestError)
        self.assertIsInstance(auction.remove_power_plant(B, ppn(10), []), RequestError)
        self.assertIsInstance(auction.remove_power_plant(A, ppn(3), []), RequestError)
        self.assertIsInstance(auction.remove_power_plant(A, ppn(99), []), RequestError)
        self.assertEqual(auction.remove_power_plant(A, ppn(10), [Resource.COAL]), CONTINUES)
        self.assertEqual(self.boards[A].plants, [11, 12, 3])
        self.assertEqual(auction.current_player(), B)

    def test_phase_ends_when_everybody_is_done(self) -> None:
        """The last request ends the phase, the unbought discounted plant is removed."""
        auction = self.make([A, B])
        self.assertEqual(auction.do_not_want_power_plant(A), CONTINUES)
        self.assertEqual(self.market.discount_removals, 0)
        self.assertEqual(auction.do_not_want_power_plant(B), ENDS)
        self.assertEqual(self.market.discount_removals, 1)
        self.assertFalse(auction.is_first_round)
        self.assertIsNone(auction.current_player())
        self.assertIsInstance(auction.select_power_plant_to_bid(A, ppn(3), 3), RequestError)

    def test_first_round_everybody_buys(self) -> None:
        """Both players buy; the phase ends and is no longer the first round."""
        auction = self.make([A, B], first_round=True)
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        auction.do_not_bid_for_current_power_plant(B)
        self.assertEqual(auction.select_power_plant_to_bid(B, ppn(4), 4), ENDS)
        self.assertFalse(auction.is_first_round)

    def test_start_phase_again_starts_a_new_round(self) -> None:
        """The same object can run the auction every round."""
        auction = self.make([A, B])
        auction.do_not_want_power_plant(A)
        auction.do_not_want_power_plant(B)
        auction.start_phase([B, A])
        self.assertEqual(auction.current_player(), B)

    def test_get_state_is_json(self) -> None:
        """The state describes the running auction."""
        auction = self.make([A, B])
        auction.select_power_plant_to_bid(A, ppn(3), 3)
        state = json.loads(auction.get_state())
        self.assertEqual(state["current_player"], "BLUE")
        self.assertEqual(state["auction"]["power_plant"], 3)
        self.assertEqual(state["auction"]["price"], 3)
        self.assertEqual(state["auction"]["highest_bidder"], "RED")


if __name__ == "__main__":
    unittest.main()
