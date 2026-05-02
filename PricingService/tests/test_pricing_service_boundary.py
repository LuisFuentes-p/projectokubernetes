import unittest
from unittest.mock import MagicMock, patch, call

from pricing_logic import process_transaction


class PricingServiceBoundaryTests(unittest.TestCase):
    """Boundary tests for PricingService Kafka integration."""

    def test_kafka_message_produces_price_event(self):
        """Verify that a transaction from Kafka produces an enriched price event."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        transaction = {
            "commodity": "gold",
            "quantity": 2.0,
            "type": "buy"
        }

        result = process_transaction(transaction, state, random_gauss=lambda m, s: 0)

        self.assertIsNotNone(result)
        self.assertEqual(result["commodity"], "gold")
        self.assertEqual(result["price"], 70.1)

    def test_kafka_unknown_commodity_skips_production(self):
        """Verify that unknown commodities don't produce price events."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        transaction = {
            "commodity": "unknown",
            "quantity": 2.0,
            "type": "buy"
        }

        result = process_transaction(transaction, state, random_gauss=lambda m, s: 0)

        self.assertIsNone(result)

    def test_kafka_invalid_transaction_type_skips_production(self):
        """Verify that invalid transaction types don't produce price events."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        transaction = {
            "commodity": "gold",
            "quantity": 2.0,
            "type": "invalid_type"
        }

        result = process_transaction(transaction, state, random_gauss=lambda m, s: 0)

        self.assertIsNone(result)

    def test_kafka_malformed_message_gracefully_handled(self):
        """Verify that messages missing fields don't crash the service."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        # Missing 'type' field
        transaction = {
            "commodity": "gold",
            "quantity": 2.0
        }

        try:
            result = process_transaction(transaction, state, random_gauss=lambda m, s: 0)
            # Should not crash; type defaults to 'buy'
            self.assertIsNotNone(result)
        except KeyError:
            self.fail("process_transaction raised KeyError on missing 'type' field")

    def test_state_accumulates_across_messages(self):
        """Verify that aggregates accumulate correctly across multiple Kafka messages."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        # First message: buy 2
        result1 = process_transaction(
            {"commodity": "gold", "quantity": 2.0, "type": "buy"},
            state,
            random_gauss=lambda m, s: 0
        )
        self.assertIsNotNone(result1)
        self.assertEqual(state["aggregates"]["gold"]["buy_volume"], 2.0)

        # Second message: sell 1 (should accumulate)
        result2 = process_transaction(
            {"commodity": "gold", "quantity": 1.0, "type": "sell"},
            state,
            random_gauss=lambda m, s: 0
        )
        self.assertIsNotNone(result2)
        self.assertEqual(state["aggregates"]["gold"]["buy_volume"], 2.0)
        self.assertEqual(state["aggregates"]["gold"]["sell_volume"], 1.0)

    def test_price_updates_on_each_transaction(self):
        """Verify that last_prices is updated after each transaction."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        initial_price = state["last_prices"]["gold"]

        process_transaction(
            {"commodity": "gold", "quantity": 10.0, "type": "buy"},
            state,
            random_gauss=lambda m, s: 0
        )

        # Price should have changed due to order flow imbalance
        updated_price = state["last_prices"]["gold"]
        self.assertNotEqual(initial_price, updated_price)

    def test_kafka_deserialization_simulated(self):
        """Simulate Kafka message deserialization by testing with dict input."""
        state = {
            "known_commodities": {"gold"},
            "aggregates": {},
            "base_prices": {"gold": 70.0},
            "last_prices": {"gold": 70.0},
            "price_sensitivity": 0.05,
            "mean_reversion_strength": 0.05,
            "volatility": {"gold": 0.6},
        }

        # Simulate JSON deserialized message
        kafka_message = {
            "commodity": "gold",
            "quantity": 2.5,
            "type": "buy"
        }

        result = process_transaction(kafka_message, state, random_gauss=lambda m, s: 0)

        self.assertIsNotNone(result)
        self.assertIn("price", result)


if __name__ == "__main__":
    unittest.main()
