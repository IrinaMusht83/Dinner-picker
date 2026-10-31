from core.models import Product, Ingredient, Recipe
from core.costing import choose_packs, scale_recipe


def make_product(pid, product, pack_size, price, in_stock=True, unit_count=None):
    return Product(pid, pid, product, pack_size, unit_count, price, in_stock)


def test_choose_packs_single_pack():
    products = [make_product("g800", "гречка", 800, 75.0)]
    packs, cost = choose_packs(300, products)
    assert cost == 75.0
    assert packs[0].qty == 1


def test_choose_packs_prefers_cheaper_big_pack():
    products = [
        make_product("g400", "гречка", 400, 60.0),
        make_product("g800", "гречка", 800, 90.0),
    ]
    packs, cost = choose_packs(300, products)
    assert cost == 60.0
    assert packs[0].product_id == "g400"


def test_choose_packs_multiple_packs():
    products = [make_product("g400", "гречка", 400, 60.0)]
    packs, cost = choose_packs(900, products)
    assert cost == 180.0
    assert packs[0].qty == 3


def test_choose_packs_tie_break_by_overrun():
    products = [
        make_product("g400", "гречка", 400, 60.0),
        make_product("g800", "гречка", 800, 90.0),
    ]
    packs, cost = choose_packs(900, products)
    assert cost == 180.0
    assert packs[0].qty == 3


def test_choose_packs_empty():
    assert choose_packs(100, []) is None


def test_scale_recipe():
    r = Recipe(
        id="x", name="X", servings_base=1, time_min=10, tags=(),
        ingredients=(
            Ingredient("гречка", "main", 80),
            Ingredient("соль", "pantry"),
        ),
    )
    scaled = scale_recipe(r, 3)
    assert scaled[0][1] == 240
    assert scaled[1][1] == 0