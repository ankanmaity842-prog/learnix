def test_notes_requires_authentication(client):
    response = client.post(
        "/api/notes/",
        json={
            "topic": "Machine Learning",
            "content": "Machine learning is a branch of AI.",
            "language": "en",
        },
    )

    assert response.status_code in {
        401,
        403,
    }