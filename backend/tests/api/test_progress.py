def test_progress_requires_authentication(client):
    response = client.get(
        "/api/progress/"
    )

    assert response.status_code in {
        401,
        403,
    }