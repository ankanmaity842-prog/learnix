from typing import Any

import cv2
import numpy as np


class VideoFeatureService:
    def __init__(self):
        self.default_features = {
            "transcript_length": 0,
            "transcript_simplicity": 0.5,
            "visual_simplicity": 0.5,
            "explanation_structure": 0.5,
            "text_density": 0.5,
            "diagram_presence": 0.0,
            "code_presence": 0.0,
            "scene_change_rate": 0.0,
            "visual_complexity": 0.5,
        }

    def extract_text_features(
        self,
        transcript: str | None,
    ) -> dict[str, float]:
        if not transcript:
            return {
                "transcript_length": 0,
                "transcript_simplicity": 0.5,
                "explanation_structure": 0.5,
            }

        text = " ".join(transcript.split())
        words = text.split()

        if not words:
            return {
                "transcript_length": 0,
                "transcript_simplicity": 0.5,
                "explanation_structure": 0.5,
            }

        sentences = [
            sentence.strip()
            for sentence in text.replace("!", ".")
            .replace("?", ".")
            .split(".")
            if sentence.strip()
        ]

        word_count = len(words)

        average_sentence_length = (
            word_count / len(sentences)
            if sentences
            else word_count
        )

        simplicity = self._calculate_simplicity(
            average_sentence_length
        )

        structure = self._calculate_structure(
            text=text,
            sentences=sentences,
        )

        return {
            "transcript_length": float(word_count),
            "transcript_simplicity": simplicity,
            "explanation_structure": structure,
        }

    def _calculate_simplicity(
        self,
        average_sentence_length: float,
    ) -> float:
        if average_sentence_length <= 10:
            return 1.0

        if average_sentence_length <= 15:
            return 0.85

        if average_sentence_length <= 20:
            return 0.7

        if average_sentence_length <= 25:
            return 0.55

        if average_sentence_length <= 35:
            return 0.4

        return 0.25

    def _calculate_structure(
        self,
        text: str,
        sentences: list[str],
    ) -> float:
        if not sentences:
            return 0.5

        markers = [
            "first",
            "second",
            "third",
            "finally",
            "therefore",
            "because",
            "example",
            "step",
            "next",
            "summary",
            "in conclusion",
        ]

        lower_text = text.lower()

        matches = sum(
            1
            for marker in markers
            if marker in lower_text
        )

        score = 0.4 + min(matches * 0.06, 0.6)

        return round(score, 4)

    def analyze_frame(
        self,
        frame: np.ndarray,
    ) -> dict[str, float]:
        if frame is None or frame.size == 0:
            return {
                "visual_complexity": 0.5,
                "visual_simplicity": 0.5,
                "text_density": 0.5,
                "diagram_presence": 0.0,
                "code_presence": 0.0,
            }

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        edges = cv2.Canny(
            gray,
            threshold1=100,
            threshold2=200,
        )

        edge_ratio = float(
            np.count_nonzero(edges) / edges.size
        )

        variance = float(
            cv2.Laplacian(
                gray,
                cv2.CV_64F,
            ).var()
        )

        visual_complexity = min(
            1.0,
            (edge_ratio * 4.0)
            + min(variance / 1000.0, 0.5),
        )

        visual_simplicity = 1.0 - visual_complexity

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        contour_count = len(contours)

        diagram_presence = min(
            contour_count / 100.0,
            1.0,
        )

        return {
            "visual_complexity": round(
                visual_complexity,
                4,
            ),
            "visual_simplicity": round(
                visual_simplicity,
                4,
            ),
            "text_density": round(
                edge_ratio,
                4,
            ),
            "diagram_presence": round(
                diagram_presence,
                4,
            ),
            "code_presence": 0.0,
        }

    def analyze_video(
        self,
        video_path: str,
        sample_interval: int = 30,
    ) -> dict[str, float]:
        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            raise ValueError(
                f"Unable to open video: {video_path}"
            )

        frame_features = []
        frame_index = 0

        while True:
            success, frame = capture.read()

            if not success:
                break

            if frame_index % sample_interval == 0:
                features = self.analyze_frame(frame)
                frame_features.append(features)

            frame_index += 1

        capture.release()

        if not frame_features:
            return {
                **self.default_features
            }

        return self._aggregate_frame_features(
            frame_features
        )

    def _aggregate_frame_features(
        self,
        features: list[dict[str, float]],
    ) -> dict[str, float]:
        keys = [
            "visual_complexity",
            "visual_simplicity",
            "text_density",
            "diagram_presence",
            "code_presence",
        ]

        result = {}

        for key in keys:
            values = [
                item.get(key, 0.0)
                for item in features
            ]

            result[key] = round(
                float(np.mean(values)),
                4,
            )

        return result

    def extract_features(
        self,
        transcript: str | None = None,
        video_path: str | None = None,
    ) -> dict[str, float]:
        text_features = self.extract_text_features(
            transcript
        )

        features = {
            **self.default_features,
            **text_features,
        }

        if video_path:
            visual_features = self.analyze_video(
                video_path
            )

            features.update(
                visual_features
            )

        return features


video_feature_service = VideoFeatureService()