import random


def load_commodities(file_path="commodities.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]

    if not items:
        raise RuntimeError("No commodities configured in commodities.txt")

    return items


def generate_transaction(commodities, random_int=None, random_choice_func=None, random_uniform=None):
    id_source = random_int if random_int is not None else random.randint
    choice_source = random_choice_func if random_choice_func is not None else random.choice
    uniform_source = random_uniform if random_uniform is not None else random.uniform

    return {
        "id": id_source(1, 100000),
        "commodity": choice_source(commodities),
        "quantity": round(uniform_source(1, 10), 2),
        "type": choice_source(["buy", "sell"])
    }
