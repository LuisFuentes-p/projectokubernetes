from kafka import KafkaProducer
import json
import time
import random

producer = None

for _ in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        break
    except Exception:
        time.sleep(5)

if producer is None:
    raise RuntimeError("Unable to connect to Kafka after multiple retries")


def load_commodities(file_path="commodities.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    if not items:
        raise RuntimeError("No commodities configured in commodities.txt")
    return items


commodities = load_commodities()

while True:
    transaction = {
        "id": random.randint(1, 100000),
        "commodity": random.choice(commodities),
        "quantity": round(random.uniform(1, 10), 2),
        # transaction type: buy or sell
        "type": random.choice(["buy", "sell"]) 
    }

    # Send with partition key (commodity) to ensure all transactions for same commodity go to same partition
    producer.send("transactions", key=transaction["commodity"], value=transaction)
    print("Produced:", transaction)

    time.sleep(0.5)