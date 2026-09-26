from pathlib import Path

import cv2
import numpy as np


def _histogram(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    histogram = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [32, 32],
        [0, 180, 0, 256],
    )

    cv2.normalize(histogram, histogram)

    return histogram


def _histogram_difference(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    return float(
        cv2.compareHist(
            first,
            second,
            cv2.HISTCMP_BHATTACHARYYA,
        )
    )


def detect_scene_changes(
    frame_paths: list[str],
    threshold: float = 0.35,
) -> list[int]:
    if len(frame_paths) < 2:
        return []

    changes = []

    previous_histogram = None

    for index, frame_path in enumerate(frame_paths):
        frame = cv2.imread(str(Path(frame_path)))

        if frame is None:
            continue

        current_histogram = _histogram(frame)

        if previous_histogram is not None:
            difference = _histogram_difference(
                previous_histogram,
                current_histogram,
            )

            if difference >= threshold:
                changes.append(index)

        previous_histogram = current_histogram

    return changes