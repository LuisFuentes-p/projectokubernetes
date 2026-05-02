import unittest

from consumer_logic import prepare_record


class ConsumerLogicTests(unittest.TestCase):
    def test_prepare_record_buy_transaction_negates_quantity(self):
        transaction = {
            "id": 1,
            "commodity": "gold",
            "quantity": 2.5,
            "price": 70.0,
            "total": 175.0,
            "type": "buy"
        }

        record = prepare_record(transaction)

        self.assertEqual(record, (1, "gold", -2.5, 70.0, 175.0, "buy"))

    def test_prepare_record_sell_transaction_keeps_positive_quantity(self):
        transaction = {
            "id": 2,
            "commodity": "silver",
            "quantity": 3.0,
            "price": 25.0,
            "total": 75.0,
            "type": "sell"
        }

        record = prepare_record(transaction)

        self.assertEqual(record, (2, "silver", 3.0, 25.0, 75.0, "sell"))

    def test_prepare_record_handles_negative_quantity_for_buy(self):
        transaction = {
            "id": 3,
            "commodity": "gold",
            "quantity": -5.0,
            "price": 70.0,
            "total": -350.0,
            "type": "buy"
        }

        record = prepare_record(transaction)

        self.assertEqual(record[2], -5.0)

    def test_prepare_record_normalizes_type_case(self):
        transaction = {
            "id": 4,
            "commodity": "gold",
            "quantity": 1.0,
            "price": 70.0,
            "total": 70.0,
            "type": "SELL"
        }

        record = prepare_record(transaction)

        self.assertEqual(record[5], "sell")


if __name__ == "__main__":
    unittest.main()
