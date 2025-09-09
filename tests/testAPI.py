import pytest
from fastapi.testclient import TestClient
from app import app
from datetime import date, datetime

client = TestClient(app) 

def test_create_task_api():
    payload = {
        "title": "API Task",
        "description": "Testing API create",
        "due_date": "2025-09-20",
        "priority": 1,
        "status": "Pending"
    }
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Task"
    assert data["priority"] == 1
    assert data["status"] == "Pending"

def test_get_all_tasks_api():
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # check for task
    assert any(task["title"] == "API Task" for task in data)

def test_get_task_by_id_api():
    # create a task
    payload = {"title": "Get By ID", "priority": 2}
    response = client.post("/tasks/", json=payload)
    task_id = response.json()["task_id"]

    # get by ID
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["title"] == "Get By ID"

def test_update_task_api():
    # Create task
    payload = {"title": "Old Title"}
    response = client.post("/tasks/", json=payload)
    task_id = response.json()["task_id"]

    # Update
    update_payload = {"title": "New Title", "status": "Completed"}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["status"] == "Completed"

def test_delete_task_api():
    # Create task
    payload = {"title": "Delete Me"}
    response = client.post("/tasks/", json=payload)
    task_id = response.json()["task_id"]

    # delete
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # check task is deleted
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
