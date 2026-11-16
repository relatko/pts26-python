# pylint: disable=too-many-instance-attributes
import json
import unittest
from collections.abc import Sequence

from test.test_game_controller import (
    FakeAuction,
    FakeBuilding,
    FakeBureaucracy,
    FakeBuying,
    FakeOrder,
)
from power_grid.game_adapter import PowerGridGameAdapter
from power_grid.game_controller import GameController
from power_grid.simple_types import (
    PhaseStatus,
    PlayerColor,
    PowerPlantNumber,
    RequestError,
    Resource,
    SerializedGameState,
)

RED, BLUE = PlayerColor.RED, PlayerColor.BLUE


class FakeController:
    # Records the calls of the adapter.

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.error: RequestError | None = None

    def select_power_plant_to_bid(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            first_bid: int) -> RequestError | None:
        self.calls.append(("select", player, ppn, first_bid))
        return self.error

    def do_not_want_power_plant(self, player: PlayerColor) -> RequestError | None:
        self.calls.append(("do_not_want", player))
        return self.error

    def bid_for_current_power_plant(self, player: PlayerColor, bid: int) -> RequestError | None:
        self.calls.append(("bid", player, bid))
        return self.error

    def do_not_bid_for_current_power_plant(self, player: PlayerColor) -> RequestError | None:
        self.calls.append(("do_not_bid", player))
        return self.error

    def remove_power_plant(
            self, player: PlayerColor, ppn: PowerPlantNumber,
            resources: Sequence[Resource]) -> RequestError | None:
        self.calls.append(("remove", player, ppn, list(resources)))
        return self.error

    def buy_resources(
            self, player: PlayerColor, resources: Sequence[Resource]) -> RequestError | None:
        self.calls.append(("buy_resources", player, list(resources)))
        return self.error

    def buy_houses(
            self, player: PlayerColor, town_names: Sequence[str]) -> RequestError | None:
        self.calls.append(("buy_houses", player, list(town_names)))
        return self.error

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> RequestError | None:
        self.calls.append(("use", player, list(ppns), list(resources_to_burn)))
        return self.error

    def get_state(self) -> str:
        return "state"


class TestPowerGridGameAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.controller: FakeController = FakeController()
        self.adapter: PowerGridGameAdapter = PowerGridGameAdapter(
            self.controller, [RED, BLUE])

    def test_to_external_wraps_the_state(self) -> None:
        # Test conversion to external
        external = self.adapter.to_external("test_state")
        self.assertIsInstance(external, SerializedGameState)
        self.assertEqual(external.state, "test_state")

    def test_to_internal_unwraps_the_state(self) -> None:
        # Test conversion back to internal
        internal = self.adapter.to_internal(SerializedGameState("test_state"))
        self.assertEqual(internal, "test_state")

    def test_player_id_is_converted_to_color_and_state_returned(self) -> None:
        # Player 1 is the second player in the list, i.e. BLUE
        result = self.adapter.selectPowerPlantToBid(1, 13, 20)
        self.assertEqual(result, SerializedGameState("state"))
        self.assertEqual(
            self.controller.calls, [("select", BLUE, PowerPlantNumber(13), 20)])

    def test_simple_auction_requests_are_forwarded(self) -> None:
        self.adapter.doNotWantPowerPlant(0)
        self.adapter.bidForCurrentPowerPlant(1, 25)
        self.adapter.doNotBidForCurrentPowerPlant(0)
        self.assertEqual(self.controller.calls, [
            ("do_not_want", RED), ("bid", BLUE, 25), ("do_not_bid", RED)])

    def test_resources_string_is_converted(self) -> None:
        # "C" is coal, "O" oil, "G" garbage and "U" uranium
        self.adapter.buyResources(0, "CCOGU")
        self.assertEqual(self.controller.calls, [(
            "buy_resources", RED,
            [Resource.COAL, Resource.COAL, Resource.OIL,
             Resource.GARBAGE, Resource.URANIUM])])

    def test_empty_resources_string_means_no_resources(self) -> None:
        self.adapter.buyResources(0, "")
        self.assertEqual(self.controller.calls, [("buy_resources", RED, [])])

    def test_remove_power_plant_converts_number_and_resources(self) -> None:
        self.adapter.removePowerPlant(1, 5, "C")
        self.assertEqual(self.controller.calls, [
            ("remove", BLUE, PowerPlantNumber(5), [Resource.COAL])])

    def test_buy_houses_may_be_empty(self) -> None:
        # An empty list of towns means the player passes
        self.adapter.buyHouses(0, [])
        self.adapter.buyHouses(1, ["Berlin", "Essen"])
        self.assertEqual(self.controller.calls, [
            ("buy_houses", RED, []), ("buy_houses", BLUE, ["Berlin", "Essen"])])

    def test_use_power_plants_converts_numbers_and_resources(self) -> None:
        self.adapter.usePowerPlants(0, [3, 7], "OG")
        self.assertEqual(self.controller.calls, [(
            "use", RED, [PowerPlantNumber(3), PowerPlantNumber(7)],
            [Resource.OIL, Resource.GARBAGE])])

    def test_unknown_resource_is_an_error_and_nothing_is_forwarded(self) -> None:
        for result in (self.adapter.buyResources(0, "CX"),
                       self.adapter.removePowerPlant(0, 5, "?"),
                       self.adapter.usePowerPlants(0, [5], "c")):
            self.assertIsInstance(result, RequestError)
        self.assertEqual(self.controller.calls, [])

    def test_unknown_player_is_an_error_and_nothing_is_forwarded(self) -> None:
        self.assertIsInstance(self.adapter.doNotWantPowerPlant(2), RequestError)
        self.assertIsInstance(self.adapter.doNotWantPowerPlant(-1), RequestError)
        self.assertEqual(self.controller.calls, [])

    def test_error_from_the_controller_is_returned(self) -> None:
        self.controller.error = RequestError("Wrong phase")
        self.assertEqual(
            self.adapter.buyHouses(0, ["Berlin"]), RequestError("Wrong phase"))


class TestAdapterWithGameController(unittest.TestCase):
    # The adapter on top of the real GameController (phases are fakes).

    def setUp(self) -> None:
        self.auction = FakeAuction()
        self.controller = GameController(
            [RED, BLUE], FakeOrder(), self.auction, FakeBuying(),
            FakeBuilding(), FakeBureaucracy())
        self.adapter = PowerGridGameAdapter(self.controller, [RED, BLUE])

    def test_successful_request_returns_the_serialized_game_state(self) -> None:
        result = self.adapter.selectPowerPlantToBid(0, 3, 3)
        self.assertIsInstance(result, SerializedGameState)
        if isinstance(result, SerializedGameState):
            self.assertEqual(json.loads(result.state)["game_phase"], "AUCTION")

    def test_request_in_the_wrong_phase_is_an_error(self) -> None:
        self.assertIsInstance(self.adapter.buyResources(0, "C"), RequestError)

    def test_end_of_the_phase_is_visible_in_the_state(self) -> None:
        self.auction.result = PhaseStatus.PHASE_ENDS
        result = self.adapter.selectPowerPlantToBid(0, 3, 3)
        if isinstance(result, SerializedGameState):
            self.assertEqual(json.loads(result.state)["game_phase"], "BUY_RESOURCES")
        else:
            self.fail("A state was expected")