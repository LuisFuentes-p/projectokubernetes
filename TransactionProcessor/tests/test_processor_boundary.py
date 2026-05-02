import unittest

from processor_logic import enrich_transaction, update_price_table


class ProcessorBoundaryTests(unittest.TestCase):
    """Boundary tests for TransactionProcessor Kafka integration."""

    def test_enrich_transaction_from_kafka_message(self):
        """Verify enrichment of a valid Kafka message."""
        price_table = {"gold": 70.5}
        kafka_message = {
            "id": 1001,
            "commodity": "gold",
            "quantity": 2.5,
            "type": "buy"
        }

        result = enrich_transaction(kafka_message, price_table)

        self.assertEqual(result["id"], 1001)
        self.assertEqual(result["commodity"], "gold")
        self.assertEqual(result["quantity"], 2.5)
        self.assertEqual(result["price"], 70.5)
        self.assertEqual(result["total"], 2.5 * 70.5)

    def test_missing_price_in_table_defaults_to_zero(self):
        """Verify that missing commodity prices default to 0."""
        price_table = {}
        kafka_message = {
            "id": 1002,
            "commodity": "unknown_commodity",
            "quantity": 1.0,
            "type": "sell"
        }

        result = enrich_transaction(kafka_message, price_table)

        self.assertEqual(result["price"], 0)
        self.assertEqual(result["total"], 0)

    def test_invalid_transaction_type_normalized_to_buy(self):
        """Verify that invalid types are normalized to 'buy'."""
        price_table = {"gold": 70.0}
        kafka_message = {
            "id": 1003,
            "commodity": "gold",
            "quantity": 1.0,
            "type": "hold"
        }

        result = enrich_transaction(kafka_message, price_table)

        self.assertEqual(result["type"], "buy")

    def test_case_insensitive_type_handling(self):
        """Verify that transaction types are case-insensitive."""
        price_table = {"gold": 70.0}
        kafka_message = {
            "id": 1004,
            "commodity": "gold",
            "quantity": 1.0,
            "type": "SELL"
        }

        result = enrich_transaction(kafka_message, price_table)

        self.assertEqual(result["type"], "sell")

    def test_price_table_update_from_price_event(self):
        """Verify price table updates from Kafka price events."""
        price_table = {"gold": 70.0}
        price_event = {"commodity": "gold", "price": 71.5}

        update_price_table(price_table, price_event)

        self.assertEqual(price_table["gold"], 71.5)

    def test_price_table_add_new_commodity(self):
        """Verify new commodities are added to price table."""
        price_table = {}
        price_event = {"commodity": "silver", "price": 25.0}

        update_price_table(price_table, price_event)

        self.assertEqual(price_table["silver"], 25.0)

    def test_price_table_ignores_malformed_event(self):
        """Verify malformed price events are safely ignored."""
        price_table = {"gold": 70.0}
        malformed_event = {"commodity": "gold"}  # Missing price

        update_price_table(price_table, malformed_event)

        # Price table should remain unchanged
        self.assertEqual(price_table["gold"], 70.0)

    def test_multiple_transactions_accumulate(self):
        """Verify multiple transactions can be enriched in sequence."""
        price_table = {"gold": 70.0, "silver": 25.0}

        tx1 = {"id": 1, "commodity": "gold", "quantity": 2.0, "type": "buy"}
        tx2 = {"id": 2, "commodity": "silver", "quantity": 3.0, "type": "sell"}

        result1 = enrich_transaction(tx1, price_table)
        result2 = enrich_transaction(tx2, price_table)

        self.assertEqual(result1["total"], 140.0)
        self.assertEqual(result2["total"], 75.0)

    def test_price_table_concurrent_updates(self):
        """Verify price table updates don't interfere with enrichment."""
        price_table = {"gold": 70.0}

        # Enrich with current price
        tx = {"id": 1, "commodity": "gold", "quantity": 1.0, "type": "buy"}
        result1 = enrich_transaction(tx, price_table)

        # Update price in table
        update_price_table(price_table, {"commodity": "gold", "price": 75.0})

        # Enrich with new price
        result2 = enrich_transaction(tx, price_table)

        self.assertEqual(result1["price"], 70.0)
        self.assertEqual(result2["price"], 75.0)


if __name__ == "__main__":
    unittest.main()
