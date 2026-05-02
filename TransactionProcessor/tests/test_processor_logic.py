import unittest

from processor_logic import enrich_transaction, update_price_table


class ProcessorLogicTests(unittest.TestCase):
    def test_enrich_transaction_with_valid_price(self):
        price_table = {"gold": 70.5}
        transaction = {
            "id": 1,
            "commodity": "gold",
            "quantity": 2.5,
            "type": "buy"
        }

        result = enrich_transaction(transaction, price_table)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["commodity"], "gold")
        self.assertEqual(result["quantity"], 2.5)
        self.assertEqual(result["price"], 70.5)
        self.assertEqual(result["total"], 2.5 * 70.5)
        self.assertEqual(result["type"], "buy")

    def test_enrich_transaction_missing_price_defaults_to_zero(self):
        price_table = {}
        transaction = {
            "id": 2,
            "commodity": "silver",
            "quantity": 3.0,
            "type": "sell"
        }

        result = enrich_transaction(transaction, price_table)

        self.assertEqual(result["price"], 0)
        self.assertEqual(result["total"], 0)

    def test_enrich_transaction_normalizes_invalid_type(self):
        price_table = {"gold": 70.0}
        transaction = {
            "id": 3,
            "commodity": "gold",
            "quantity": 1.0,
            "type": "invalid"
        }

        result = enrich_transaction(transaction, price_table)

        self.assertEqual(result["type"], "buy")

    def test_update_price_table_adds_price(self):
        price_table = {}
        price_event = {"commodity": "gold", "price": 70.5}

        update_price_table(price_table, price_event)

        self.assertEqual(price_table["gold"], 70.5)

    def test_update_price_table_updates_existing_price(self):
        price_table = {"gold": 70.0}
        price_event = {"commodity": "gold", "price": 71.0}

        update_price_table(price_table, price_event)

        self.assertEqual(price_table["gold"], 71.0)


if __name__ == "__main__":
    unittest.main()
