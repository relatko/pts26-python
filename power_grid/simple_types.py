from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class Resource(Enum):
    """The four types of resources available in the game."""
    COAL = 1
    OIL = 2
    GARBAGE = 3
    URANIUM = 4


class PlayerColor(Enum):
    """The possible colors for players. Power Grid supports up to 6 players."""
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    PURPLE = auto()
    BLACK = auto()


class PhaseStatus(Enum):
    """Indicates the status of the current phase or the game itself."""
    CONTINUES = auto()
    PHASE_ENDS = auto()
    GAME_ENDS = auto()


class GamePhase(Enum):
    """The four sequential phases that make up a single game round."""
    AUCTION = auto()
    BUY_RESOURCES = auto()
    BUILD_HOUSES = auto()
    BUREAUCRACY = auto()


class GameStep(Enum):
    """The three steps of the game. The step affects building limits and deck composition."""
    STEP_1 = auto()
    STEP_2 = auto()
    STEP_3 = auto()


@dataclass(frozen=True)
class PowerPlantNumber:
    """A simple wrapper around an integer representing a power plant's number."""
    number: int


@dataclass(frozen=True)
class RequestError:
    """Represents an error returned by a game action instead of raising an exception."""
    description: str


@dataclass(frozen=True)
class SerializedGameState:
    """Holds the serialized state of the game, typically as a JSON string."""
    state: str


@dataclass(frozen=True)
class PowerPlant:
    """
    Represents a power plant card.
    
    Attributes:
        number: The plant's number (also its minimum auction bid).
        resource: The resource it requires (None if it's an ecological plant).
        cities: How many cities this plant can power.
        required_resources: How many units of the resource are needed to run it.
    """
    number: int
    resource: Optional[Resource]
    cities: int
    required_resources: int = 0

    def post_init(self) -> None:
        """Validates the power plant data after initialization."""
        if self.number < 3 or self.number > 50:
            raise ValueError(f"Invalid power plant number: {self.number}")
        if self.cities < 1:
            raise ValueError("Power plant must power at least 1 city")
        if self.resource is not None and self.required_resources < 1:
            raise ValueError("Non-ecological plant must require at least 1 resource")