def test_list_tasks(test_client, auth_headers, test_task):
    response = test_client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert "Test Task" in response.text


def test_task_rows_partial(test_client, auth_headers, test_task):
    response = test_client.get("/tasks/task_rows", headers=auth_headers)
    assert response.status_code == 200
    assert "Test Task" in response.text


def test_new_task_form(test_client, auth_headers):
    response = test_client.get("/tasks/new", headers=auth_headers)
    assert response.status_code == 200
    assert "New Task" in response.text or "modal" in response.text.lower()


def test_create_task(test_client, auth_headers):
    response = test_client.post(
        "/tasks",
        data={"title": "New Task", "priority": "high"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "New Task" in response.text


def test_edit_task_form(test_client, auth_headers, test_task):
    response = test_client.get(f"/tasks/{test_task.id}/edit", headers=auth_headers)
    assert response.status_code == 200


def test_update_task(test_client, auth_headers, test_task):
    response = test_client.put(
        f"/tasks/{test_task.id}",
        data={"title": "Updated Task", "status": "completed", "priority": "medium"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "Updated Task" in response.text


def test_complete_task(test_client, auth_headers, test_task):
    response = test_client.post(
        f"/tasks/{test_task.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_archive_task(test_client, auth_headers, test_task):
    response = test_client.post(
        f"/tasks/{test_task.id}/archive",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_restore_task(test_client, auth_headers, test_task):
    response = test_client.post(
        f"/tasks/{test_task.id}/restore",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_duplicate_task(test_client, auth_headers, test_task):
    response = test_client.post(
        f"/tasks/{test_task.id}/duplicate",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_delete_task(test_client, auth_headers, test_task):
    response = test_client.delete(
        f"/tasks/{test_task.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200


# ---- JSON REST API Tests ----

def test_api_list_tasks(test_client, auth_headers, test_task):
    response = test_client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_get_task(test_client, auth_headers, test_task):
    response = test_client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"


def test_api_create_task(test_client, auth_headers):
    response = test_client.post(
        "/api/tasks",
        json={"title": "API Task", "priority": "low"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Task"


def test_api_update_task(test_client, auth_headers, test_task):
    response = test_client.put(
        f"/api/tasks/{test_task.id}",
        json={"title": "API Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "API Updated"


def test_api_delete_task(test_client, auth_headers, test_task):
    response = test_client.delete(
        f"/api/tasks/{test_task.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204
