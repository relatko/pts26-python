"""AuctionPowerPlants: phase 2 (auction of power plants) of a round."""
import json
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence, Union

from power_grid.auction_interfaces import (
    InterfacePlayerBoardFacadeAuctionPowerPlants,
    InterfacePowerPlantMarketAuctionPowerPlants,
)
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlantNumber, RequestError, Resource)

Result = Union[PhaseStatus, RequestError]


@dataclass
class _Auction:
    ppn: PowerPlantNumber
    price: int
    highest: PlayerColor
    active: list[PlayerColor]  # still bidding, in player order
    current: PlayerColor  # whose bid or pass it is

    def next_after(self, player: PlayerColor) -> PlayerColor:
        return self.active[(self.active.index(player) + 1) % len(self.active)]


class AuctionPowerPlants:  # pylint: disable=too-many-instance-attributes
    """Players choose a plant in turn and the others bid for it.

    Every request returns PhaseStatus (PHASE_ENDS when everybody is done) or a RequestError.
    A request is validated completely before anything is changed.
    """

    def __init__(
        self,
        market: InterfacePowerPlantMarketAuctionPowerPlants,
        boards: Mapping[PlayerColor, InterfacePlayerBoardFacadeAuctionPowerPlants],
        is_first_round: bool = True,
    ) -> None:
        self.is_first_round = is_first_round
        self._market = market
        self._boards = boards
        self._order: list[PlayerColor] = []
        self._running = False
        self._finished: set[PlayerColor] = set()  # bought a plant or do not want one
        self._auction: Optional[_Auction] = None
        self._pending_removal: Optional[PlayerColor] = None
        self._last_bought: Optional[PowerPlantNumber] = None

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Starts the phase; players choose in the given order."""
        self._order = list(player_order)
        self._running = True
        self._finished = set()
        self._auction = None
        self._pending_removal = None
        self._last_bought = None

    def current_player(self) -> Optional[PlayerColor]:
        """Player who has to act now; None if the phase is not running."""
        if not self._running:
            return None
        if self._pending_removal is not None:
            return self._pending_removal
        if self._auction is not None:
            return self._auction.current
        return self._chooser()

    def select_power_plant_to_bid(
        self, player: PlayerColor, ppn: PowerPlantNumber, first_bid: int
    ) -> Result:
        """The player on turn offers a plant with the first bid."""
        if (err := self._check_choosing(player)) is not None:
            return err
        if (err := self._market.can_take_power_plant(ppn, first_bid)) is not None:
            return err
        if not self._boards[player].has_enough_money(first_bid):
            return RequestError("Not enough money")
        active = [p for p in self._order if p not in self._finished]
        if len(active) == 1:  # nobody can outbid the last player: he pays the minimum
            self._auction = _Auction(ppn, self._market.minimum_bid(ppn), player, active, player)
            return self._finish_auction()
        self._auction = _Auction(ppn, first_bid, player, active, player)
        self._auction.current = self._auction.next_after(player)
        return PhaseStatus.CONTINUES

    def do_not_want_power_plant(self, player: PlayerColor) -> Result:
        """The player on turn buys no plant in this round (not allowed in the first round)."""
        if (err := self._check_choosing(player)) is not None:
            return err
        if self.is_first_round:
            return RequestError("In the first round every player must buy a power plant")
        self._finished.add(player)
        return self._advance()

    def bid_for_current_power_plant(self, player: PlayerColor, bid: int) -> Result:
        """The player on turn raises the bid."""
        if (err := self._check_bidding(player)) is not None:
            return err
        auction = self._auction
        assert auction is not None
        if bid <= auction.price:
            return RequestError("Bid must be higher than the current bid")
        if not self._boards[player].has_enough_money(bid):
            return RequestError("Not enough money")
        auction.price = bid
        auction.highest = player
        auction.current = auction.next_after(player)
        return PhaseStatus.CONTINUES

    def do_not_bid_for_current_power_plant(self, player: PlayerColor) -> Result:
        """The player on turn leaves the auction of the current plant."""
        if (err := self._check_bidding(player)) is not None:
            return err
        auction = self._auction
        assert auction is not None
        following = auction.next_after(player)
        auction.active.remove(player)
        if len(auction.active) == 1:
            return self._finish_auction()
        auction.current = following
        return PhaseStatus.CONTINUES

    def remove_power_plant(
        self, player: PlayerColor, ppn: PowerPlantNumber, resources: Sequence[Resource]
    ) -> Result:
        """The winner above the plant limit scraps a plant (not the one just bought)."""
        if not self._running:
            return RequestError("The auction is not running")
        if self._pending_removal != player:
            return RequestError("You do not have to remove a power plant")
        if ppn == self._last_bought:
            return RequestError("You cannot scrap the power plant you have just bought")
        if (err := self._boards[player].remove_power_plant(ppn, resources)) is not None:
            return err
        self._pending_removal = None
        return self._advance()

    def get_state(self) -> str:
        """The state of the auction as a JSON string."""
        auction = None
        if self._auction is not None:
            auction = {
                "power_plant": self._auction.ppn.number,
                "price": self._auction.price,
                "highest_bidder": self._auction.highest.name,
                "bidders": [p.name for p in self._auction.active],
            }
        current = self.current_player()
        return json.dumps({
            "phase": "auction",
            "running": self._running,
            "first_round": self.is_first_round,
            "current_player": None if current is None else current.name,
            "players_done": [p.name for p in self._order if p in self._finished],
            "auction": auction,
        })

    # ---------- internals ----------
    def _chooser(self) -> Optional[PlayerColor]:
        return next((p for p in self._order if p not in self._finished), None)

    def _check_choosing(self, player: PlayerColor) -> Optional[RequestError]:
        if not self._running:
            return RequestError("The auction is not running")
        if self._pending_removal is not None:
            return RequestError("Waiting for a power plant to be removed")
        if self._auction is not None:
            return RequestError("An auction is in progress")
        if player != self._chooser():
            return RequestError("Not your turn")
        return None

    def _check_bidding(self, player: PlayerColor) -> Optional[RequestError]:
        if not self._running:
            return RequestError("The auction is not running")
        if self._auction is None:
            return RequestError("No auction in progress")
        if player != self._auction.current:
            return RequestError("Not your turn to bid")
        return None

    def _finish_auction(self) -> Result:
        auction = self._auction
        assert auction is not None
        winner = auction.highest
        self._market.take_power_plant(auction.ppn)
        within_limit = self._boards[winner].receive_power_plant(auction.ppn, auction.price)
        self._auction = None
        self._finished.add(winner)
        self._last_bought = auction.ppn
        if not within_limit:
            self._pending_removal = winner
            return PhaseStatus.CONTINUES
        return self._advance()

    def _advance(self) -> Result:
        if len(self._finished) < len(self._order):
            return PhaseStatus.CONTINUES
        self._market.remove_discounted_power_plant()
        self._running = False
        self._last_bought = None
        self.is_first_round = False
        return PhaseStatus.PHASE_ENDS
