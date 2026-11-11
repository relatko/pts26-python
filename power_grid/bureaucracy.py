# pylint: disable=too-many-arguments, too-many-positional-arguments
"""Bureaucracy phase."""
from collections import Counter
from typing import Mapping, Sequence, Union
from power_grid.phase_dependencies import (
    PlayerBoardForPhases, PowerPlantMarketForPhases, ResourcePoolForPhases,
    StepChecker, TownsForPhases, TurnOrder)
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlant, PowerPlantNumber, RequestError,
    Resource)


class Bureaucracy:
    """Players burn resources and get income; then the markets are refilled."""

    def __init__(self, players: Mapping[PlayerColor, PlayerBoardForPhases],
                 towns: TownsForPhases, pool: ResourcePoolForPhases,
                 market: PowerPlantMarketForPhases, steps: StepChecker,
                 towns_to_end_game: int) -> None:
        self._players = players
        self._towns = towns
        self._pool = pool
        self._market = market
        self._steps = steps
        self._towns_to_end_game = towns_to_end_game
        self._turn = TurnOrder()

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Starts the phase."""
        self._turn.start(player_order)

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> Union[PhaseStatus, RequestError]:
        """Runs the chosen plants, burns fuel and pays income."""
        error = self._turn.check_turn(player)
        if error is not None:
            return error
        board = self._players[player]
        plants = self._chosen_plants(board, ppns, resources_to_burn)
        if isinstance(plants, RequestError):
            return plants
        board.remove_resources(resources_to_burn)
        powered = min(sum(p.cities for p in plants),
                      self._towns.number_of_towns(player))
        board.receive_money(powered)
        if self._turn.advance() is PhaseStatus.PHASE_ENDS:
            return self._finish_round()
        return PhaseStatus.CONTINUES

    def get_state(self) -> str:
        """Serialized state of the phase."""
        return self._turn.state("BUREAUCRACY")

    @staticmethod
    def _chosen_plants(
            board: PlayerBoardForPhases, ppns: Sequence[PowerPlantNumber],
            burn: Sequence[Resource]) -> Union[list[PowerPlant], RequestError]:
        if len(set(ppns)) != len(ppns):
            return RequestError("Power plant listed twice")
        owned = {PowerPlantNumber(p.number): p for p in board.get_power_plants()}
        plants: list[PowerPlant] = []
        for ppn in ppns:
            if ppn not in owned:
                return RequestError(f"Power plant {ppn.number} is not yours")
            plants.append(owned[ppn])
        needed: Counter[Resource] = Counter()
        for plant in plants:
            if plant.resource is not None:
                needed[plant.resource] += plant.required_resources
        if Counter(burn) != needed:
            return RequestError("Resources to burn do not match the power plants")
        if Counter(burn) - Counter(board.get_resources()):
            return RequestError("You do not have these resources")
        return plants

    def _finish_round(self) -> PhaseStatus:
        if self._towns.get_max_number_of_houses() >= self._towns_to_end_game:
            return PhaseStatus.GAME_ENDS
        self._pool.refill(self._steps.getStep(), len(self._players))
        self._market.prepare_next_turn()
        return PhaseStatus.PHASE_ENDS
