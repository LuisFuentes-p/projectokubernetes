import unittest

from consumer_logic import prepare_record


class ConsumerBoundaryTests(unittest.TestCase):
    """Boundary tests for TransactionConsumer Kafka/Postgres integration."""

    def test_prepare_record_from_kafka_message(self):
        """Verify record preparation from a Kafka message."""
        kafka_message = {
            "id": 1,
            "commodity": "gold",
            "quantity": 2.5,
            "price": 70.0,
            "total": 175.0,
            "type": "buy"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[0], 1)  # id
        self.assertEqual(record[1], "gold")  # commodity
        self.assertEqual(record[2], -2.5)  # signed_quantity (buy = negative)
        self.assertEqual(record[3], 70.0)  # price
        self.assertEqual(record[4], 175.0)  # total
        self.assertEqual(record[5], "buy")  # type

    def test_sell_transaction_keeps_positive_quantity(self):
        """Verify sell transactions maintain positive quantity."""
        kafka_message = {
            "id": 2,
            "commodity": "silver",
            "quantity": 3.0,
            "price": 25.0,
            "total": 75.0,
            "type": "sell"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[2], 3.0)  # signed_quantity (sell = positive)

    def test_buy_with_negative_quantity_stays_negative(self):
        """Verify buy with negative quantity is negated to negative."""
        kafka_message = {
            "id": 3,
            "commodity": "gold",
            "quantity": -5.0,
            "price": 70.0,
            "total": -350.0,
            "type": "buy"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[2], -5.0)  # Already negative, abs(-5) = 5, negated = -5

    def test_sell_with_negative_quantity_becomes_positive(self):
        """Verify sell with negative quantity is converted to positive."""
        kafka_message = {
            "id": 4,
            "commodity": "oil",
            "quantity": -2.0,
            "price": 80.0,
            "total": -160.0,
            "type": "sell"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[2], 2.0)  # abs(-2) = 2, positive for sell

    def test_type_case_insensitivity(self):
        """Verify transaction type is lowercased."""
        kafka_message = {
            "id": 5,
            "commodity": "gold",
            "quantity": 1.0,
            "price": 70.0,
            "total": 70.0,
            "type": "SELL"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[5], "sell")

    def test_missing_type_defaults_to_buy(self):
        """Verify missing type field defaults to 'buy'."""
        kafka_message = {
            "id": 6,
            "commodity": "gold",
            "quantity": 1.0,
            "price": 70.0,
            "total": 70.0
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[5], "buy")

    def test_zero_quantity(self):
        """Verify zero quantity is handled correctly."""
        kafka_message = {
            "id": 7,
            "commodity": "gold",
            "quantity": 0,
            "price": 70.0,
            "total": 0,
            "type": "buy"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[2], 0)  # abs(0) = 0, negated = 0

    def test_record_tuple_structure_matches_sql(self):
        """Verify record tuple structure matches SQL INSERT statement."""
        kafka_message = {
            "id": 8,
            "commodity": "copper",
            "quantity": 1.5,
            "price": 22.0,
            "total": 33.0,
            "type": "buy"
        }

        record = prepare_record(kafka_message)

        # Verify tuple has 6 elements for SQL: (id, commodity, quantity, price, total, tx_type)
        self.assertEqual(len(record), 6)
        self.assertIsInstance(record, tuple)

    def test_large_quantity_values(self):
        """Verify large quantity values are handled correctly."""
        kafka_message = {
            "id": 9,
            "commodity": "gold",
            "quantity": 10000.5,
            "price": 70.0,
            "total": 700035.0,
            "type": "sell"
        }

        record = prepare_record(kafka_message)

        self.assertEqual(record[2], 10000.5)


if __name__ == "__main__":
    unittest.main()
