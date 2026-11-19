from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Resource(Enum):
    COAL = 1
    OIL = 2
    GARBAGE = 3
    URANIUM = 4


class PlayerColor(Enum):
    RED = "Red"
    YELLOW = "Yellow"
    BLUE = "Blue"
    GREEN = "Green"
    PURPLE = "Purple"
    BLACK = "Black"


class PhaseStatus(Enum):
    PHASE_CONTINUES = "PhaseContinues"
    PHASE_ENDS = "PhaseEnds"
    GAME_ENDS = "GameEnds"


class GamePhase(Enum):
    AUCTION_POWER_PLANTS = "AuctionPowerPlants"
    BUY_RESOURCES = "BuyResources"
    BUY_HOUSES = "BuyHouses"
    BUREAUCRACY = "Bureaucracy"
    GAME_END = "GameEnd"


@dataclass(frozen=True, order=True)
class PowerPlantNumber:
    number: int


@dataclass(frozen=True)
class PowerPlant:
    number: PowerPlantNumber
    accepted_resources: list[Resource]
    resource_amount: int
    number_of_cities: int


@dataclass(frozen=True)
class RequestError:
    description: str


@dataclass(frozen=True)
class SerializedGameState:
    state: str
