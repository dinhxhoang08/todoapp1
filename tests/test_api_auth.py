def test_register(test_client):
    response = test_client.post(
        "/auth/register",
        data={"username": "newuser", "email": "new@test.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_register_duplicate_username(test_client, test_user):
    response = test_client.post(
        "/auth/register",
        data={"username": "testuser", "email": "other@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "already taken" in response.text.lower()


def test_register_duplicate_email(test_client, test_user):
    response = test_client.post(
        "/auth/register",
        data={"username": "otheruser", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "already registered" in response.text.lower()


def test_login_success(test_client, test_user):
    response = test_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_login_wrong_password(test_client, test_user):
    response = test_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpass"},
    )
    assert response.status_code == 200
    assert "invalid" in response.text.lower()


def test_login_nonexistent(test_client):
    response = test_client.post(
        "/auth/login",
        data={"username": "nobody", "password": "testpass123"},
    )
    assert response.status_code == 200
    assert "invalid" in response.text.lower()


def test_logout(test_client):
    response = test_client.post("/auth/logout", follow_redirects=False)
    assert response.status_code == 303


def test_dashboard_requires_auth(test_client):
    response = test_client.get("/dashboard")
    assert response.status_code == 401


def test_dashboard_authenticated(test_client, auth_headers):
    response = test_client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
