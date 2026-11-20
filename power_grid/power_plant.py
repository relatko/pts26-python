
from power_grid.simple_types import Resource


class PowerPlantNumber:

    def __init__(self, number: int) -> None:
        self.number = number


class PowerPlant:

    def __init__(self, number: PowerPlantNumber,
                 accepted_resources: list[Resource],
                 resource_amount: int,
                 number_of_cities: int) -> None:

        self.number = number
        self.accepted_resources = accepted_resources
        self.resource_amount = resource_amount
        self.number_of_cities = number_of_cities
