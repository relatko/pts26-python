from power_grid.simple_types import SerializedGameState


class PowerGridGameAdapter:
    """
    Converts internal and external types.
    """
    def to_external(self, internal_state: str) -> SerializedGameState:
        # Converts internal string to the external SerializedGameState type
        return SerializedGameState(state=internal_state)

    def to_internal(self, external_state: SerializedGameState) -> str:
        # Converts external state back to internal string
        return external_state.state