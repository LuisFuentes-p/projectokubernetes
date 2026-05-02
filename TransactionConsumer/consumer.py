from kafka import KafkaConsumer
import json
import psycopg2
import time

consumer = None

for _ in range(10):
    try:
        consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers='kafka:9092',
            group_id='transactions-group',
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        break
    except Exception:
        time.sleep(5)

if consumer is None:
    raise RuntimeError("Unable to connect to Kafka after multiple retries")


# Postgres setup
conn = psycopg2.connect(
    host="postgres",
    database="transactions_db",
    user="user",
    password="password"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER,
    commodity TEXT,
    quantity REAL,
    price REAL,
    total REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        "INSERT INTO transactions (id, commodity, quantity, price, total) VALUES (%s, %s, %s, %s, %s)",
        enriched
    )
    conn.commit()

    print("Consumed + Enriched:", enriched)