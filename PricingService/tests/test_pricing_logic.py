import tempfile
import unittest

from pricing_logic import calculate_price, initialize_state, load_commodities, process_transaction


class PricingLogicTests(unittest.TestCase):
    def test_load_commodities_ignores_blank_lines(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            temp_file.write("gold\n\n silver \n")
            temp_path = temp_file.name

        self.assertEqual(load_commodities(temp_path), ["gold", "silver"])

    def test_calculate_price_applies_floor(self):
        price = calculate_price(
            base_price=10.0,
            last_price=0.5,
            imbalance=-100,
            price_sensitivity=0.05,
            mean_reversion_strength=0.05,
            noise=-10.0,
        )

        self.assertEqual(price, 0.01)

    def test_process_transaction_updates_state_and_returns_event(self):
        state = initialize_state({"gold"})

        event = process_transaction(
            {"commodity": "gold", "quantity": 2, "type": "buy"},
            state,
            random_gauss=lambda mean, stddev: 0,
        )

        self.assertEqual(event, {"commodity": "gold", "price": 70.1})
        self.assertEqual(state["aggregates"]["gold"]["buy_volume"], 2)
        self.assertEqual(state["last_prices"]["gold"], 70.1)

    def test_process_transaction_skips_unknown_commodity(self):
        state = initialize_state({"gold"})

        event = process_transaction(
            {"commodity": "silver", "quantity": 2, "type": "buy"},
            state,
            random_gauss=lambda mean, stddev: 0,
        )

        self.assertIsNone(event)

    def test_process_transaction_skips_invalid_type(self):
        state = initialize_state({"gold"})

        event = process_transaction(
            {"commodity": "gold", "quantity": 2, "type": "hold"},
            state,
            random_gauss=lambda mean, stddev: 0,
        )

        self.assertIsNone(event)


if __name__ == "__main__":
    unittest.main()