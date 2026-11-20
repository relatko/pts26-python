import heapq
from collections.abc import Sequence


class Connections:
    def __init__(self, distances: Sequence[tuple[str, str, int]]) -> None:
        self._distances: list[tuple[str, str, int]] = []
        self._adjacency: dict[str, list[tuple[str, int]]] = {}

        for town_a, town_b, cost in distances:
            if cost < 0:
                raise ValueError(
                    f"Connection cost must be non-negative, got {cost} "
                    f"for ({town_a}, {town_b})"
                )
            self._distances.append((town_a, town_b, cost))
            self._adjacency.setdefault(town_a, []).append((town_b, cost))
            self._adjacency.setdefault(town_b, []).append((town_a, cost))

    @property
    def distances(self) -> list[tuple[str, str, int]]:
        return list(self._distances)

    def calculate_connecting_cost(
        self,
        from_towns: Sequence[str],
        to_towns: Sequence[str],
    ) -> int:
        owned: set[str] = set(from_towns)
        remaining: list[str] = []
        seen_targets: set[str] = set()
        for town in to_towns:
            if town not in owned and town not in seen_targets:
                remaining.append(town)
                seen_targets.add(town)

        if not remaining:
            return 0

        remaining_set: set[str] = set(remaining)
        if not owned:
            first_town = remaining[0]
            owned.add(first_town)
            remaining_set.remove(first_town)

        total_cost = 0
        while remaining_set:
            nearest_town, nearest_cost = self._find_nearest_target(
                owned, remaining_set
            )
            total_cost += nearest_cost
            owned.add(nearest_town)
            remaining_set.remove(nearest_town)

        return total_cost

    def _find_nearest_target(
        self,
        owned: set[str],
        targets: set[str],
    ) -> tuple[str, int]:
        best_distances: dict[str, int] = {town: 0 for town in owned}
        heap: list[tuple[int, str]] = [(0, town) for town in owned]
        heapq.heapify(heap)

        while heap:
            current_cost, current_town = heapq.heappop(heap)
            if current_cost > best_distances[current_town]:
                continue
            if current_town in targets:
                return current_town, current_cost

            for neighbor, edge_cost in self._adjacency.get(current_town, ()):
                next_cost = current_cost + edge_cost
                if next_cost < best_distances.get(neighbor, next_cost + 1):
                    best_distances[neighbor] = next_cost
                    heapq.heappush(heap, (next_cost, neighbor))

        unreachable = ", ".join(sorted(targets))
        raise ValueError(f"No connection path to town(s): {unreachable}")
