"""Проверяет, что все main-продукты из рецептов есть в снапшоте."""
import sys

from core.loader import load_recipes, load_catalog

PANTRY = {"масло для жарки", "соль", "специи"}


def main():
    recipes = load_recipes("data/recipes.json")
    catalog = load_catalog("data/catalog_snapshot.json")

    catalog_products = {p.product for p in catalog}
    errors = []

    for r in recipes:
        for ing in r.ingredients:
            if ing.type == "main" and ing.product not in catalog_products:
                errors.append(f"  [{r.id}] нет в каталоге: '{ing.product}'")
            if ing.type == "pantry" and ing.product not in PANTRY:
                errors.append(f"  [{r.id}] неканонический pantry: '{ing.product}'")

        pantry = {i.product for i in r.pantry}
        if not pantry <= PANTRY:
            errors.append(f"  [{r.id}] pantry вне набора: {pantry - PANTRY}")

    print(f"Рецептов: {len(recipes)}, товаров: {len(catalog)}")
    if errors:
        print("ОШИБКИ:")
        print("\n".join(errors))
        sys.exit(1)
    print("✅ Данные согласованы")


if __name__ == "__main__":
    main()