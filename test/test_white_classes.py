import unittest
from power_grid.simple_types import (
    PlayerColor,
    Resource,
    PhaseStatus,
    GamePhase,
    GameStep,
    PowerPlant,
    RequestError,
    SerializedGameState,
    PowerPlantNumber,
)


class TestWhiteClasses(unittest.TestCase):
    """
    Unit tests for the white classes (Enums and Dataclasses).
    These tests ensure that the basic building blocks of the game are correct.
    """

    def test_enums_exist(self) -> None:
        """
        Test that all enums are properly defined and have the correct number of values.
        """
        self.assertEqual(len(PlayerColor), 6)
        self.assertEqual(len(Resource), 4)
        self.assertEqual(len(PhaseStatus), 3)
        # GamePhase includes GAME_END, so it has 5 elements
        self.assertEqual(len(GamePhase), 5)
        self.assertEqual(len(GameStep), 3)

    def test_power_plant_valid(self) -> None:
        """
        Test creating a valid power plant using the new UML fields.
        """
        plant = PowerPlant(
            number=PowerPlantNumber(13), 
            acceptedResources=[Resource.COAL], 
            numberOfCities=3, 
            resourceAmount=2
        )
        self.assertEqual(plant.number.number, 13)
        self.assertEqual(plant.acceptedResources, [Resource.COAL])
        self.assertEqual(plant.numberOfCities, 3)
        self.assertEqual(plant.resourceAmount, 2)

    def test_power_plant_ecological(self) -> None:
        """
        Test creating an ecological power plant (no resources needed).
        """
        plant = PowerPlant(
            number=PowerPlantNumber(20), 
            acceptedResources=[], 
            numberOfCities=5, 
            resourceAmount=0
        )
        self.assertEqual(plant.acceptedResources, [])
        self.assertEqual(plant.numberOfCities, 5)
        self.assertEqual(plant.resourceAmount, 0)

    def test_dataclasses(self) -> None:
        """
        Test the other dataclasses.
        """
        err = RequestError(description="Not enough money")
        self.assertEqual(err.description, "Not enough money")
        
        state = SerializedGameState(state="{}")
        self.assertEqual(state.state, "{}")
        
        num = PowerPlantNumber(number=5)
        self.assertEqual(num.number, 5)


if __name__ == '__main__':
    unittest.main()