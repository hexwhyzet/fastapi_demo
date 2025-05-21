import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from src.main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_create_task(client):
    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "Test description",
        "status": "в ожидании",
        "priority": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "в ожидании"
    assert data["priority"] == 2


def test_list_tasks(client):
    client.post("/tasks/", json={
        "title": "Another Task",
        "description": "Desc",
        "status": "в работе",
        "priority": 1
    })

    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1


def test_get_task_by_id(client):
    create_response = client.post("/tasks/", json={
        "title": "Unique Task",
        "description": "Find me",
        "status": "в работе",
        "priority": 3
    })
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}/")
    assert response.status_code == 200
    assert response.json()["title"] == "Unique Task"


def test_update_task(client):
    create_response = client.post("/tasks/", json={
        "title": "Old Title",
        "description": "Old Desc",
        "status": "в ожидании",
        "priority": 1
    })
    task_id = create_response.json()["id"]

    response = client.put(f"/tasks/{task_id}/", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_task(client):
    create_response = client.post("/tasks/", json={
        "title": "Delete Me",
        "description": "To be deleted",
        "status": "в ожидании",
        "priority": 1
    })
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}/")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}/")
    assert get_response.status_code == 200
    assert get_response.json() is None


def test_search_task(client):
    client.post("/tasks/", json={
        "title": "Unique Search Title",
        "description": "Blah blah",
        "status": "в ожидании",
        "priority": 1
    })
    response = client.get("/tasks/search/", params={"query": "Search"})
    assert response.status_code == 200
    results = response.json()
    assert any("Search" in task["title"] for task in results)


def test_create_task_missing_fields(client):
    response = client.post("/tasks/", json={
        "description": "No title field",
        "status": "в ожидании",
        "priority": 1
    })
    assert response.status_code == 422


def test_create_task_invalid_status(client):
    response = client.post("/tasks/", json={
        "title": "Invalid status",
        "description": "Bad status",
        "status": "not_a_valid_status",
        "priority": 1
    })
    assert response.status_code == 422


def test_create_task_invalid_priority_type(client):
    response = client.post("/tasks/", json={
        "title": "Wrong type",
        "description": "priority as string",
        "status": "в ожидании",
        "priority": "high"
    })
    assert response.status_code == 422


def test_update_task_invalid_fields(client):
    create_response = client.post("/tasks/", json={
        "title": "To update",
        "description": "Some",
        "status": "в ожидании",
        "priority": 1
    })
    task_id = create_response.json()["id"]

    response = client.put(f"/tasks/{task_id}/", json={
        "status": "unknown_status"
    })
    assert response.status_code == 422


def test_get_task_not_found(client):
    response = client.get("/tasks/999999/")
    assert response.status_code == 200
    assert response.json() is None


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999999/")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"
