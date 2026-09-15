def get_token(client):
    client.post(
        "/register",
        json={
            "username": "uploaduser",
            "email": "upload@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/login",
        json={
            "email": "upload@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_upload_rejects_unsupported_file_type(client):
    token = get_token(client)

    response = client.post(
        "/documents/",
        json={
            "title": "Upload Test",
            "content": "Testing uploads",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    document_id = response.json()["id"]

    response = client.post(
        f"/documents/{document_id}/file",
        files={
            "file": (
                "malware.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

def test_upload_rejects_file_over_10mb(client):
    token = get_token(client)

    response = client.post(
        "/documents/",
        json={
            "title": "Large File Test",
            "content": "Testing file size",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    document_id = response.json()["id"]

    large_file = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        f"/documents/{document_id}/file",
        files={
            "file": (
                "large.txt",
                large_file,
                "text/plain",
            )
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400