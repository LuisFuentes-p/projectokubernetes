from kafka import KafkaConsumer, KafkaProducer
import json
import time

# --- Connect consumers ---
def create_consumer(topic, group):
    for _ in range(10):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers='kafka:9092',
                group_id=group,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
        except Exception:
            time.sleep(5)
    raise RuntimeError(f"Unable to connect to Kafka for {topic}")

transactions_consumer = create_consumer('transactions', 'transaction-processor')
prices_consumer = create_consumer('prices', 'transaction-processor-prices')

# --- Producer ---
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

# --- Local state store (price table) ---
price_table = {}

print("Processor started...")

# --- Prime price table first ---
for msg in prices_consumer:
    data = msg.value
    price_table[data["commodity"]] = data["price"]

    # break early once we have some data (optional optimization)
    if len(price_table) > 0:
        break

# --- Main loop ---
for msg in transactions_consumer:
    tx = msg.value

    commodity = tx.get("commodity")
    quantity = tx.get("quantity", 0)
    tx_type = str(tx.get("type", "buy")).lower()
    if tx_type not in ("buy", "sell"):
        tx_type = "buy"

    price = price_table.get(commodity, 0)
    total = quantity * price

    enriched = {
        "id": tx["id"],
        "commodity": commodity,
        "quantity": quantity,
        "type": tx_type,
        "price": price,
        "total": total
    }

    producer.send('transactions_processed', key=commodity, value=enriched)

    print("Processed:", enriched)

    # Non-blocking update of prices (poll)
    price_msgs = prices_consumer.poll(timeout_ms=10)
    for tp, messages in price_msgs.items():
        for m in messages:
            p = m.value
            price_table[p["commodity"]] = p["price"]