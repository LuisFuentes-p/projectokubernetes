from kafka import KafkaConsumer, KafkaProducer
import json
import time
import os

from pricing_logic import initialize_state, load_commodities, process_transaction


def create_consumer(topic, group):
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    for _ in range(10):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=kafka_bootstrap,
                group_id=group,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
        except Exception:
            time.sleep(5)
    raise RuntimeError(f"Unable to connect to Kafka for {topic}")


def main():
    consumer = create_consumer('transactions', 'pricing-service')
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

    known_commodities = set(load_commodities())
    state = initialize_state(known_commodities)

    print("Pricing Service started...")

    for msg in consumer:
        price_event = process_transaction(msg.value, state)
        if price_event is None:
            continue

        producer.send('prices', key=price_event["commodity"], value=price_event)
        print("Updated price:", price_event)


if __name__ == "__main__":
    main()