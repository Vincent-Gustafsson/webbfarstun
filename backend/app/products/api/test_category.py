from fastapi.testclient import TestClient


def test_create_category(client: TestClient):
    payload = {
        "name": "Phones",
        "description": "This is a description.",
        "is_container": True,
    }

    response = client.post("/categories/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert payload.items() <= data.items()
