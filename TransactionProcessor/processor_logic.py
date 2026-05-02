def enrich_transaction(transaction, price_table):
    commodity = transaction.get("commodity")
    quantity = transaction.get("quantity", 0)
    tx_type = str(transaction.get("type", "buy")).lower()

    if tx_type not in ("buy", "sell"):
        tx_type = "buy"

    price = price_table.get(commodity, 0)
    total = quantity * price

    return {
        "id": transaction["id"],
        "commodity": commodity,
        "quantity": quantity,
        "type": tx_type,
        "price": price,
        "total": total
    }


def update_price_table(price_table, price_event):
    commodity = price_event.get("commodity")
    price = price_event.get("price")
    if commodity and price is not None:
        price_table[commodity] = price
