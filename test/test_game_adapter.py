import unittest

from power_grid.game_adapter import PowerGridGameAdapter
from power_grid.simple_types import SerializedGameState


class TestPowerGridGameAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter: PowerGridGameAdapter = PowerGridGameAdapter()

    def test_to_external_wraps_the_state(self) -> None:
        # Test conversion to external
        external = self.adapter.to_external("test_state")
        self.assertIsInstance(external, SerializedGameState)
        self.assertEqual(external.state, "test_state")

    def test_to_internal_unwraps_the_state(self) -> None:
        # Test conversion back to internal
        internal = self.adapter.to_internal(SerializedGameState("test_state"))
        self.assertEqual(internal, "test_state")

    def test_round_trip_keeps_json_untouched(self) -> None:
        # The adapter must not change the content of the state string
        state = '{"phase": "AUCTION", "current_player": "RED"}'
        external = self.adapter.to_external(state)
        self.assertEqual(self.adapter.to_internal(external), state)