def prepare_record(transaction):
    tx_type = str(transaction.get("type", "buy")).lower()
    quantity = transaction.get("quantity", 0)

    if tx_type == "buy":
        signed_quantity = -abs(quantity)
    else:
        signed_quantity = abs(quantity)

    return (
        transaction.get("id"),
        transaction.get("commodity"),
        signed_quantity,
        transaction.get("price"),
        transaction.get("total"),
        tx_type
    )
