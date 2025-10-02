import uuid
from fastapi.testclient import TestClient


def test_create_service(test_client: TestClient):
    # Arrange
    service_data = {"name": "光療指甲", "price": 1500, "duration_minutes": 90}

    # Act
    response = test_client.post("/api/v1/services", json=service_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == service_data["name"]
    assert data["price"] == service_data["price"]
    assert "id" in data


def test_list_services(test_client: TestClient):
    # Arrange: Create a service first
    test_client.post("/api/v1/services", json={"name": "卸甲", "price": 500, "duration_minutes": 30})

    # Act
    response = test_client.get("/api/v1/services")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["name"] == "卸甲" for item in data)


def test_update_service(test_client: TestClient):
    # Arrange: Create a service first
    create_response = test_client.post("/api/v1/services", json={"name": "保養", "price": 800, "duration_minutes": 60})
    service_id = create_response.json()["id"]
    update_data = {"price": 900, "is_active": False}

    # Act
    response = test_client.put(f"/api/v1/services/{service_id}", json=update_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 900
    assert data["is_active"] is False


def test_delete_service(test_client: TestClient):
    # Arrange: Create a service first
    create_response = test_client.post("/api/v1/services", json={"name": "待刪除服務", "price": 100, "duration_minutes": 10})
    service_id = create_response.json()["id"]

    # Act
    response = test_client.delete(f"/api/v1/services/{service_id}")

    # Assert
    assert response.status_code == 204
