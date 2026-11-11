"""Unit tests of PowerPlantMarket (the shuffle is replaced by a deterministic one)."""
import unittest

from power_grid.power_plant_market import PowerPlantMarket
from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


def plant(number: int) -> PowerPlant:
    """A plant with the given number."""
    return PowerPlant(number, Resource.COAL, 1, 1)


def plants(*plant_numbers: int) -> list[PowerPlant]:
    """Plants with the given numbers."""
    return [plant(n) for n in plant_numbers]


def numbers(cards: list[PowerPlant]) -> list[int]:
    """Numbers of the plants."""
    return [c.number for c in cards]


def reverse_shuffle(cards: list[PowerPlant]) -> None:
    """Deterministic 'shuffle'."""
    cards.reverse()


def ppn(number: int) -> PowerPlantNumber:
    """Shortcut."""
    return PowerPlantNumber(number)


def make(above: tuple[int, ...] = (11, 12), below: tuple[int, ...] = (13, 14)) -> PowerPlantMarket:
    """Markets 3-6 / 7-10 and the given decks."""
    return PowerPlantMarket(plants(3, 4, 5, 6), plants(7, 8, 9, 10), plants(*above),
                            plants(*below), reverse_shuffle)


class TestPowerPlantMarket(unittest.TestCase):
    """Taking plants, discount, refilling, steps."""

    def test_constructor_sorts_and_splits_markets(self) -> None:
        """Eight plants in any order form the current and the future market."""
        market = PowerPlantMarket(plants(9, 3, 10, 4, 8, 5, 7, 6), [], [], [], reverse_shuffle)
        self.assertEqual(numbers(market.current_market), [3, 4, 5, 6])
        self.assertEqual(numbers(market.future_market), [7, 8, 9, 10])

    def test_can_take_checks_market_and_price(self) -> None:
        """Only the current market is for sale and the bid must reach the minimum."""
        market = make()
        self.assertIsInstance(market.can_take_power_plant(ppn(7), 7), RequestError)
        self.assertIsInstance(market.can_take_power_plant(ppn(99), 7), RequestError)
        self.assertIsInstance(market.can_take_power_plant(ppn(5), 4), RequestError)
        self.assertIsNone(market.can_take_power_plant(ppn(5), 5))

    def test_lowest_plant_is_discounted(self) -> None:
        """The lowest plant can be bid for with 1; the others have their number."""
        market = make()
        self.assertEqual(market.minimum_bid(ppn(3)), 1)
        self.assertEqual(market.minimum_bid(ppn(4)), 4)
        self.assertIsNone(market.can_take_power_plant(ppn(3), 1))

    def test_taking_discounted_plant_removes_discount(self) -> None:
        """After that the new lowest plant has its full price."""
        market = make()
        self.assertEqual(market.take_power_plant(ppn(3)).number, 3)
        self.assertFalse(market.is_first_power_plant_discounted)
        self.assertEqual(market.minimum_bid(ppn(4)), 4)

    def test_taking_other_plant_keeps_discount(self) -> None:
        """The discount stays for the lowest plant."""
        market = make()
        market.take_power_plant(ppn(5))
        self.assertTrue(market.is_first_power_plant_discounted)
        self.assertEqual(market.minimum_bid(ppn(3)), 1)

    def test_take_refills_from_the_deck(self) -> None:
        """The new plant goes to the future market and the markets stay sorted."""
        market = make()
        self.assertEqual(market.take_power_plant(ppn(5)).number, 5)
        self.assertEqual(numbers(market.current_market), [3, 4, 6, 7])
        self.assertEqual(numbers(market.future_market), [8, 9, 10, 11])
        self.assertEqual(numbers(market.deck_above_step3), [12])

    def test_take_unknown_plant_raises(self) -> None:
        """The auction checks with can_take_power_plant first."""
        with self.assertRaises(ValueError):
            make().take_power_plant(ppn(7))

    def test_unbought_discounted_plant_is_removed(self) -> None:
        """At the end of the auction the lowest plant leaves the game."""
        market = make()
        market.remove_discounted_power_plant()
        self.assertEqual(numbers(market.current_market), [4, 5, 6, 7])
        self.assertEqual(numbers(market.future_market), [8, 9, 10, 11])
        market.remove_discounted_power_plant()  # nothing more to remove
        self.assertEqual(numbers(market.current_market), [4, 5, 6, 7])

    def test_bought_discounted_plant_is_not_removed_again(self) -> None:
        """If the discounted plant was bought, nothing else is removed."""
        market = make()
        market.take_power_plant(ppn(3))
        market.remove_discounted_power_plant()
        self.assertEqual(numbers(market.current_market), [4, 5, 6, 7])

    def test_step3_card_is_drawn_when_deck_above_is_empty(self) -> None:
        """No plant is added, the deck below is shuffled and step 3 is waiting."""
        market = make(above=())
        market.take_power_plant(ppn(3))
        self.assertTrue(market.is_step3_start())
        self.assertFalse(market.is_step3)
        self.assertEqual(numbers(market.current_market), [4, 5, 6, 7])
        self.assertEqual(numbers(market.future_market), [8, 9, 10])
        self.assertEqual(numbers(market.deck_below_step3), [14, 13])

    def test_start_step3_removes_lowest_and_joins_markets(self) -> None:
        """Six plants form one market without the future market."""
        market = make(above=())
        market.take_power_plant(ppn(3))
        market.start_step3()
        self.assertTrue(market.is_step3)
        self.assertFalse(market.is_step3_start())
        self.assertEqual(numbers(market.current_market), [5, 6, 7, 8, 9, 10])
        self.assertEqual(market.future_market, [])

    def test_start_step3_without_step3_card_raises(self) -> None:
        """Step 3 cannot start before the card is drawn."""
        with self.assertRaises(ValueError):
            make().start_step3()

    def test_take_in_step3_refills_the_single_market(self) -> None:
        """The market keeps six plants while the deck lasts."""
        market = make(above=())
        market.take_power_plant(ppn(3))
        market.start_step3()
        market.take_power_plant(ppn(7))
        self.assertEqual(numbers(market.current_market), [5, 6, 8, 9, 10, 14])

    def test_remove_plants_cheaper_than(self) -> None:
        """Plants are replaced until the lowest one is not cheaper than the value."""
        market = make()
        market.remove_power_plants_cheaper_than(6)
        self.assertEqual(numbers(market.current_market), [6, 7, 8, 9])
        self.assertEqual(numbers(market.future_market), [10, 11, 12])
        self.assertTrue(market.is_step3_start())

    def test_prepare_next_turn_in_steps_1_and_2(self) -> None:
        """The highest future plant goes under the deck, a new one is drawn."""
        market = make()
        market.take_power_plant(ppn(3))
        market.prepare_next_turn()
        self.assertEqual(numbers(market.current_market), [4, 5, 6, 7])
        self.assertEqual(numbers(market.future_market), [8, 9, 10, 12])
        self.assertEqual(numbers(market.deck_below_step3), [13, 14, 11])
        self.assertTrue(market.is_first_power_plant_discounted)

    def test_prepare_next_turn_in_step3(self) -> None:
        """The lowest plant leaves the game and the market is refilled."""
        market = make(above=())
        market.take_power_plant(ppn(3))
        market.start_step3()
        market.prepare_next_turn()
        self.assertEqual(numbers(market.current_market), [6, 7, 8, 9, 10, 14])
        self.assertTrue(market.is_first_power_plant_discounted)


if __name__ == "__main__":
    unittest.main()
