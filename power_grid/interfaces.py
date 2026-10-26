# pylint: disable=unused-argument, duplicate-code
from typing import Sequence
from power_grid.simple_types import Resource


class InterfaceResourcePoolResourceMarket:
    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        assert False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        assert False

    def to_string(self) -> str:
        assert False
