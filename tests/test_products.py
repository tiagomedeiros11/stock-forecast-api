def test_create_product(client):
    response = client.post("/products/", json={
        "sku": "PROD-001",
        "name": "Widget A",
        "current_stock": 100.0,
        "reorder_point": 20.0,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "PROD-001"
    assert data["current_stock"] == 100.0


def test_create_duplicate_sku(client):
    payload = {"sku": "PROD-002", "name": "Widget B", "current_stock": 50.0, "reorder_point": 10.0}
    client.post("/products/", json=payload)
    response = client.post("/products/", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_products(client):
    client.post("/products/", json={"sku": "A", "name": "A", "current_stock": 10.0, "reorder_point": 2.0})
    client.post("/products/", json={"sku": "B", "name": "B", "current_stock": 20.0, "reorder_point": 5.0})
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404


def test_update_product(client):
    res = client.post("/products/", json={"sku": "UPD", "name": "Old", "current_stock": 10.0, "reorder_point": 2.0})
    product_id = res.json()["id"]
    response = client.patch(f"/products/{product_id}", json={"current_stock": 999.0})
    assert response.status_code == 200
    assert response.json()["current_stock"] == 999.0


def test_delete_product(client):
    res = client.post("/products/", json={"sku": "DEL", "name": "Del", "current_stock": 1.0, "reorder_point": 0.0})
    product_id = res.json()["id"]
    assert client.delete(f"/products/{product_id}").status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404
