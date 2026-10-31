from core.models import Recipe, Ingredient, Product
from core.selector import select, nearest_over_budget


CATALOG = [
    Product("g800", "Гречка 800", "гречка", 800, None, 75.0, True),
    Product("ch700", "Курица 700", "куриная грудка", 700, None, 259.0, True),
    Product("ch_nostock", "Курица нет", "куриное бедро", 900, None, 219.0, False),
]


def make_recipe(rid, name, mains):
    return Recipe(
        id=rid, name=name, servings_base=1, time_min=30, tags=(),
        ingredients=tuple(Ingredient(p, "main", g) for p, g in mains),
    )


def test_select_strict_budget():
    r1 = make_recipe("r1", "Курица+гречка", [("куриная грудка", 150), ("гречка", 80)])
    r2 = make_recipe("r2", "Только гречка", [("гречка", 80)])
    res = select([r1, r2], CATALOG, persons=1, budget=334)
    assert len(res) == 2
    assert res[0].recipe.id == "r1"
    assert res[1].recipe.id == "r2"


def test_select_excludes_over_budget():
    r1 = make_recipe("r1", "Курица+гречка", [("куриная грудка", 150), ("гречка", 80)])
    res = select([r1], CATALOG, persons=1, budget=300)
    assert res == []


def test_select_excludes_out_of_stock():
    r = make_recipe("r", "Бедро+гречка", [("куриное бедро", 180), ("гречка", 80)])
    res = select([r], CATALOG, persons=1, budget=1000)
    assert res == []


def test_select_excludes_missing_product():
    r = make_recipe("r", "Лосось+гречка", [("лосось", 150), ("гречка", 80)])
    res = select([r], CATALOG, persons=1, budget=10000)
    assert res == []


def test_select_tie_break_by_name():
    r1 = make_recipe("r1", "Блюдо Б", [("гречка", 80)])
    r2 = make_recipe("r2", "Блюдо А", [("гречка", 80)])
    res = select([r1, r2], CATALOG, persons=1, budget=1000)
    assert res[0].recipe.name == "Блюдо А"


def test_nearest_over_budget():
    r1 = make_recipe("r1", "Курица+гречка", [("куриная грудка", 150), ("гречка", 80)])
    nearest = nearest_over_budget([r1], CATALOG, persons=1, budget=300)
    assert nearest is not None
    assert nearest.recipe.id == "r1"
    assert nearest.total_cost == 334.0