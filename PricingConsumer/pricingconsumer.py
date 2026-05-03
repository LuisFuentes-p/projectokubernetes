from kafka import KafkaConsumer
import json
import psycopg2
import time
import os

# --- Kafka Consumer ---
kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
consumer = None
for _ in range(10):
    try:
        consumer = KafkaConsumer(
            'prices',
            bootstrap_servers=kafka_bootstrap,
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
# Read DB credentials from environment (Kubernetes secret) with Docker Compose defaults
db_host = os.getenv('host', 'postgres')
db_port = os.getenv('port', '5432')
db_name = os.getenv('dbname', 'transactions_db')
db_user = os.getenv('user', 'user')
db_password = os.getenv('password', 'password')

conn = psycopg2.connect(
    host=db_host,
    port=int(db_port),
    database=db_name,
    user=db_user,
    password=db_password
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