from kafka import KafkaProducer
import json
import time

from producer_logic import load_commodities, generate_transaction


def create_producer():
    for _ in range(10):
        try:
            return KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except Exception:
            time.sleep(5)
    raise RuntimeError("Unable to connect to Kafka after multiple retries")


def main():
    producer = create_producer()
    commodities = load_commodities()

    while True:
        transaction = generate_transaction(commodities)
        producer.send("transactions", key=transaction["commodity"], value=transaction)
        print("Produced:", transaction)
        time.sleep(0.5)


if __name__ == "__main__":
    main()