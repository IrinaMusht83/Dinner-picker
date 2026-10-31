from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import Onboarding, Daily
from core.loader import load_recipes, load_catalog
from core.selector import select, nearest_over_budget
from db.profiles import init_db, get_profile, save_profile

router = Router()

RECIPES = load_recipes("data/recipes.json")
CATALOG = load_catalog("data/catalog_snapshot.json")
STORES = {"chizhik_test_001": "Чижик (тестовый)"}


# ---------- Онбординг ----------

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    init_db()
    profile = get_profile(message.from_user.id)

    if profile:
        store_name = STORES.get(profile["store_id"], profile["store_id"])
        await message.answer(
            f"С возвращением! Магазин: {store_name}, "
            f"{profile['default_persons']} чел. по умолчанию.\n\n"
            "Введите /dinner, чтобы подобрать ужин, "
            "или /reset, чтобы изменить профиль."
        )
        await state.set_state(None)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"store:{sid}")]
        for sid, name in STORES.items()
    ])
    await message.answer("Выберите магазин доставки:", reply_markup=kb)
    await state.set_state(Onboarding.choosing_store)


@router.message(Command("reset"))
async def reset(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"store:{sid}")]
        for sid, name in STORES.items()
    ])
    await message.answer("Выберите магазин доставки:", reply_markup=kb)
    await state.set_state(Onboarding.choosing_store)


@router.callback_query(F.data.startswith("store:"))
async def choose_store(cb: CallbackQuery, state: FSMContext):
    store_id = cb.data.split(":", 1)[1]
    await state.update_data(store_id=store_id)
    await cb.message.edit_text("Сколько человек обычно готовите? (целое число 1–20)")
    await state.set_state(Onboarding.entering_persons)
    await cb.answer()


@router.message(Onboarding.entering_persons)
async def onboard_persons(message: Message, state: FSMContext):
    try:
        n = int(message.text.strip())
        assert 1 <= n <= 20
    except (ValueError, AssertionError):
        await message.answer("Введите целое число от 1 до 20.")
        return

    data = await state.get_data()
    store_id = data["store_id"]
    save_profile(message.from_user.id, store_id, n)

    await message.answer(
        f"Профиль сохранён: {STORES[store_id]}, {n} чел. по умолчанию.\n\n"
        "Каждый день вводите /dinner, чтобы подобрать ужин."
    )
    await state.set_state(None)


# ---------- Ежедневный сценарий ----------

@router.message(Command("dinner"))
async def dinner_start(message: Message, state: FSMContext):
    profile = get_profile(message.from_user.id)
    if not profile:
        await message.answer("Сначала настройте профиль: /start")
        return

    default_n = profile["default_persons"]
    await message.answer(
        f"Сколько человек сегодня? (по умолчанию {default_n}; отправьте число или /ok)"
    )
    await state.set_state(Daily.entering_persons)


@router.message(Command("ok"))
async def dinner_use_default(message: Message, state: FSMContext):
    profile = get_profile(message.from_user.id)
    if not profile:
        await message.answer("Сначала настройте профиль: /start")
        return
    n = profile["default_persons"]
    await state.update_data(persons=n)
    await message.answer("Какая сумма на ужин? (общая на всех, ₽)")
    await state.set_state(Daily.entering_budget)


@router.message(Daily.entering_persons)
async def dinner_persons(message: Message, state: FSMContext):
    try:
        n = int(message.text.strip())
        assert 1 <= n <= 20
    except (ValueError, AssertionError):
        await message.answer("Введите целое число от 1 до 20.")
        return
    await state.update_data(persons=n)
    await message.answer("Какая сумма на ужин? (общая на всех, ₽)")
    await state.set_state(Daily.entering_budget)


@router.message(Daily.entering_budget)
async def dinner_budget(message: Message, state: FSMContext):
    try:
        budget = float(message.text.replace(",", ".").strip())
        assert budget > 0
    except (ValueError, AssertionError):
        await message.answer("Введите сумму больше 0 (например, 800).")
        return

    data = await state.get_data()
    persons = data["persons"]

    results = select(RECIPES, CATALOG, persons, budget, limit=5)

    if not results:
        nearest = nearest_over_budget(RECIPES, CATALOG, persons, budget)
        text = f"😕 В сумму {budget:.0f} ₽ ничего не подобралось."
        kb = None
        if nearest:
            text += (
                f"\n\nБлижайший вариант: {nearest.recipe.name} — "
                f"{nearest.total_cost:.0f} ₽ "
                f"(на {nearest.total_cost - budget:.0f} ₽ больше)."
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"Показать «{nearest.recipe.name}»",
                    callback_data=f"show:{nearest.recipe.id}"
                )]
            ])
        await message.answer(text, reply_markup=kb)
        await state.update_data(budget=budget)
        await state.set_state(Daily.viewing_results)
        return

    await state.update_data(budget=budget, results=[rc.recipe.id for rc in results])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{rc.recipe.name} — {rc.total_cost:.0f} ₽",
            callback_data=f"show:{rc.recipe.id}"
        )]
        for rc in results
    ])
    await message.answer("Варианты ужина (по близости к бюджету):", reply_markup=kb)
    await state.set_state(Daily.viewing_results)


@router.callback_query(F.data.startswith("show:"))
async def show_recipe(cb: CallbackQuery, state: FSMContext):
    recipe_id = cb.data.split(":", 1)[1]
    data = await state.get_data()
    persons = data.get("persons", 1)
    budget = data.get("budget", 0)

    recipe = next(r for r in RECIPES if r.id == recipe_id)
    rc_list = select([recipe], CATALOG, persons, budget, limit=1)
    if not rc_list:
        await cb.answer("Этот вариант уже не проходит по бюджету", show_alert=True)
        return
    rc = rc_list[0]

    lines = [f"🍽 {recipe.name}", f"На {persons} чел. — {rc.total_cost:.0f} ₽", "", "Продукты:"]
    for item in rc.items:
        packs = ", ".join(f"{p.name} ×{p.qty}" for p in item.chosen_packs)
        lines.append(f"• {item.product}: {item.needed_grams:.0f} г → {packs} ({item.cost:.0f} ₽)")

    pantry = [i.product for i in recipe.pantry]
    await state.update_data(pending_recipe=recipe_id, pending_pantry=pantry)

    await cb.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
        ])
    )
    await state.set_state(Daily.confirming_pantry)
    await cb.answer()


@router.callback_query(F.data == "confirm")
async def confirm_recipe(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pantry = data.get("pending_pantry", [])
    if pantry:
        text = (
            "⚠️ Перед подтверждением проверьте наличие дополнительных продуктов:\n\n"
            + "\n".join(f"• {p}" for p in pantry)
            + "\n\nЭти продукты не входят в список покупок, но нужны для приготовления."
        )
        await cb.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Всё есть — продолжить", callback_data="final")],
                [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
            ])
        )
    else:
        await finalize(cb, state)
    await cb.answer()


@router.callback_query(F.data == "final")
async def finalize(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    recipe_id = data["pending_recipe"]
    recipe = next(r for r in RECIPES if r.id == recipe_id)
    rc = select([recipe], CATALOG, data["persons"], data["budget"], limit=1)[0]

    lines = [f"✅ {recipe.name} — {rc.total_cost:.0f} ₽", "", "Список покупок:"]
    for item in rc.items:
        for p in item.chosen_packs:
            lines.append(f"• {p.name} ×{p.qty} — {p.price * p.qty:.0f} ₽")
    await cb.message.edit_text("\n".join(lines))
    await state.set_state(None)
    await cb.answer()


@router.callback_query(F.data == "cancel")
async def cancel(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Отменено. Введите /dinner, чтобы начать заново.")
    await state.set_state(None)
    await cb.answer()