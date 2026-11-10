from power_grid.simple_types import PlayerColor
from power_grid.steps import DeterminePlayerOrder, CheckAndBumpStep


def test_player_order() -> None:
    logic = DeterminePlayerOrder()
    
    # Assume RED has 5 cities, BLUE has 2, and GREEN has 8
    order = logic.gameResult({PlayerColor.RED: 5, PlayerColor.BLUE: 2, PlayerColor.GREEN: 8})
    
    # BLUE should be first, RED second, GREEN third
    assert order == [PlayerColor.BLUE, PlayerColor.RED, PlayerColor.GREEN]


def test_check_and_bump() -> None:
    logic = CheckAndBumpStep()
    
    # The game should remain in Step 1 with 5 cities
    assert logic.getStep() == 1
    assert logic.checkAndBumpToStep2(max_cities=5) is False
    
    # The game should advance to Step 2 when a player reaches 7 cities
    assert logic.checkAndBumpToStep2(max_cities=7) is True
    assert logic.getStep() == 2
    
    # The game should advance to Step 3 when a player reaches 14 cities
    assert logic.checkAndBumpToStep3(max_cities=14) is True
    assert logic.getStep() == 3