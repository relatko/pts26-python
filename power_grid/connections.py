"""Connections between towns and the price of connecting a town to a network."""
import heapq
from typing import Sequence


class Connections:
    """Undirected graph of towns with the connection costs."""

    def __init__(self, distances: Sequence[tuple[str, str, int]]) -> None:
        self._graph: dict[str, dict[str, int]] = {}
        for first, second, cost in distances:
            if cost < 0:
                raise ValueError("Connection cost cannot be negative")
            self._graph.setdefault(first, {})[second] = cost
            self._graph.setdefault(second, {})[first] = cost

    @property
    def towns(self) -> set[str]:
        """Names of all towns."""
        return set(self._graph)

    def calculate_connecting_cost(
        self, from_towns: Sequence[str], to_towns: Sequence[str]
    ) -> int:
        """Cheapest connection from any of `from_towns` to any of `to_towns`.

        0 if `from_towns` is empty (the first house) or the sets overlap.
        Raises ValueError for an unknown town or when there is no path.
        """
        for town in (*from_towns, *to_towns):
            if town not in self._graph:
                raise ValueError(f"Unknown town {town}")
        if not from_towns or not to_towns:
            return 0
        targets = set(to_towns)
        best = {town: 0 for town in from_towns}
        heap = [(0, town) for town in from_towns]
        heapq.heapify(heap)
        while heap:
            cost, town = heapq.heappop(heap)
            if cost > best[town]:
                continue
            if town in targets:
                return cost
            for neighbour, price in self._graph[town].items():
                new_cost = cost + price
                if neighbour not in best or new_cost < best[neighbour]:
                    best[neighbour] = new_cost
                    heapq.heappush(heap, (new_cost, neighbour))
        raise ValueError("The towns are not connected")
