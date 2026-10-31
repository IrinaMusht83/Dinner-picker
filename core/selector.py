from core.models import Recipe, Product, RecipeCost
from core.costing import calculate_cost


def all_available(mains, catalog: list[Product]) -> bool:
    return all(
        any(p.product == ing.product and p.in_stock for p in catalog)
        for ing in mains
    )


def select(
    recipes: list[Recipe],
    catalog: list[Product],
    persons: int,
    budget: float,
    limit: int = 5,
) -> list[RecipeCost]:
    """Строгий фильтр + ранжирование C: (budget - cost) ↑, tie-break по названию."""
    results: list[RecipeCost] = []
    for r in recipes:
        if not all_available(r.mains, catalog):
            continue
        rc = calculate_cost(r.mains, persons, catalog)
        if rc is None:
            continue
        if rc.total_cost <= budget:
            results.append(RecipeCost(
                recipe=r,
                persons=persons,
                total_cost=rc.total_cost,
                items=rc.items,
            ))

    results.sort(key=lambda x: (budget - x.total_cost, x.recipe.name))
    return results[:limit]


def nearest_over_budget(
    recipes: list[Recipe],
    catalog: list[Product],
    persons: int,
    budget: float,
) -> RecipeCost | None:
    """Ближайший по превышению среди доступных (cost > budget)."""
    candidates: list[RecipeCost] = []
    for r in recipes:
        if not all_available(r.mains, catalog):
            continue
        rc = calculate_cost(r.mains, persons, catalog)
        if rc is None:
            continue
        if rc.total_cost > budget:
            candidates.append(RecipeCost(
                recipe=r,
                persons=persons,
                total_cost=rc.total_cost,
                items=rc.items,
            ))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x.total_cost - budget, x.recipe.name))
    return candidates[0]