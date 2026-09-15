def get_token(client, username, email):
    client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )

    response = client.post(
        "/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_users_cannot_access_each_others_documents(client):
    token_a = get_token(
        client,
        "usera",
        "usera@example.com",
    )

    token_b = get_token(
        client,
        "userb",
        "userb@example.com",
    )

    # User A creates a document
    response = client.post(
        "/documents/",
        json={
            "title": "User A Document",
            "content": "Private information belonging to User A.",
        },
        headers={
            "Authorization": f"Bearer {token_a}"
        },
    )

    assert response.status_code == 201

    document_a_id = response.json()["id"]

    # User B tries to access User A's document
    response = client.get(
        f"/documents/{document_a_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        },
    )

    assert response.status_code == 404

def test_users_only_see_their_own_documents(client):
    token_a = get_token(
        client,
        "listusera",
        "listusera@example.com",
    )

    token_b = get_token(
        client,
        "listuserb",
        "listuserb@example.com",
    )

    # User A creates a document
    response = client.post(
        "/documents/",
        json={
            "title": "A Private Document",
            "content": "Private content A",
        },
        headers={
            "Authorization": f"Bearer {token_a}"
        },
    )

    assert response.status_code == 201

    # User B creates a document
    response = client.post(
        "/documents/",
        json={
            "title": "B Private Document",
            "content": "Private content B",
        },
        headers={
            "Authorization": f"Bearer {token_b}"
        },
    )

    assert response.status_code == 201

    # User A lists documents
    response = client.get(
        "/documents/",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    titles = [
        document["title"]
        for document in data["items"]
    ]

    assert "A Private Document" in titles
    assert "B Private Document" not in titles