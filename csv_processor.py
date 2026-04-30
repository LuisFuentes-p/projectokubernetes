import csv
import random
import statistics
from pathlib import Path
from typing import List, Dict, Optional


class CSVGenerator:
    """Generate random CSV files with sample data."""
    
    def __init__(self, filename: str = "data.csv"):
        """Initialize the CSV generator with a filename."""
        self.filename = filename
        self.data = []
    
    def generate(self, rows: int = 10, columns: List[str] = None) -> None:
        """Generate random data for CSV.
        
        Args:
            rows: Number of rows to generate
            columns: List of column names (default: ['id', 'name', 'score', 'value'])
        """
        if columns is None:
            columns = ['id', 'name', 'score', 'value']
        
        self.columns = columns
        names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
        
        for i in range(rows):
            row = {
                'id': i + 1,
                'name': random.choice(names),
                'score': random.randint(50, 100),
                'value': round(random.uniform(10.0, 100.0), 2)
            }
            self.data.append(row)
    
    def save(self) -> None:
        """Save generated data to CSV file."""
        if not self.data:
            print("No data to save. Call generate() first.")
            return
        
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"✓ CSV file '{self.filename}' created with {len(self.data)} rows")


class CSVAnalyzer:
    """Analyze CSV files and calculate metrics."""
    
    def __init__(self, filename: str):
        """Initialize the analyzer with a CSV filename."""
        self.filename = filename
        self.data = []
        self.columns = []
    
    def load(self) -> bool:
        """Load CSV file into memory.
        
        Returns:
            True if successful, False otherwise
        """
        if not Path(self.filename).exists():
            print(f"Error: File '{self.filename}' not found.")
            return False
        
        try:
            with open(self.filename, 'r') as f:
                reader = csv.DictReader(f)
                self.columns = reader.fieldnames
                self.data = list(reader)
            
            print(f"✓ Loaded '{self.filename}' with {len(self.data)} rows")
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def get_numeric_columns(self) -> List[str]:
        """Identify numeric columns."""
        numeric_cols = []
        for col in self.columns:
            try:
                for row in self.data:
                    float(row[col])
                numeric_cols.append(col)
                break
            except (ValueError, TypeError):
                continue
        return numeric_cols
    
    def calculate_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate metrics for numeric columns.
        
        Returns:
            Dictionary with column metrics (min, max, mean, median, stdev)
        """
        metrics = {}
        numeric_cols = self.get_numeric_columns()
        
        for col in numeric_cols:
            values = [float(row[col]) for row in self.data]
            
            metrics[col] = {
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0
            }
        
        return metrics
    
    def print_summary(self) -> None:
        """Print a summary of the CSV data and metrics."""
        if not self.data:
            print("No data loaded.")
            return
        
        print(f"\n{'='*60}")
        print(f"CSV Summary: {self.filename}")
        print(f"{'='*60}")
        print(f"Total Rows: {len(self.data)}")
        print(f"Columns: {', '.join(self.columns)}")
        
        metrics = self.calculate_metrics()
        
        if metrics:
            print(f"\n{'Metrics':^60}")
            print(f"{'-'*60}")
            for col, stats in metrics.items():
                print(f"\n{col}:")
                for stat_name, value in stats.items():
                    print(f"  {stat_name:>10}: {value:>12.2f}")
        print(f"{'='*60}\n")


def main():
    """Main function to demonstrate the CSV processor."""
    
    print("\n=== CSV Processor Demo ===\n")
    
    # Generate a random CSV
    print("1. Generating random CSV...")
    generator = CSVGenerator("sample_data.csv")
    generator.generate(rows=20)
    generator.save()
    
    # Analyze the generated CSV
    print("\n2. Analyzing the CSV...")
    analyzer = CSVAnalyzer("sample_data.csv")
    
    if analyzer.load():
        analyzer.print_summary()
        
        # Show first few rows
        print("First 5 rows:")
        for i, row in enumerate(analyzer.data[:5], 1):
            print(f"  Row {i}: {row}")


if __name__ == "__main__":
    main()
