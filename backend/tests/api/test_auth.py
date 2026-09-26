def test_login_requires_email(client):
    response = client.post(
        "/api/auth/login",
        json={
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_requires_password(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
        },
    )

    assert response.status_code == 422