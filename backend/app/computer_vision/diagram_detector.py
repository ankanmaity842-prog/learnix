from pathlib import Path

import cv2


def detect_diagrams(frame_path: str) -> dict:
    frame = cv2.imread(str(Path(frame_path)))

    if frame is None:
        return {
            "frame_path": frame_path,
            "diagram_count": 0,
            "has_diagram": False,
        }

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    diagram_count = 0

    image_area = frame.shape[0] * frame.shape[1]

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < image_area * 0.002:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            continue

        approximation = cv2.approxPolyDP(
            contour,
            0.03 * perimeter,
            True,
        )

        if 3 <= len(approximation) <= 20:
            diagram_count += 1

    diagram_count = min(diagram_count, 20)

    return {
        "frame_path": frame_path,
        "diagram_count": diagram_count,
        "has_diagram": diagram_count >= 3,
    }