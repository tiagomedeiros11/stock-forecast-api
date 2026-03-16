# Stock Forecast API

A REST API for **inventory demand forecasting** built with FastAPI. Given a product's historical sales data, it predicts future demand using Linear Regression and alerts when stock is likely to fall below the reorder point.

![CI](https://github.com/YOUR_USERNAME/stock-forecast-api/actions/workflows/ci.yml/badge.svg)

---

## Features

- **Demand forecasting** — predicts total units needed for the next N days (default: 30)
- **Reorder alerts** — lists all products predicted to go below their reorder point
- **Adaptive model** — uses Linear Regression when enough data is available, falls back to moving average otherwise
- **Confidence score** — returns `low / medium / high` confidence based on R² of the regression
- **Bulk sales import** — register historical sales in batches
- **Interactive docs** — auto-generated Swagger UI at `/docs`
- **Dockerized** — runs with a single `docker compose up`
- **CI/CD** — GitHub Actions runs the full test suite on every push

---

## Architecture

```
app/
├── main.py              # FastAPI app + lifespan (DB init)
├── database.py          # SQLAlchemy engine + session + Base
├── models/              # ORM models (Product, Sale)
├── schemas/             # Pydantic schemas (request/response)
├── routers/             # API endpoints (products, sales, forecast)
├── services/            # Business logic (forecast, alerts)
└── ml/
    └── model.py         # Prediction engine (scikit-learn)
```

### Prediction logic

```
sales history (< 7 days)  →  Moving Average  →  confidence: low
sales history (>= 7 days) →  Linear Regression on time series  →  confidence based on R²
                                    ↓
                          R² >= 0.7  →  high
                          R² >= 0.4  →  medium
                          R²  < 0.4  →  low
```

The forecasted demand is subtracted from `current_stock`. If the result is below `reorder_point`, the product appears in the `/forecast/alerts` endpoint.

---

## Getting Started

### With Docker (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/stock-forecast-api.git
cd stock-forecast-api
docker compose up
```

API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

---

## API Endpoints

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/products/` | Register a new product |
| `GET` | `/products/` | List all products |
| `GET` | `/products/{id}` | Get product by ID |
| `PATCH` | `/products/{id}` | Update product (stock, reorder point) |
| `DELETE` | `/products/{id}` | Remove product |

### Sales
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/products/{id}/sales/` | Register a single sale |
| `POST` | `/products/{id}/sales/bulk` | Register multiple sales at once |
| `GET` | `/products/{id}/sales/` | List all sales for a product |

### Forecast
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/forecast/products/{id}?days_ahead=30` | Forecast demand for a product |
| `GET` | `/forecast/alerts?days_ahead=30` | List products that need reordering |

---

## Example Usage

**1. Create a product**
```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"sku": "WIDGET-A", "name": "Widget A", "current_stock": 200, "reorder_point": 50}'
```

**2. Add historical sales**
```bash
curl -X POST http://localhost:8000/products/1/sales/bulk \
  -H "Content-Type: application/json" \
  -d '{"sales": [
    {"quantity": 12, "date": "2024-01-01"},
    {"quantity": 9,  "date": "2024-01-02"},
    {"quantity": 15, "date": "2024-01-03"}
  ]}'
```

**3. Get forecast**
```bash
curl http://localhost:8000/forecast/products/1?days_ahead=30
```

```json
{
  "product_id": 1,
  "product_sku": "WIDGET-A",
  "product_name": "Widget A",
  "days_ahead": 30,
  "predicted_demand": 342.5,
  "current_stock": 200.0,
  "stock_after_demand": -142.5,
  "needs_reorder": true,
  "reorder_point": 50.0,
  "confidence": "high",
  "r2_score": 0.812,
  "generated_at": "2024-02-15T10:30:00Z"
}
```

---

## Running Tests

```bash
pytest --cov=app tests/
```

Test coverage includes:
- Product CRUD endpoints
- Sales registration (single + bulk)
- Forecast logic and confidence levels
- ML model edge cases (empty history, negative predictions, few samples)

---

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — async web framework with automatic OpenAPI docs
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM with SQLite (easily swappable for PostgreSQL)
- **[Pydantic v2](https://docs.pydantic.dev/)** — data validation and serialization
- **[scikit-learn](https://scikit-learn.org/)** — Linear Regression model
- **[pandas](https://pandas.pydata.org/)** — time series aggregation
- **[pytest](https://pytest.org/)** — test suite with dependency injection override
- **Docker** + **GitHub Actions** — containerization and CI

---

## Design Decisions

**Why SQLite by default?**
Zero-config for local development and CI. Swap `DATABASE_URL` to a PostgreSQL URL for production — no code changes needed.

**Why Linear Regression instead of something fancier?**
It's interpretable, fast, and sufficient for the use case. The R² score is surfaced directly in the response so consumers know how much to trust the forecast. Adding Prophet or ARIMA would be a natural next step for seasonal data.

**Why a separate `ml/` module?**
Keeps the prediction logic isolated and unit-testable without the HTTP layer. The `predict()` function is a pure function: input sales history, output forecast — no DB, no side effects.
