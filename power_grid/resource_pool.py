
import json
from typing import Sequence

from power_grid.simple_types import Resource
from power_grid.interfaces import InterfaceResourcePoolResourceMarket


class ResourcePool(InterfaceResourcePoolResourceMarket):

    def __init__(self, resources: list[Resource], storage_space: list[Resource]) -> None:

        self.resources = resources.copy()
        self.storage_space = storage_space.copy()

    #Kontrola ci mame dostatok surovin v sklade
    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:

        sklad = self.storage_space.copy()

        for i in range(len(resources)):

            if resources[i] in sklad:
                sklad.remove(resources[i])

            else:
                return False

        return True

    #Odobratie surovin zo skladu
    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:

        if self.can_take_resources_from_storage_space(resources):

            for i in range(len(resources)):
                self.storage_space.remove(resources[i])

        else:
            assert False, "Not enough resources"

    #Odobratie surovin z hlavnej zasoby
    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:

        vysledok = []

        for i in range(len(resources)):

            if resources[i] in self.resources:

                self.resources.remove(resources[i])
                vysledok.append(resources[i])

        return vysledok

    #Pridanie surovin do zasoby
    def put_resources(self, resources: list[Resource]) -> None:

        for i in range(len(resources)):

            self.resources.append(resources[i])

    #Textovy vypis zasob
    def to_string(self) -> str:

        suroviny = []
        sklad = []

        for i in range(len(self.resources)):
            suroviny.append(self.resources[i].name)

        for i in range(len(self.storage_space)):
            sklad.append(self.storage_space[i].name)

        vysledok = {
            "resources": suroviny,
            "storage_space": sklad
        }

        return json.dumps(vysledok)
