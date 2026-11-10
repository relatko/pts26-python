"""GameController: switches the game phases and forwards player requests to them."""
from typing import Optional, Sequence, Union

from power_grid.phase_interfaces import (
    InterfaceAuctionPowerPlantsGameController,
    InterfaceBuildingHousesGameController,
    InterfaceBureaucracyGameController,
    InterfaceBuyingResourcesGameController,
    InterfaceDeterminePlayerOrderGameController,
)
from power_grid.simple_types import (
    GamePhase, PhaseStatus, PlayerColor, PowerPlantNumber, RequestError, Resource)


class GameController: # pylint: disable=too-many-instance-attributes
    """All public requests return None on success or a RequestError.

    A request is forwarded to the current phase only if the game is in the right phase.
    When the phase reports PHASE_ENDS, the controller starts the next phase.
    """

    def __init__( # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        players: Sequence[PlayerColor],
        determine_player_order: InterfaceDeterminePlayerOrderGameController,
        auction: InterfaceAuctionPowerPlantsGameController,
        buying: InterfaceBuyingResourcesGameController,
        building: InterfaceBuildingHousesGameController,
        bureaucracy: InterfaceBureaucracyGameController,
        is_first_turn: bool = True,
    ) -> None:
        # `players` is the initial order; shuffle it outside to control randomness.
        self.is_first_turn = is_first_turn
        self.game_phase = GamePhase.AUCTION
        self.game_over = False  # GamePhase has no GAME_END value
        self._player_order = list(players)
        self._determine_player_order = determine_player_order
        self._auction = auction
        self._buying = buying
        self._building = building
        self._bureaucracy = bureaucracy
        self._auction.start_phase(self._player_order)

    # ---------- phase 2: auction ----------
    def select_power_plant_to_bid(
        self, player: PlayerColor, ppn: PowerPlantNumber, first_bid: int
    ) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.AUCTION)) is not None:
            return err
        return self._handle(self._auction.select_power_plant_to_bid(player, ppn, first_bid))

    def do_not_want_power_plant(self, player: PlayerColor) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.AUCTION)) is not None:
            return err
        return self._handle(self._auction.do_not_want_power_plant(player))

    def bid_for_current_power_plant(self, player: PlayerColor, bid: int) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.AUCTION)) is not None:
            return err
        return self._handle(self._auction.bid_for_current_power_plant(player, bid))

    def do_not_bid_for_current_power_plant(self, player: PlayerColor) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.AUCTION)) is not None:
            return err
        return self._handle(self._auction.do_not_bid_for_current_power_plant(player))

    def remove_power_plant(
        self, player: PlayerColor, ppn: PowerPlantNumber, resources: Sequence[Resource]
    ) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.AUCTION)) is not None:
            return err
        return self._handle(self._auction.remove_power_plant(player, ppn, resources))

    # ---------- phase 3: resources ----------
    def buy_resources(
        self, player: PlayerColor, resources: Sequence[Resource]
    ) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.BUY_RESOURCES)) is not None:
            return err
        return self._handle(self._buying.buy_resources(player, resources))

    # ---------- phase 4: houses ----------
    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str]
    ) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.BUILD_HOUSES)) is not None:
            return err
        return self._handle(self._building.build_houses(player, town_names))

    # ---------- phase 5: bureaucracy ----------
    def use_power_plants(
        self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
        resources_to_burn: Sequence[Resource]
    ) -> Optional[RequestError]:
        if (err := self._check_phase(GamePhase.BUREAUCRACY)) is not None:
            return err
        return self._handle(self._bureaucracy.use_power_plants(player, ppns, resources_to_burn))

    # ---------- internals ----------
    def _check_phase(self, expected: GamePhase) -> Optional[RequestError]:
        if self.game_over:
            return RequestError("The game is over")
        if self.game_phase is not expected:
            return RequestError("Wrong phase")
        return None

    def _handle(self, result: Union[PhaseStatus, RequestError]) -> Optional[RequestError]:
        if isinstance(result, RequestError):
            return result
        if result is PhaseStatus.GAME_ENDS:
            self.game_over = True
        elif result is PhaseStatus.PHASE_ENDS:
            self._start_next_phase()
        return None

    def _start_next_phase(self) -> None:
        if self.game_phase is GamePhase.AUCTION:
            if self.is_first_turn:  # one-time re-ordering after the first auction
                self._player_order = self._determine_player_order.reorder()
            self.game_phase = GamePhase.BUY_RESOURCES
            self._buying.start_phase(self._reversed_order())
        elif self.game_phase is GamePhase.BUY_RESOURCES:
            self.game_phase = GamePhase.BUILD_HOUSES
            self._building.start_phase(self._reversed_order())
        elif self.game_phase is GamePhase.BUILD_HOUSES:
            self.game_phase = GamePhase.BUREAUCRACY
            self._bureaucracy.start_phase(self._player_order)
        elif self.game_phase is GamePhase.BUREAUCRACY:
            self.is_first_turn = False
            self._player_order = self._determine_player_order.reorder()
            self.game_phase = GamePhase.AUCTION
            self._auction.start_phase(self._player_order)

    def _reversed_order(self) -> list[PlayerColor]:
        return list(reversed(self._player_order))