from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    choosing_store = State()
    entering_persons = State()


class Daily(StatesGroup):
    entering_persons = State()
    entering_budget = State()
    viewing_results = State()
    confirming_pantry = State()