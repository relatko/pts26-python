"""PowerPlantMarket: the current market, the future market and the draw deck."""
import random
from typing import Callable, Optional, Sequence

from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError

Shuffle = Callable[[list[PowerPlant]], None]
MARKET_SIZE = 4
STEP3_MARKET_SIZE = 6


def _number(plant: PowerPlant) -> int:
    return plant.number


class PowerPlantMarket:  # pylint: disable=too-many-instance-attributes
    """Plants in the current market can be bought; the future market is only visible.

    The draw deck is `deck_above_step3`, then the Step 3 card, then `deck_below_step3`.
    Randomness is controlled by the `shuffle` argument, so tests can make it deterministic.
    """

    def __init__(
        self,
        current: Sequence[PowerPlant],
        future: Sequence[PowerPlant],
        deck_above_step3: Sequence[PowerPlant],
        deck_below_step3: Sequence[PowerPlant],
        shuffle: Shuffle = random.shuffle,
    ) -> None:
        self.is_first_power_plant_discounted = True
        self._current = list(current)
        self._future = list(future)
        self._above = list(deck_above_step3)  # index 0 is the top of the deck
        self._below = list(deck_below_step3)
        self._shuffle = shuffle
        self._step3_drawn = False  # the Step 3 card was drawn
        self._step3_started = False
        self._rebalance(None)

    # ---------- state ----------
    @property
    def current_market(self) -> list[PowerPlant]:
        """Plants that can be bought, ordered by number."""
        return list(self._current)

    @property
    def future_market(self) -> list[PowerPlant]:
        """Plants that will move to the current market (empty in step 3)."""
        return list(self._future)

    @property
    def deck_above_step3(self) -> list[PowerPlant]:
        """Cards above the Step 3 card (the top is first)."""
        return list(self._above)

    @property
    def deck_below_step3(self) -> list[PowerPlant]:
        """Cards below the Step 3 card."""
        return list(self._below)

    @property
    def is_step3(self) -> bool:
        """True after start_step3."""
        return self._step3_started

    def is_step3_start(self) -> bool:
        """True if the Step 3 card was drawn but step 3 has not started yet."""
        return self._step3_drawn and not self._step3_started

    # ---------- auction ----------
    def minimum_bid(self, ppn: PowerPlantNumber) -> int:
        """Plant number, but 1 for the discounted (lowest) plant."""
        plant = self._find_current(ppn)
        if plant is None:
            raise ValueError(f"Power plant {ppn.number} is not in the current market")
        if self.is_first_power_plant_discounted and plant.number == self._current[0].number:
            return 1
        return plant.number

    def can_take_power_plant(self, ppn: PowerPlantNumber, price: int) -> Optional[RequestError]:
        """None if the plant may be bought for `price`."""
        if self._find_current(ppn) is None:
            return RequestError(f"Power plant {ppn.number} is not in the current market")
        minimum = self.minimum_bid(ppn)
        if price < minimum:
            return RequestError(f"The minimum bid is {minimum}")
        return None

    def take_power_plant(self, ppn: PowerPlantNumber) -> PowerPlant:
        """Removes the plant from the current market and refills the markets."""
        plant = self._find_current(ppn)
        if plant is None:
            raise ValueError(f"Power plant {ppn.number} is not in the current market")
        if self.is_first_power_plant_discounted and plant.number == self._current[0].number:
            self.is_first_power_plant_discounted = False
        self._current.remove(plant)
        self._rebalance(self._draw())
        return plant

    def remove_discounted_power_plant(self) -> None:
        """If the discounted (lowest) plant was not bought, it leaves the game."""
        if not self.is_first_power_plant_discounted or not self._current:
            return
        self.is_first_power_plant_discounted = False
        self._current.pop(0)
        self._rebalance(self._draw())

    # ---------- between phases and rounds ----------
    def remove_power_plants_cheaper_than(self, value: int) -> None:
        """Removes every plant of the current market with a number below `value`."""
        while self._current and self._current[0].number < value:
            self._current.pop(0)
            self._rebalance(self._draw())

    def prepare_next_turn(self) -> None:
        """End of a round: steps 1-2 move the highest future plant under the deck,
        step 3 removes the lowest plant. The market is refilled and the discount returns."""
        if self._step3_started:
            if self._current:
                self._current.pop(0)
        elif self._future:
            self._below.append(self._future.pop())
        self._rebalance(self._draw())
        self.is_first_power_plant_discounted = True

    def start_step3(self) -> None:
        """Removes the lowest plant; all remaining plants form one market."""
        if not self._step3_drawn:
            raise ValueError("The Step 3 card has not been drawn")
        if self._step3_started:
            return
        self._step3_started = True
        plants = sorted(self._current + self._future, key=_number)
        if plants:
            plants.pop(0)
        self._current = plants
        self._future = []

    # ---------- internals ----------
    def _find_current(self, ppn: PowerPlantNumber) -> Optional[PowerPlant]:
        return next((p for p in self._current if p.number == ppn.number), None)

    def _draw(self) -> Optional[PowerPlant]:
        """Next plant of the deck; None if the Step 3 card or nothing is drawn."""
        if self._above:
            return self._above.pop(0)
        if not self._step3_drawn:
            self._step3_drawn = True
            self._shuffle(self._below)
            return None
        if self._below:
            return self._below.pop(0)
        return None

    def _rebalance(self, extra: Optional[PowerPlant]) -> None:
        plants = self._current + self._future
        if extra is not None:
            plants.append(extra)
        plants.sort(key=_number)
        if self._step3_started:
            self._current, self._future = plants, []
        else:
            self._current, self._future = plants[:MARKET_SIZE], plants[MARKET_SIZE:]
