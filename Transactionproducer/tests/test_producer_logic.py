import tempfile
import unittest

from producer_logic import generate_transaction, load_commodities


class ProducerLogicTests(unittest.TestCase):
    def test_load_commodities_ignores_blank_lines(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            temp_file.write("gold\n\nsilver\n  platinum  \n")
            temp_path = temp_file.name

        commodities = load_commodities(temp_path)

        self.assertEqual(commodities, ["gold", "silver", "platinum"])

    def test_generate_transaction_includes_all_fields(self):
        commodities = ["gold", "silver"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 42,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 5.0
        )

        self.assertEqual(transaction["id"], 42)
        self.assertEqual(transaction["commodity"], "gold")
        self.assertEqual(transaction["quantity"], 5.0)
        self.assertIn(transaction["type"], ["buy", "sell"])

    def test_generate_transaction_quantity_is_rounded(self):
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 3.14159
        )

        self.assertEqual(transaction["quantity"], 3.14)


if __name__ == "__main__":
    unittest.main()
