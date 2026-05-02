from kafka import KafkaConsumer
import json
import psycopg2
import time

# --- Kafka Consumer ---
consumer = None
for _ in range(10):
    try:
        consumer = KafkaConsumer(
            'prices',
            bootstrap_servers='kafka:9092',
            group_id='price-db-consumer',
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        break
    except Exception:
        time.sleep(5)

if consumer is None:
    raise RuntimeError("Unable to connect to Kafka")

# --- Postgres ---
conn = psycopg2.connect(
    host="postgres",
    database="transactions_db",
    user="user",
    password="password"
)
cursor = conn.cursor()

# Table for latest prices
cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    commodity TEXT PRIMARY KEY,
    price REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

print("Price DB Consumer started...")

for msg in consumer:
    price_event = msg.value

    commodity = price_event["commodity"]
    price = price_event["price"]

    # Upsert (insert or update)
    cursor.execute("""
        INSERT INTO prices (commodity, price)
        VALUES (%s, %s)
        ON CONFLICT (commodity)
        DO UPDATE SET price = EXCLUDED.price,
                      updated_at = CURRENT_TIMESTAMP
    """, (commodity, price))

    conn.commit()

    print("Price stored:", commodity, price)