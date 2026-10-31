from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from core.loader import load_recipes, load_catalog
from core.selector import select, nearest_over_budget

app = FastAPI()

# Загружаем данные при старте
RECIPES = load_recipes("data/recipes.json")
CATALOG = load_catalog("data/catalog_snapshot.json")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
    <head><meta charset="utf-8"><title>Подбор ужина</title></head>
    <body style="font-family: sans-serif; padding: 20px;">
        <h1>Подбор ужина</h1>
        <form action="/pick" method="post">
            <p>Человек: <input name="persons" type="number" value="2" min="1" max="20"></p>
            <p>Бюджет (₽): <input name="budget" type="number" value="800" min="1"></p>
            <button type="submit" style="padding: 10px 20px; font-size: 16px;">Подобрать</button>
        </form>
    </body>
    </html>
    """

@app.post("/pick", response_class=HTMLResponse)
async def pick(persons: int = Form(...), budget: float = Form(...)):
    results = select(RECIPES, CATALOG, persons, budget, limit=5)
    
    if not results:
        nearest = nearest_over_budget(RECIPES, CATALOG, persons, budget)
        if nearest:
            html = f"<p>Ничего не подошло. Ближайший: <b>{nearest.recipe.name}</b> — {nearest.total_cost:.0f} ₽</p>"
        else:
            html = "<p>Ничего не подошло.</p>"
        return html + "<a href='/'>Назад</a>"

    html = f"<h2>Варианты на {persons} чел., бюджет {budget:.0f} ₽</h2><ul>"
    for rc in results:
        html += f"<li><b>{rc.recipe.name}</b> — {rc.total_cost:.0f} ₽</li>"
    html += "</ul><a href='/'>Назад</a>"
    return html