from kafka import KafkaConsumer, KafkaProducer
import json
import time
import os

from processor_logic import enrich_transaction, update_price_table


def create_consumer(topic, group):
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    for _ in range(10):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=kafka_bootstrap,
                group_id=group,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
        except Exception:
            time.sleep(5)
    raise RuntimeError(f"Unable to connect to Kafka for {topic}")


def main():
    transactions_consumer = create_consumer('transactions', 'transaction-processor')
    prices_consumer = create_consumer('prices', 'transaction-processor-prices')
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

    price_table = {}

    print("Processor started...")

    for msg in prices_consumer:
        update_price_table(price_table, msg.value)
        if len(price_table) > 0:
            break

    for msg in transactions_consumer:
        enriched = enrich_transaction(msg.value, price_table)
        if enriched is None:
            continue

        producer.send('transactions_processed', key=enriched["commodity"], value=enriched)
        print("Processed:", enriched)

        price_msgs = prices_consumer.poll(timeout_ms=10)
        for tp, messages in price_msgs.items():
            for m in messages:
                update_price_table(price_table, m.value)


if __name__ == "__main__":
    main()