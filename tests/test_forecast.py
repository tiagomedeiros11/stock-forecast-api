import pytest
from datetime import date, timedelta


@pytest.fixture
def product_with_sales(client):
    res = client.post("/products/", json={
        "sku": "FC-001",
        "name": "Forecast Product",
        "current_stock": 200.0,
        "reorder_point": 50.0,
    })
    product = res.json()

    # 30 days of sales history
    sales = []
    base = date(2024, 1, 1)
    for i in range(30):
        sales.append({"quantity": float(10 + i % 5), "date": str(base + timedelta(days=i))})

    client.post(f"/products/{product['id']}/sales/bulk", json={"sales": sales})
    return product


def test_forecast_product(client, product_with_sales):
    product_id = product_with_sales["id"]
    response = client.get(f"/forecast/products/{product_id}?days_ahead=30")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["predicted_demand"] >= 0
    assert data["confidence"] in ("low", "medium", "high")
    assert "needs_reorder" in data


def test_forecast_product_not_found(client):
    response = client.get("/forecast/products/999")
    assert response.status_code == 404


def test_forecast_no_sales_history(client):
    res = client.post("/products/", json={
        "sku": "EMPTY",
        "name": "No Sales",
        "current_stock": 10.0,
        "reorder_point": 5.0,
    })
    product_id = res.json()["id"]
    response = client.get(f"/forecast/products/{product_id}?days_ahead=30")
    assert response.status_code == 200
    assert response.json()["predicted_demand"] == 0.0
    assert response.json()["confidence"] == "low"


def test_reorder_alerts(client, product_with_sales):
    response = client.get("/forecast/alerts?days_ahead=30")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_forecast_needs_reorder_when_stock_low(client):
    res = client.post("/products/", json={
        "sku": "LOW-STOCK",
        "name": "Low Stock Product",
        "current_stock": 5.0,
        "reorder_point": 100.0,
    })
    product_id = res.json()["id"]

    sales = [{"quantity": 10.0, "date": str(date(2024, 1, 1) + timedelta(days=i))} for i in range(15)]
    client.post(f"/products/{product_id}/sales/bulk", json={"sales": sales})

    response = client.get(f"/forecast/products/{product_id}?days_ahead=30")
    assert response.json()["needs_reorder"] is True
