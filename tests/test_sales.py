import pytest


@pytest.fixture
def product(client):
    res = client.post("/products/", json={
        "sku": "SALE-PROD",
        "name": "Sale Product",
        "current_stock": 100.0,
        "reorder_point": 10.0,
    })
    return res.json()


def test_create_sale(client, product):
    response = client.post(f"/products/{product['id']}/sales/", json={
        "quantity": 5.0,
        "date": "2024-01-10",
    })
    assert response.status_code == 201
    assert response.json()["quantity"] == 5.0


def test_create_sale_product_not_found(client):
    response = client.post("/products/999/sales/", json={"quantity": 1.0, "date": "2024-01-01"})
    assert response.status_code == 404


def test_bulk_create_sales(client, product):
    payload = {
        "sales": [
            {"quantity": 3.0, "date": "2024-01-01"},
            {"quantity": 7.0, "date": "2024-01-02"},
            {"quantity": 5.0, "date": "2024-01-03"},
        ]
    }
    response = client.post(f"/products/{product['id']}/sales/bulk", json=payload)
    assert response.status_code == 201
    assert len(response.json()) == 3


def test_list_sales(client, product):
    client.post(f"/products/{product['id']}/sales/", json={"quantity": 2.0, "date": "2024-02-01"})
    client.post(f"/products/{product['id']}/sales/", json={"quantity": 4.0, "date": "2024-02-02"})
    response = client.get(f"/products/{product['id']}/sales/")
    assert response.status_code == 200
    assert len(response.json()) == 2
