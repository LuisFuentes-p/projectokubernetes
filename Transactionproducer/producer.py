from kafka import KafkaProducer
import json
import time
import random

producer = None

for _ in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        break
    except Exception:
        time.sleep(5)

if producer is None:
    raise RuntimeError("Unable to connect to Kafka after multiple retries")

commodities = ["gold", "silver", "oil"]

while True:
    transaction = {
        "id": random.randint(1, 100000),
        "commodity": random.choice(commodities),
        "quantity": round(random.uniform(1, 10), 2)
    }

    producer.send("transactions", transaction)
    print("Produced:", transaction)

    time.sleep(0.5)