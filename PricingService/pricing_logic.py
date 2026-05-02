import random


DEFAULT_BASE_PRICES = {
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

DEFAULT_VOLATILITY = {
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


def load_commodities(file_path="commodities.txt"):
    with open(file_path, "r", encoding="utf-8") as file_handle:
        items = [line.strip() for line in file_handle if line.strip()]

    if not items:
        raise RuntimeError("No commodities configured in commodities.txt")

    return items


def initialize_state(known_commodities):
    base_prices = {
        commodity: DEFAULT_BASE_PRICES.get(commodity, 10.0)
        for commodity in known_commodities
    }

    return {
        "known_commodities": set(known_commodities),
        "aggregates": {},
        "base_prices": base_prices,
        "last_prices": {commodity: base_prices.get(commodity, 10.0) for commodity in known_commodities},
        "price_sensitivity": 0.05,
        "mean_reversion_strength": 0.05,
        "volatility": dict(DEFAULT_VOLATILITY),
    }


def calculate_price(base_price, last_price, imbalance, price_sensitivity, mean_reversion_strength, noise):
    mean_reversion = mean_reversion_strength * (base_price - last_price)
    order_flow_move = imbalance * price_sensitivity
    return max(0.01, last_price + mean_reversion + order_flow_move + noise)


def process_transaction(transaction, state, random_gauss=None):
    commodity = transaction.get("commodity")
    quantity = transaction.get("quantity", 0)
    tx_type = str(transaction.get("type", "buy")).lower()

    if commodity not in state["known_commodities"]:
        return None

    if tx_type not in ("buy", "sell"):
        return None

    aggregates = state["aggregates"]
    if commodity not in aggregates:
        aggregates[commodity] = {"buy_volume": 0, "sell_volume": 0}

    if tx_type == "buy":
        aggregates[commodity]["buy_volume"] += quantity
    else:
        aggregates[commodity]["sell_volume"] += quantity

    buy = aggregates[commodity]["buy_volume"]
    sell = aggregates[commodity]["sell_volume"]
    imbalance = buy - sell

    base_price = state["base_prices"].get(commodity, 10.0)
    last_price = state["last_prices"].get(commodity, base_price)
    noise_source = random_gauss if random_gauss is not None else random.gauss
    noise = noise_source(0, 1) * state["volatility"].get(commodity, 0.5)

    new_price = calculate_price(
        base_price=base_price,
        last_price=last_price,
        imbalance=imbalance,
        price_sensitivity=state["price_sensitivity"],
        mean_reversion_strength=state["mean_reversion_strength"],
        noise=noise,
    )
    state["last_prices"][commodity] = new_price

    return {
        "commodity": commodity,
        "price": round(new_price, 2)
    }