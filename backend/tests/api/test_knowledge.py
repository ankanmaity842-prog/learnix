def test_knowledge_requires_authentication(client):
    response = client.get(
        "/api/knowledge/map"
    )

    assert response.status_code in {
        401,
        403,
    }


def test_knowledge_gaps_requires_authentication(client):
    response = client.get(
        "/api/knowledge/gaps"
    )

    assert response.status_code in {
        401,
        403,
    }


def test_knowledge_prerequisites_requires_authentication(client):
    response = client.get(
        "/api/knowledge/prerequisites/Python"
    )

    assert response.status_code in {
        401,
        403,
    }


def test_knowledge_readiness_requires_authentication(client):
    response = client.get(
        "/api/knowledge/readiness/Machine%20Learning"
    )

    assert response.status_code in {
        401,
        403,
    }