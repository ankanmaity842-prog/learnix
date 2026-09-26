from pathlib import Path

import cv2


def detect_slides(
    frame_paths: list[str],
) -> list[dict]:
    results = []

    for frame_path in frame_paths:
        frame = cv2.imread(str(Path(frame_path)))

        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 80, 180)

        edge_density = float((edges > 0).mean())

        brightness = float(gray.mean())

        contrast = float(gray.std())

        slide_score = (
            min(edge_density * 3.0, 1.0) * 0.35
            + min(contrast / 80.0, 1.0) * 0.25
            + min(brightness / 255.0, 1.0) * 0.40
        )

        results.append(
            {
                "frame_path": frame_path,
                "is_slide": slide_score >= 0.45,
                "slide_score": round(slide_score, 4),
            }
        )

    return results