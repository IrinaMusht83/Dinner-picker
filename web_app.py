from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from core.loader import load_recipes, load_catalog
from core.selector import select, nearest_over_budget

app = FastAPI()

RECIPES = load_recipes("data/recipes.json")
CATALOG = load_catalog("data/catalog_snapshot.json")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html><body>
    <h1>Подбор ужина</h1>
    <form action="/pick" method="post">
        Человек: <input name="persons" type="number" value="2" min="1" max="20"><br>
        Бюджет (₽): <input name="budget" type="number" value="800" min="1"><br>
        <button type="submit">Подобрать</button>
    </form>
    </body></html>
    """

@app.post("/pick", response_class=HTMLResponse)
async def pick(persons: int = Form(...), budget: float = Form(...)):
    results = select(RECIPES, CATALOG, persons, budget, limit=5)
    if not results:
        nearest = nearest_over_budget(RECIPES, CATALOG, persons, budget)
        if nearest:
            return f"<p>Ничего не подошло. Ближайший: {nearest.recipe.name} — {nearest.total_cost:.0f} ₽</p><a href='/'>Назад</a>"
        return "<p>Ничего не подошло.</p><a href='/'>Назад</a>"
    html = f"<h2>Варианты на {persons} чел., бюджет {budget:.0f} ₽</h2><ul>"
    for rc in results:
        html += f"<li><b>{rc.recipe.name}</b> — {rc.total_cost:.0f} ₽</li>"
    html += "</ul><a href='/'>Назад</a>"
    return html