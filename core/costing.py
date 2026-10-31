from math import ceil

from core.models import (
    Recipe, Ingredient, Product, ChosenPack, ItemCost, RecipeCost
)


def scale_recipe(recipe: Recipe, persons: int) -> list[tuple[Ingredient, float]]:
    """Возвращает [(ингредиент, нужные_граммы)] для N человек."""
    return [(ing, ing.grams_per_serving * persons) for ing in recipe.ingredients]


def match_products(product_name: str, catalog: list[Product]) -> list[Product]:
    """Точное совпадение product + in_stock."""
    return [p for p in catalog if p.product == product_name and p.in_stock]


def choose_packs(
    needed_grams: float, products: list[Product]
) -> tuple[tuple[ChosenPack, ...], float] | None:
    """Минимум стоимости, tie-break — минимум перерасхода."""
    if not products:
        return None

    candidates: list[tuple[list[tuple[Product, int]], float, float]] = []

    for p in products:
        if p.pack_size >= needed_grams:
            candidates.append(([(p, 1)], p.price, p.pack_size - needed_grams))

    biggest = max(products, key=lambda p: p.pack_size)
    qty = ceil(needed_grams / biggest.pack_size)
    candidates.append(
        ([(biggest, qty)], biggest.price * qty, biggest.pack_size * qty - needed_grams)
    )

    for p in products:
        q = ceil(needed_grams / p.pack_size)
        candidates.append(([(p, q)], p.price * q, p.pack_size * q - needed_grams))

    best_items, best_cost, _ = min(candidates, key=lambda x: (x[1], x[2]))

    packs = tuple(
        ChosenPack(product_id=p.product_id, name=p.name, price=p.price, qty=q)
        for p, q in best_items
    )
    return packs, best_cost


def calculate_cost(
    mains: list[Ingredient],
    persons: int,
    catalog: list[Product],
) -> RecipeCost | None:
    """Стоимость main-ингредиентов под N человек. None, если что-то недоступно."""
    items: list[ItemCost] = []
    total = 0.0
    for ing in mains:
        needed = ing.grams_per_serving * persons
        products = match_products(ing.product, catalog)
        if not products:
            return None
        chosen = choose_packs(needed, products)
        if chosen is None:
            return None
        packs, cost = chosen
        items.append(ItemCost(
            product=ing.product,
            needed_grams=needed,
            chosen_packs=packs,
            cost=cost,
        ))
        total += cost

    return RecipeCost(
        recipe=None,
        persons=persons,
        total_cost=round(total, 2),
        items=tuple(items),
    )