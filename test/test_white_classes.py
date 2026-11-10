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
        This prevents accidental deletion or addition of enum members.
        """
        # PlayerColor should have 6 colors: RED, BLUE, GREEN, YELLOW, PURPLE, BLACK
        self.assertEqual(len(PlayerColor), 6)
        
        # Resource should have 4 types: COAL, OIL, GARBAGE, URANIUM
        self.assertEqual(len(Resource), 4)
        
        # PhaseStatus should have 3 states
        self.assertEqual(len(PhaseStatus), 3)
        
        # GamePhase should have 4 phases: AUCTION, BUY_RESOURCES, BUILD_HOUSES, BUREAUCRACY
        self.assertEqual(len(GamePhase), 4)
        
        # GameStep should have 3 steps: STEP_1, STEP_2, STEP_3
        self.assertEqual(len(GameStep), 3)

    def test_power_plant_valid(self) -> None:
        """
        Test creating a valid power plant.
        Verifies that all attributes are stored correctly by the dataclass.
        """
        plant = PowerPlant(
            number=13, 
            resource=Resource.COAL, 
            cities=3, 
            required_resources=2
        )
        self.assertEqual(plant.number, 13)
        self.assertEqual(plant.resource, Resource.COAL)
        self.assertEqual(plant.cities, 3)
        self.assertEqual(plant.required_resources, 2)

    def test_power_plant_ecological(self) -> None:
        """
        Test creating an ecological power plant (e.g., wind or solar).
        Ecological plants do not require any resources to operate.
        """
        plant = PowerPlant(
            number=20, 
            resource=None, 
            cities=5, 
            required_resources=0
        )
        # The resource must be None, and required_resources must be 0.
        self.assertIsNone(plant.resource)
        self.assertEqual(plant.required_resources, 0)

    def test_power_plant_invalid_number(self) -> None:
        """
        Test that invalid plant numbers raise a ValueError.
        In Power Grid, valid power plant numbers are between 3 and 50 inclusive.
        """
        # Using assertRaisesRegex checks both the exception type and the error message.
        with self.assertRaisesRegex(ValueError, "Invalid power plant number"):
            PowerPlant(
                number=100, 
                resource=Resource.COAL, 
                cities=3, 
                required_resources=1
            )

    def test_power_plant_invalid_cities(self) -> None:
        """
        Test that plants powering 0 cities raise a ValueError.
        A power plant must be able to power at least 1 city.
        """
        with self.assertRaisesRegex(ValueError, "at least 1 city"):
            PowerPlant(
                number=13, 
                resource=Resource.COAL, 
                cities=0, 
                required_resources=1
            )

    def test_power_plant_missing_resources(self) -> None:
        """
        Test that non-ecological plants without required resources raise a ValueError.
        If a plant uses a resource, it must require at least 1 unit of it.
        """
        with self.assertRaisesRegex(ValueError, "must require at least 1 resource"):
            PowerPlant(
                number=13, 
                resource=Resource.COAL, 
                cities=3, 
                required_resources=0
            )

    def test_dataclasses(self) -> None:
        """
        Test the other dataclasses (RequestError, SerializedGameState, PowerPlantNumber).
        These are simple wrappers and should just hold their values.
        """
        # Test RequestError
        err = RequestError(description="Not enough money")
        self.assertEqual(err.description, "Not enough money")
        
        # Test SerializedGameState
        state = SerializedGameState(state="{}")
        self.assertEqual(state.state, "{}")
        
        # Test PowerPlantNumber
        num = PowerPlantNumber(number=5)
        self.assertEqual(num.number, 5)


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    unittest.main()