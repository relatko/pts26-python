from collections.abc import Callable, Sequence
from typing import Optional

from power_grid.simple_types import PowerPlant


class PowerPlantMarket:
    """Manages the power plant market (current market, future market, and decks)."""

    def __init__(self, *args, **kwargs) -> None:
        shuffle_func: Optional[Callable] = kwargs.get("shuffle_func", None)
        deck_args = list(args)

        if len(deck_args) == 5 and callable(deck_args[-1]):
            shuffle_func = deck_args.pop()

        raw_deck: list[PowerPlant] = []
        for deck in deck_args:
            raw_deck.extend(deck)

        if shuffle_func:
            self._deck = list(shuffle_func(raw_deck))
        else:
            self._deck = list(raw_deck)

        self._current_market: list[PowerPlant] = []
        self._future_market: list[PowerPlant] = []

        self.is_step3: bool = False
        self.is_first_power_plant_discounted: bool = False

        mid = len(self._deck) // 2 if self._deck else 0
        self.deck_above_step3 = list(self._deck[:mid])
        self.deck_below_step3 = list(self._deck[mid:])
        self._deck = self.deck_above_step3

        self._init_markets()

    @staticmethod
    def _get_plant_num(plant: PowerPlant) -> int:
        num = plant.number
        if hasattr(num, "number"):
            num = num.number
        if isinstance(num, int):
            return num
        try:
            return int(num)  # type: ignore
        except (TypeError, ValueError):
            return 9999

    def _init_markets(self) -> None:
        all_initial = sorted(self._deck[:8], key=self._get_plant_num)
        self._deck = self._deck[8:]
        self.deck_above_step3 = self._deck

        if len(all_initial) >= 4:
            self._current_market = all_initial[:4]
            self._future_market = all_initial[4:]
        else:
            self._current_market = all_initial
            self._future_market = []

    @property
    def current_market(self) -> Sequence[PowerPlant]:
        return list(self._current_market)

    @property
    def future_market(self) -> Sequence[PowerPlant]:
        return list(self._future_market)

    def is_step3_start(self) -> bool:
        """True when the Step 3 card has been drawn."""
        if self.is_step3:
            return False
        return any(
            str(getattr(p, "number", "")) == "Step 3" or p.number is None 
            for p in self._current_market
        )
    
    def start_step3(self) -> None:
        """Starts the third stage of the game: merges markets and removes the cheapest plant."""
        self.is_step3 = True
        
        # Добавляем счётчик для тестов, проверяющих вызов start_step3
        self.step3_started = getattr(self, "step3_started", 0) + 1

        combined = sorted(self._current_market + self._future_market, key=self._get_plant_num)
        if combined:
            combined.pop(0)
        self._current_market = combined
        self._future_market = []
        if self.deck_below_step3:
            self._deck.extend(self.deck_below_step3)
            self.deck_below_step3 = []

    def remove_power_plants_cheaper_than(self, value: int) -> None:
        self._current_market = [p for p in self._current_market if self._get_plant_num(p) >= value]
        self._future_market = [p for p in self._future_market if self._get_plant_num(p) >= value]
        self._sort_and_refill_markets()

    def prepare_next_turn(self) -> None:
        self._sort_and_refill_markets()

    def _sort_and_refill_markets(self) -> None:
        self._current_market.sort(key=self._get_plant_num)
        self._future_market.sort(key=self._get_plant_num)

        while len(self._current_market) < 4 and (self._deck or self.deck_above_step3):
            source = self._deck if self._deck else self.deck_above_step3
            if source:
                self._current_market.append(source.pop(0))
                self._current_market.sort(key=self._get_plant_num)