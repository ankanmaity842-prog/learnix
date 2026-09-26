def test_quiz_requires_authentication(client):
    response = client.post(
        "/api/quiz/generate",
        json={
            "topic": "Machine Learning",
            "content": "Machine learning uses data to learn patterns.",
            "language": "en",
            "question_count": 5,
        },
    )

    assert response.status_code in {
        401,
        403,
    }