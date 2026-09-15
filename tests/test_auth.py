def test_register(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data


def test_login_and_get_me(client):
    client.post(
        "/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert me_response.status_code == 200

    data = me_response.json()

    assert data["username"] == "loginuser"
    assert data["email"] == "login@example.com"