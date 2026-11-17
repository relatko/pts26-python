# PowerGridGameAdapter: converts the external types (ints, strings) to internal ones.
from collections.abc import Callable, Sequence
from typing import Protocol

from power_grid.interfaces import PowerGridRulesGameInterface
from power_grid.simple_types import (
    PlayerColor,
    PowerPlantNumber,
    RequestError,
    Resource,
    SerializedGameState,
)

RESOURCE_CODES: dict[str, Resource] = {
    "C": Resource.COAL,
    "O": Resource.OIL,
    "G": Resource.GARBAGE,
    "U": Resource.URANIUM,
}


class GameControllerForAdapter(Protocol):
    # GameController as seen by the adapter.

    def select_power_plant_to_bid(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            first_bid: int) -> RequestError | None:
        ...

    def do_not_want_power_plant(self, player: PlayerColor) -> RequestError | None:
        ...

    def bid_for_current_power_plant(self, player: PlayerColor, bid: int) -> RequestError | None:
        ...

    def do_not_bid_for_current_power_plant(self, player: PlayerColor) -> RequestError | None:
        ...

    def remove_power_plant(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            resources: Sequence[Resource]) -> RequestError | None:
        ...

    def buy_resources(
            self, player: PlayerColor, resources: Sequence[Resource]) -> RequestError | None:
        ...

    def buy_houses(
            self, player: PlayerColor, town_names: Sequence[str]) -> RequestError | None:
        ...

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> RequestError | None:
        ...

    def get_state(self) -> str:
        ...


def parse_resources(text: str) -> list[Resource] | RequestError:
    # Decodes a string such as "CCOU" into resources.
    resources: list[Resource] = []
    for code in text:
        if code not in RESOURCE_CODES:
            return RequestError(f"Unknown resource '{code}'")
        resources.append(RESOURCE_CODES[code])
    return resources


class PowerGridGameAdapter(PowerGridRulesGameInterface):
    # Converts internal and external types.
    #
    # Player ids are indexes into `players`; every successful request
    # returns the new state of the game.

    def __init__(self, controller: GameControllerForAdapter,
                 players: Sequence[PlayerColor]) -> None:
        self._controller = controller
        self._players: list[PlayerColor] = list(players)

    def to_external(self, internal_state: str) -> SerializedGameState:
        # Converts internal string to the external SerializedGameState type.
        return SerializedGameState(state=internal_state)

    def to_internal(self, external_state: SerializedGameState) -> str:
        # Converts external state back to internal string.
        return external_state.state

    def selectPowerPlantToBid(
        self, playerId: int, powerPlantNumber: int, firstBid: int
    ) -> SerializedGameState | RequestError:
        return self._call(playerId, lambda player: self._controller.select_power_plant_to_bid(
            player, PowerPlantNumber(powerPlantNumber), firstBid))

    def doNotWantPowerPlant(self, playerId: int) -> SerializedGameState | RequestError:
        return self._call(playerId, self._controller.do_not_want_power_plant)

    def bidForCurrentPowerPlant(
        self, playerId: int, bid: int
    ) -> SerializedGameState | RequestError:
        return self._call(
            playerId, lambda player: self._controller.bid_for_current_power_plant(player, bid))

    def doNotBidForCurrentPowerPlant(self, playerId: int) -> SerializedGameState | RequestError:
        return self._call(playerId, self._controller.do_not_bid_for_current_power_plant)

    def removePowerPlant(
        self, playerId: int, powerplantNumber: int, removedResources: str
    ) -> SerializedGameState | RequestError:
        resources = parse_resources(removedResources)
        if isinstance(resources, RequestError):
            return resources
        return self._call(playerId, lambda player: self._controller.remove_power_plant(
            player, PowerPlantNumber(powerplantNumber), resources))

    def buyResources(self, playerId: int, resources: str) -> SerializedGameState | RequestError:
        parsed = parse_resources(resources)
        if isinstance(parsed, RequestError):
            return parsed
        return self._call(
            playerId, lambda player: self._controller.buy_resources(player, parsed))

    def buyHouses(
        self, playerId: int, townNames: Sequence[str]
    ) -> SerializedGameState | RequestError:
        return self._call(
            playerId, lambda player: self._controller.buy_houses(player, townNames))

    def usePowerPlants(
        self, playerId: int, powerPlantNumbers: Sequence[int], resourcesToBurn: str
    ) -> SerializedGameState | RequestError:
        resources = parse_resources(resourcesToBurn)
        if isinstance(resources, RequestError):
            return resources
        numbers = [PowerPlantNumber(number) for number in powerPlantNumbers]
        return self._call(playerId, lambda player: self._controller.use_power_plants(
            player, numbers, resources))

    def _call(
        self, player_id: int, action: Callable[[PlayerColor], RequestError | None]
    ) -> SerializedGameState | RequestError:
        if not 0 <= player_id < len(self._players):
            return RequestError(f"Unknown player {player_id}")
        error = action(self._players[player_id])
        if error is not None:
            return error
        return self.to_external(self._controller.get_state())