"""BuildingHouses phase."""
from typing import Mapping, Sequence, Union
from power_grid.phase_dependencies import (
    PlayerBoardForPhases, PowerPlantMarketForPhases, StepChecker,
    TownsForPhases, TurnOrder)
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError


class BuildingHouses:
    """Players build houses one by one in the given order."""

    def __init__(self, players: Mapping[PlayerColor, PlayerBoardForPhases],
                 towns: TownsForPhases, market: PowerPlantMarketForPhases,
                 steps: StepChecker) -> None:
        self._players = players
        self._towns = towns
        self._market = market
        self._steps = steps
        self._turn = TurnOrder()

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Starts the phase; an empty list of towns means passing."""
        self._turn.start(player_order)

    def build_houses(
            self, player: PlayerColor,
            town_names: Sequence[str]) -> Union[PhaseStatus, RequestError]:
        """Builds houses in the given towns for the player on turn."""
        error = self._turn.check_turn(player)
        if error is not None:
            return error
        board = self._players[player]
        if town_names:
            cost = self._towns.buy_houses(
                player, town_names, board.outstanding_money())
            if isinstance(cost, RequestError):
                return cost
            board.spend_money(cost)
            self._update_steps()
        return self._turn.advance()

    def get_state(self) -> str:
        """Serialized state of the phase."""
        return self._turn.state("BUILD_HOUSES")

    def _update_steps(self) -> None:
        max_houses = self._towns.get_max_number_of_houses()
        if self._steps.checkAndBumpToStep2(max_houses):
            self._towns.start_step2()
        if self._steps.checkAndBumpToStep3(max_houses):
            self._market.start_step3()
        self._market.remove_power_plants_cheaper_than(max_houses + 1)
