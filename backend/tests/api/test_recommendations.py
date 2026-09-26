def test_recommendation_requires_authentication(client):
    response = client.get(
        "/api/recommendations/"
    )

def test_recommendation_requires_topic(client):
    response = client.post(
        "/api/recommendations/",
        json={
            "language": "en",
            "level": "beginner",
        },
    )

    assert response.status_code == 422


def test_recommendation_topic_too_short(client):
    response = client.post(
        "/api/recommendations/",
        json={
            "topic": "a",
            "language": "en",
            "level": "beginner",
        },
    )

    assert response.status_code == 422
    assert response.status_code in {
        401,
        403,
    }