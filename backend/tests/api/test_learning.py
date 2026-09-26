def test_start_learning_without_video(client):
    response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "session_id" in data
    assert data["topic"] == "Python"
    assert data["language"] == "en"
    assert data["completed"] is False
    assert data["watch_percentage"] == 0.0 if "watch_percentage" in data else True


def test_start_learning_with_invalid_video(client):
    response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "video_id": "invalid-youtube-id",
            "language": "en",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Video not found"


def test_start_learning_empty_topic(client):
    response = client.post(
        "/learning/start",
        json={
            "topic": "",
            "language": "en",
        },
    )

    assert response.status_code == 422


def test_learning_event_watch_progress(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    assert start_response.status_code == 200

    session_id = start_response.json()["session_id"]

    response = client.post(
        "/learning/event",
        json={
            "session_id": session_id,
            "event_type": "watch_progress",
            "value": 65,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["event_type"] == "watch_progress"
    assert data["watch_percentage"] == 65.0
    assert data["status"] == "recorded"


def test_learning_event_watch_time(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.post(
        "/learning/event",
        json={
            "session_id": session_id,
            "event_type": "watch_time",
            "value": 300,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["watch_time_seconds"] == 300


def test_learning_event_quiz_completed(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.post(
        "/learning/event",
        json={
            "session_id": session_id,
            "event_type": "quiz_completed",
            "value": 85,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quiz_score"] == 85.0


def test_learning_event_video_completed(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.post(
        "/learning/event",
        json={
            "session_id": session_id,
            "event_type": "video_completed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["watch_percentage"] == 100.0


def test_update_learning_progress(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.patch(
        f"/learning/progress/{session_id}",
        json={
            "watch_percentage": 75,
            "watch_time_seconds": 450,
            "quiz_score": 90,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["watch_percentage"] == 75.0
    assert data["watch_time_seconds"] == 450
    assert data["quiz_score"] == 90.0


def test_complete_learning(client):
    start_response = client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.post(
        f"/learning/complete/{session_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["completed"] is True
    assert data["watch_percentage"] == 100.0
    assert data["completed_at"] is not None


def test_complete_invalid_session(client):
    response = client.post(
        "/learning/complete/999999"
    )

    assert response.status_code == 404


def test_learning_history(client):
    client.post(
        "/learning/start",
        json={
            "topic": "Python",
            "language": "en",
        },
    )

    client.post(
        "/learning/start",
        json={
            "topic": "Machine Learning",
            "language": "en",
        },
    )

    response = client.get(
        "/learning/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert "sessions" in data
    assert len(data["sessions"]) >= 2

    for session in data["sessions"]:
        assert "session_id" in session
        assert "language" in session
        assert "watch_percentage" in session
        assert "watch_time_seconds" in session
        assert "quiz_score" in session
        assert "completed" in session