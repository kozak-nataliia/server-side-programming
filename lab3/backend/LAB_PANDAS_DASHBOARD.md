# Lab: pandas analytics + Plotly dashboard in Django

This implementation follows the lab requirements (except the last **optional** part about multiprocessing).

## What was implemented

### 1) 6 aggregated ORM queries (repository level)

File: `cookbook/recipes/analytics.py`

Queries:
1. **Top recipes by favorites** (Recipe ↔ FavoriteRecipe) — `HAVING favorites_count > 0`, sorted by `favorites_count`.
2. **Recipe ratings** (Recipe ↔ RecipeComment) — `AVG(rating)` + comment count, `HAVING comments_count >= min_comments`.
3. **Ingredient usage** (Ingredient ↔ RecipeItem ↔ Recipe) — how many recipes use each ingredient.
4. **Recipes by ingredient count** (Recipe ↔ RecipeItem) — number of distinct ingredients + total quantity, `HAVING ingredients_count >= min_items`.
5. **Comments by month** (RecipeComment, grouped by `TruncMonth(created_at)`) — monthly trend + average rating.
6. **Unit usage** (Unit ↔ RecipeItem) — how often a unit is used + average quantity.

### 2) REST API endpoints that return pandas DataFrames

File: `cookbook/recipes/API/analytics_api.py`

All endpoints are under `GET /api/analytics/...` and require authentication.

Each endpoint:
- executes the ORM aggregated query
- converts rows into `pandas.DataFrame`
- returns JSON:
  - `rows`: DataFrame rows
  - `columns`: DataFrame column names
  - `stats`: basic statistics (mean/median/min/max) for selected numeric columns

### 3) Plotly dashboard integrated into Django

Files:
- View: `cookbook/recipes/views.py` → `analytics_dashboard`
- Template: `cookbook/recipes/templates/recipes/dashboard.html`

URL:
- `GET /dashboard/analytics/`

It shows **6 Plotly graphs** (one per aggregated query) and includes filters via query params:
- `recipe_category_id`
- `limit`
- `min_comments`
- `min_items`
- `min_recipes`
- `months`

## Difference: ORM aggregation vs pandas aggregation

### ORM (Django)
- Aggregation happens **in the database** (`GROUP BY`, `HAVING`, `COUNT`, `AVG`, ...).
- Efficient for large datasets because DB engines optimize queries and use indexes.
- Best when you need to filter/join on relational data and only send aggregated results to the app.

### pandas
- Aggregation happens **in Python memory** after the data is loaded.
- Great for fast experimentation, statistics, reshaping, joining already-loaded tables, and producing datasets for visualization.
- Not ideal for very large tables unless you first aggregate/filter in SQL/ORM.

In this lab, the “heavy” grouping is done via ORM, and pandas is used to:
- structure the results into DataFrames
- compute descriptive statistics
- feed Plotly charts

## How to run

1) Install deps

```bash
pip install -r requirements.txt
```

2) Run migrations (if needed)

```bash
python manage.py migrate
```

3) Create superuser (for Django login to see the dashboard)

```bash
python manage.py createsuperuser
```

4) Run server

```bash
python manage.py runserver
```

Open:
- Dashboard: `http://127.0.0.1:8000/dashboard/analytics/`

## API endpoints (pandas DataFrame response)

Examples:

- `GET /api/analytics/top-recipes-by-favorites/?limit=10`
- `GET /api/analytics/recipe-ratings/?min_comments=3&recipe_category_id=1`
- `GET /api/analytics/ingredient-usage/?min_recipes=2`
- `GET /api/analytics/recipes-by-ingredient-count/?min_items=4`
- `GET /api/analytics/comments-by-month/?months=12`
- `GET /api/analytics/unit-usage/?min_items=5`

Auth: use your existing token or Django session login.
