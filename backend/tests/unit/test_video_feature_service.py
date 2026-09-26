import cv2
import numpy as np

from app.services.video_feature_service import (
    VideoFeatureService,
)


def test_extract_text_features():
    service = VideoFeatureService()

    transcript = (
        "First learn variables. "
        "Next learn functions. "
        "Finally build a project."
    )

    features = service.extract_text_features(
        transcript
    )

    assert features["transcript_length"] > 0

    assert 0.0 <= features[
        "transcript_simplicity"
    ] <= 1.0

    assert 0.0 <= features[
        "explanation_structure"
    ] <= 1.0


def test_empty_transcript():
    service = VideoFeatureService()

    features = service.extract_text_features(
        ""
    )

    assert features["transcript_length"] == 0
    assert features["transcript_simplicity"] == 0.5
    assert features["explanation_structure"] == 0.5


def test_analyze_frame():
    service = VideoFeatureService()

    frame = np.zeros(
        (224, 224, 3),
        dtype=np.uint8,
    )

    features = service.analyze_frame(frame)

    assert "visual_complexity" in features
    assert "visual_simplicity" in features
    assert "text_density" in features
    assert "diagram_presence" in features
    assert "code_presence" in features

    assert 0.0 <= features[
        "visual_complexity"
    ] <= 1.0

    assert 0.0 <= features[
        "visual_simplicity"
    ] <= 1.0


def test_analyze_frame_with_edges():
    service = VideoFeatureService()

    frame = np.zeros(
        (224, 224, 3),
        dtype=np.uint8,
    )

    cv2.rectangle(
        frame,
        (20, 20),
        (200, 200),
        (255, 255, 255),
        3,
    )

    features = service.analyze_frame(frame)

    assert features["visual_complexity"] >= 0.0
    assert features["visual_simplicity"] >= 0.0


def test_analyze_invalid_frame():
    service = VideoFeatureService()

    features = service.analyze_frame(
        np.array([])
    )

    assert features["visual_complexity"] == 0.5
    assert features["visual_simplicity"] == 0.5
    assert features["text_density"] == 0.5
    assert features["diagram_presence"] == 0.0
    assert features["code_presence"] == 0.0


def test_extract_features_without_video():
    service = VideoFeatureService()

    features = service.extract_features(
        transcript="Python is a programming language."
    )

    assert features["transcript_length"] > 0
    assert "visual_simplicity" in features
    assert "visual_complexity" in features


def test_extract_features_without_transcript():
    service = VideoFeatureService()

    features = service.extract_features()

    assert features["transcript_length"] == 0
    assert features["transcript_simplicity"] == 0.5