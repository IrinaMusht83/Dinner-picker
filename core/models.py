from dataclasses import dataclass
from typing import Literal

IngredientType = Literal["main", "pantry"]


@dataclass(frozen=True)
class Ingredient:
    product: str
    type: IngredientType
    grams_per_serving: float = 0.0
    note: str | None = None


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    servings_base: int
    time_min: int
    tags: tuple[str, ...]
    ingredients: tuple[Ingredient, ...]

    @property
    def mains(self) -> list[Ingredient]:
        return [i for i in self.ingredients if i.type == "main"]

    @property
    def pantry(self) -> list[Ingredient]:
        return [i for i in self.ingredients if i.type == "pantry"]


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    product: str
    pack_size: float
    unit_count: int | None
    price: float
    in_stock: bool


@dataclass(frozen=True)
class ChosenPack:
    product_id: str
    name: str
    price: float
    qty: int


@dataclass(frozen=True)
class ItemCost:
    product: str
    needed_grams: float
    chosen_packs: tuple[ChosenPack, ...]
    cost: float


@dataclass(frozen=True)
class RecipeCost:
    recipe: Recipe | None
    persons: int
    total_cost: float
    items: tuple[ItemCost, ...]