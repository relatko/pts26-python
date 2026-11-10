from power_grid.steps import DeterminePlayerOrder, CheckAndBumpStep
from power_grid.simple_types import PlayerColor

def test_player_order() -> None:
    logic = DeterminePlayerOrder()
    # Assume RED has 5 cities, BLUE has 2, and GREEN has 8
    order = logic.get_order({PlayerColor.RED: 5, PlayerColor.BLUE: 2, PlayerColor.GREEN: 8})
    
    # BLUE should be first, RED second, GREEN third
    assert order == [PlayerColor.BLUE, PlayerColor.RED, PlayerColor.GREEN]

def test_check_and_bump() -> None:
    logic = CheckAndBumpStep()
    # The game should remain in Step 1 with 5 cities
    assert logic.check_and_bump(max_cities=5) == 1 
    # The game should advance to Step 2 when a player reaches 7 cities
    assert logic.check_and_bump(max_cities=7) == 2