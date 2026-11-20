from __future__ import annotations

from power_grid.simple_types import Resource, RequestError
from power_grid.power_plant import PowerPlant


class UsePowerPlants:

    def number_of_suppliable_towns(
        self, resources: list[Resource], powerplants: list[PowerPlant]
    ) -> int | RequestError:
        remaining = resources.copy()
        suppliable_towns = 0

        sorted_plants = sorted(
            powerplants, key=lambda plant: len(plant.accepted_resources)
        )

        for plant in sorted_plants:
            for _ in range(plant.resource_amount):
                for resource_type in plant.accepted_resources:
                    if resource_type in remaining:
                        remaining.remove(resource_type)
                        break
                else:
                    return RequestError("Not enough resources for one of chosen powerplants")

            suppliable_towns += plant.number_of_cities

        if remaining:
            return RequestError("More resources than expected")

        return suppliable_towns
    