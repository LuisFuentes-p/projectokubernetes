from kafka import KafkaConsumer
import json
import psycopg2
import time

# --- Kafka consumer ---
consumer = None

for _ in range(10):
    try:
        consumer = KafkaConsumer(
            'transactions_processed',
            bootstrap_servers='kafka:9092',
            group_id='db-consumer-group',
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER,
    commodity TEXT,
    quantity REAL,
    price REAL,
    total REAL,
    tx_type TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

print("DB Consumer started...")

# --- Consume and insert ---
for msg in consumer:
    tx = msg.value

    tx_type = str(tx.get("type", "buy")).lower()
    quantity = tx.get("quantity", 0)
    if tx_type == "buy":
        signed_quantity = -abs(quantity)
    else:
        signed_quantity = abs(quantity)

    record = (
        tx.get("id"),
        tx.get("commodity"),
        signed_quantity,
        tx.get("price"),
        tx.get("total"),
        tx_type
    )

    cursor.execute(
        "INSERT INTO transactions (id, commodity, quantity, price, total, tx_type) VALUES (%s, %s, %s, %s, %s, %s)",
        record
    )
    conn.commit()

    print("Inserted:", record)