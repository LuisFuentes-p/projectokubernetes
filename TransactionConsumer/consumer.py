from kafka import KafkaConsumer
import json
import psycopg2
import time

from consumer_logic import prepare_record


def create_consumer(topic, group):
    for _ in range(10):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers='kafka:9092',
                group_id=group,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
        except Exception:
            time.sleep(5)
    raise RuntimeError(f"Unable to connect to Kafka for {topic}")


def main():
    consumer = create_consumer('transactions_processed', 'db-consumer-group')

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

    for msg in consumer:
        record = prepare_record(msg.value)
        cursor.execute(
            "INSERT INTO transactions (id, commodity, quantity, price, total, tx_type) VALUES (%s, %s, %s, %s, %s, %s)",
            record
        )
        conn.commit()
        print("Inserted:", record)


if __name__ == "__main__":
    main()