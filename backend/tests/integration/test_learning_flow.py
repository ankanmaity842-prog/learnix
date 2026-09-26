def test_learning_flow_starts_with_topic_search(client):
    response = client.get(
        "/api/search/",
        params={
            "q": "machine learning",
        },
    )

    assert response.status_code in {
        200,
        401,
        403,
    }