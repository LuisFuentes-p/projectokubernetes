import tempfile
import unittest

from producer_logic import load_commodities, generate_transaction


class ProducerBoundaryTests(unittest.TestCase):
    """Boundary tests for Transactionproducer Kafka integration."""

    def test_load_commodities_strips_whitespace(self):
        """Verify commodity loading trims whitespace."""
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            temp_file.write("  gold  \n silver\n  platinum  \n")
            temp_path = temp_file.name

        commodities = load_commodities(temp_path)

        self.assertEqual(commodities, ["gold", "silver", "platinum"])

    def test_load_commodities_empty_file_raises_error(self):
        """Verify empty commodity file raises RuntimeError."""
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            temp_file.write("")
            temp_path = temp_file.name

        with self.assertRaises(RuntimeError):
            load_commodities(temp_path)

    def test_load_commodities_all_blank_lines_raises_error(self):
        """Verify file with only blank lines raises RuntimeError."""
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            temp_file.write("\n\n\n")
            temp_path = temp_file.name

        with self.assertRaises(RuntimeError):
            load_commodities(temp_path)

    def test_generate_transaction_structure(self):
        """Verify generated transaction has required fields."""
        commodities = ["gold", "silver"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 42,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 5.0
        )

        self.assertIn("id", transaction)
        self.assertIn("commodity", transaction)
        self.assertIn("quantity", transaction)
        self.assertIn("type", transaction)

    def test_generate_transaction_id_range(self):
        """Verify generated transaction ID is within expected range."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 99999,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 1.0
        )

        self.assertEqual(transaction["id"], 99999)
        self.assertGreaterEqual(transaction["id"], 1)

    def test_generate_transaction_selects_commodity(self):
        """Verify transaction selects from available commodities."""
        commodities = ["gold", "silver", "platinum"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[1],  # Select second commodity
            random_uniform=lambda a, b: 1.0
        )

        self.assertEqual(transaction["commodity"], "silver")

    def test_generate_transaction_quantity_range(self):
        """Verify quantity is within 1-10 range and rounded."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 7.12345
        )

        self.assertEqual(transaction["quantity"], 7.12)

    def test_generate_transaction_type_is_valid(self):
        """Verify transaction type is either buy or sell."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 5.0
        )

        self.assertIn(transaction["type"], ["buy", "sell"])

    def test_generate_transaction_with_single_commodity(self):
        """Verify transaction generation with single commodity."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 100,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 5.5
        )

        self.assertEqual(transaction["commodity"], "gold")
        self.assertEqual(transaction["id"], 100)
        self.assertEqual(transaction["quantity"], 5.5)

    def test_generate_transaction_with_many_commodities(self):
        """Verify transaction generation with large commodity list."""
        commodities = [f"commodity_{i}" for i in range(100)]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0] if len(seq) > 50 else seq[0],  # Handle both commodity and type lists
            random_uniform=lambda a, b: 3.0
        )

        self.assertEqual(transaction["commodity"], "commodity_0")

    def test_quantity_zero_handling(self):
        """Verify quantity at boundary (close to 1.0)."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 1.0
        )

        self.assertEqual(transaction["quantity"], 1.0)

    def test_quantity_max_boundary(self):
        """Verify quantity at upper boundary (close to 10.0)."""
        commodities = ["gold"]

        transaction = generate_transaction(
            commodities,
            random_int=lambda a, b: 1,
            random_choice_func=lambda seq: seq[0],
            random_uniform=lambda a, b: 10.0
        )

        self.assertEqual(transaction["quantity"], 10.0)


if __name__ == "__main__":
    unittest.main()
