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
    <head>
        <meta charset="utf-8">
        <title>Подбор ужина</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background-color: #f9f9f9; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            input { padding: 8px; margin: 5px 0; width: 100%; box-sizing: border-box; }
            button { padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; }
            button:hover { background-color: #45a049; }
            ul { padding-left: 20px; }
            li { margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Подбор ужина</h1>
            <form action="/pick" method="post">
                <label>Количество человек:</label>
                <input name="persons" type="number" value="2" min="1" max="20" required>
                
                <label>Бюджет (₽):</label>
                <input name="budget" type="number" value="800" min="1" required>
                
                <button type="submit">Подобрать</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/pick", response_class=HTMLResponse)
async def pick(persons: int = Form(...), budget: float = Form(...)):
    # Ищем рецепты
    results = select(RECIPES, CATALOG, persons, budget, limit=5)
    
    # Формируем ответ
    html = """
    <html>
    <head><meta charset="utf-8"><title>Результаты</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background-color: #f9f9f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .back-link { display: inline-block; margin-top: 20px; color: #4CAF50; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
        .warning { color: #d32f2f; font-weight: bold; }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
    </style>
    </head>
    <body>
    <div class="container">
    """
    
    if not results:
        nearest = nearest_over_budget(RECIPES, CATALOG, persons, budget)
        html += f"<h2>Ничего не подошло в бюджет {budget:.0f} ₽</h2>"
        if nearest:
            html += f"<p class='warning'>Ближайший вариант: <b>{nearest.recipe.name}</b> — {nearest.total_cost:.0f} ₽</p>"
        else:
            html += "<p>В выбранном магазине нет подходящих продуктов.</p>"
    else:
        html += f"<h2>Варианты на {persons} чел., бюджет {budget:.0f} ₽</h2><ul>"
        for rc in results:
            html += f"<li><b>{rc.recipe.name}</b> — {rc.total_cost:.0f} ₽</li>"
        html += "</ul>"
        
    html += "<a href='/' class='back-link'>← Назад</a></div></body></html>"
    return html