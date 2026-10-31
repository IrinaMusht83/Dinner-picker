import json
from pathlib import Path

from core.models import Recipe, Ingredient, Product


def load_recipes(path: str | Path) -> list[Recipe]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    recipes = []
    for r in data["recipes"]:
        ingredients = tuple(
            Ingredient(
                product=i["product"],
                type=i["type"],
                grams_per_serving=i.get("grams_per_serving", 0.0),
                note=i.get("note"),
            )
            for i in r["ingredients"]
        )
        recipes.append(Recipe(
            id=r["id"],
            name=r["name"],
            servings_base=r["servings_base"],
            time_min=r["time_min"],
            tags=tuple(r.get("tags", [])),
            ingredients=ingredients,
        ))
    return recipes


def load_catalog(path: str | Path) -> list[Product]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        Product(
            product_id=p["product_id"],
            name=p["name"],
            product=p["product"],
            pack_size=p["pack_size"],
            unit_count=p.get("unit_count"),
            price=p["price"],
            in_stock=p["in_stock"],
        )
        for p in data["products"]
    ]