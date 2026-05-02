from kafka import KafkaConsumer, KafkaProducer
import json
import time
import random

# --- Kafka Consumer ---
consumer = None
for _ in range(10):
    try:
        consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers='kafka:9092',
            group_id='pricing-service',
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        break
    except Exception:
        time.sleep(5)

if consumer is None:
    raise RuntimeError("Unable to connect to Kafka")

# --- Kafka Producer ---
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)


def load_commodities(file_path="commodities.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    if not items:
        raise RuntimeError("No commodities configured in commodities.txt")
    return items

# --- State (aggregation) ---
aggregates = {}
known_commodities = set(load_commodities())

# Base prices per commodity (fallback is used if a new commodity is added)
default_base_prices = {
    "gold": 70.0,
    "silver": 25.0,
    "platinum": 45.0,
    "oil": 80.0,
    "natural_gas": 35.0,
    "wheat": 12.0,
    "corn": 9.0,
    "coffee": 18.0,
    "copper": 22.0,
    "aluminum": 15.0,
}
base_prices = {commodity: default_base_prices.get(commodity, 10.0) for commodity in known_commodities}
price_sensitivity = 0.05

# Per-commodity volatility (standard deviation for random shock)
volatility = {
    "gold": 0.6,
    "silver": 0.8,
    "platinum": 1.0,
    "oil": 1.5,
    "natural_gas": 2.0,
    "wheat": 0.5,
    "corn": 0.4,
    "coffee": 0.9,
    "copper": 0.7,
    "aluminum": 0.6,
}

# Track last traded price per commodity to support smooth, dynamic evolution
last_prices = {commodity: base_prices.get(commodity, 10.0) for commodity in known_commodities}
mean_reversion_strength = 0.05

print("Pricing Service started...")

for msg in consumer:
    tx = msg.value
    commodity = tx.get("commodity")
    quantity = tx.get("quantity", 0)
    tx_type = str(tx.get("type", "buy")).lower()

    if commodity not in known_commodities:
        print(f"Skipping transaction for unknown commodity: {tx}")
        continue

    if tx_type not in ("buy", "sell"):
        print(f"Skipping transaction with invalid type: {tx}")
        continue

    # Initialize state per commodity
    if commodity not in aggregates:
        aggregates[commodity] = {
            "buy_volume": 0,
            "sell_volume": 0
        }

    # Update buy/sell volumes
    if tx_type == "buy":
        aggregates[commodity]["buy_volume"] += quantity
    elif tx_type == "sell":
        aggregates[commodity]["sell_volume"] += quantity

    buy = aggregates[commodity]["buy_volume"]
    sell = aggregates[commodity]["sell_volume"]

    imbalance = buy - sell

    base_price = base_prices.get(commodity, 10.0)
    last_price = last_prices.get(commodity, base_price)

    # Price dynamics = mean reversion + order-flow pressure + random market shock
    mean_reversion = mean_reversion_strength * (base_price - last_price)
    order_flow_move = imbalance * price_sensitivity
    noise = random.gauss(0, 1) * volatility.get(commodity, 0.5)

    # price increases if demand > supply, decreases otherwise
    new_price = max(0.01, last_price + mean_reversion + order_flow_move + noise)
    last_prices[commodity] = new_price

    price_event = {
        "commodity": commodity,
        "price": round(new_price, 2)
    }

    # Send updated price with partition key (commodity)
    producer.send('prices', key=commodity, value=price_event)

    print("Updated price:", price_event)