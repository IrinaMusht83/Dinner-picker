"""Смоук: подбор на реальных данных, без Telegram."""
from core.loader import load_recipes, load_catalog
from core.selector import select, nearest_over_budget


def main():
    recipes = load_recipes("data/recipes.json")
    catalog = load_catalog("data/catalog_snapshot.json")

    cases = [
        (2, 800),
        (3, 800),
        (4, 1500),
        (1, 300),
        (5, 3000),
    ]

    for persons, budget in cases:
        print(f"\n=== {persons} чел., бюджет {budget} ₽ ===")
        results = select(recipes, catalog, persons, budget, limit=5)
        if results:
            for rc in results:
                print(f"  {rc.recipe.name:40s} {rc.total_cost:7.0f} ₽  "
                      f"(откл. {budget - rc.total_cost:5.0f})")
        else:
            nearest = nearest_over_budget(recipes, catalog, persons, budget)
            if nearest:
                print(f"  ничего ≤ {budget}; ближайший: {nearest.recipe.name} "
                      f"— {nearest.total_cost:.0f} ₽ "
                      f"(+{nearest.total_cost - budget:.0f})")
            else:
                print("  ничего не подошло и ближайшего нет")


if __name__ == "__main__":
    main()