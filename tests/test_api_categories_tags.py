def test_list_categories(test_client, auth_headers):
    response = test_client.get("/categories", headers=auth_headers)
    assert response.status_code == 200


def test_new_category_form(test_client, auth_headers):
    response = test_client.get("/categories/new", headers=auth_headers)
    assert response.status_code == 200


def test_create_category(test_client, auth_headers):
    response = test_client.post(
        "/categories",
        data={"name": "Work", "color": "#0d6efd"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "Work" in response.text


def test_create_and_delete_category(test_client, auth_headers, db_session):
    from app.models.category import Category
    cat = Category(user_id=1, name="TempCat", color="#10b981")
    db_session.add(cat)
    db_session.flush()
    db_session.refresh(cat)

    response = test_client.delete(f"/categories/{cat.id}", headers=auth_headers)
    assert response.status_code == 200


def test_list_tags(test_client, auth_headers):
    response = test_client.get("/tags", headers=auth_headers)
    assert response.status_code == 200


def test_new_tag_form(test_client, auth_headers):
    response = test_client.get("/tags/new", headers=auth_headers)
    assert response.status_code == 200


def test_create_tag(test_client, auth_headers):
    response = test_client.post(
        "/tags",
        data={"name": "urgent", "color": "#dc3545"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "urgent" in response.text


def test_delete_tag(test_client, auth_headers, db_session):
    from app.models.tag import Tag
    tag = Tag(user_id=1, name="to-delete", color="#6c757d")
    db_session.add(tag)
    db_session.flush()
    db_session.refresh(tag)

    response = test_client.delete(f"/tags/{tag.id}", headers=auth_headers)
    assert response.status_code == 200
