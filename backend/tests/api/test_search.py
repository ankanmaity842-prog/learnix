def test_search_requires_query(client):
    response = client.get(
        "/api/search/"
    )
def test_search_requires_minimum_query_length(client):
    response = client.get(
        "/api/search/",
        params={
            "q": "a",
        },
    )

    assert response.status_code == 422


def test_search_accepts_topic(client):
    response = client.get(
        "/api/search/",
        params={
            "q": "machine learning",
            "language": "en",
            "level": "beginner",
        },
    )

    assert response.status_code in {
        200,
        401,
        403,
    }
    assert response.status_code in {
        400,
        422,
    }