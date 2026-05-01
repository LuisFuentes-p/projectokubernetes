from kafka import KafkaConsumer
import json
import sqlite3
import time

consumer = None

for _ in range(10):
    try:
        consumer = KafkaConsumer(
            "transactions",
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        break
    except Exception:
        time.sleep(5)

if consumer is None:
    raise RuntimeError("Unable to connect to Kafka after multiple retries")

# SQLite setup
conn = sqlite3.connect("/data/transactions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER,
    commodity TEXT,
    quantity REAL,
    price REAL,
    total REAL
)
""")
conn.commit()

commodity_prices = {
    "gold": 70.0,
    "silver": 25.0,
    "oil": 80.0
}

for msg in consumer:
    tx = msg.value

    price = commodity_prices.get(tx["commodity"], 0)
    total = tx["quantity"] * price

    enriched = (
        tx["id"],
        tx["commodity"],
        tx["quantity"],
        price,
        total
    )

    cursor.execute(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?)",
        enriched
    )
    conn.commit()

    print("Consumed + Enriched:", enriched)