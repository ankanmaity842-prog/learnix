from pathlib import Path

import cv2
import numpy as np


def calculate_visual_complexity(
    frame_path: str,
) -> dict:

    frame = cv2.imread(
        str(Path(frame_path))
    )

    if frame is None:
        return {
            "frame_path": frame_path,
            "complexity_score": 0.0,
            "complexity_level": "unknown",
            "visual_simplicity": 0.0,
        }

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY,
    )

    edges = cv2.Canny(
        gray,
        80,
        180,
    )

    edge_density = float(
        (edges > 0).mean()
    )

    contrast = float(
        gray.std()
    )

    histogram = cv2.calcHist(
        [gray],
        [0],
        None,
        [256],
        [0, 256],
    )

    histogram = histogram / max(
        histogram.sum(),
        1,
    )

    non_zero = histogram[
        histogram > 0
    ]

    entropy = 0.0

    if len(non_zero):
        entropy = float(
            -np.sum(
                non_zero
                * np.log2(non_zero)
            )
        )

    edge_score = min(
        edge_density / 0.25,
        1.0,
    )

    contrast_score = min(
        contrast / 80.0,
        1.0,
    )

    entropy_score = min(
        entropy / 8.0,
        1.0,
    )

    complexity_score = (
        edge_score * 0.40
        + contrast_score * 0.25
        + entropy_score * 0.35
    )

    complexity_score = round(
        max(
            0.0,
            min(
                complexity_score,
                1.0,
            ),
        ),
        4,
    )

    visual_simplicity = round(
        1.0 - complexity_score,
        4,
    )

    if complexity_score < 0.35:
        level = "low"
    elif complexity_score < 0.65:
        level = "medium"
    else:
        level = "high"

    return {
        "frame_path": frame_path,
        "complexity_score": complexity_score,
        "complexity_level": level,
        "visual_simplicity": visual_simplicity,
    }