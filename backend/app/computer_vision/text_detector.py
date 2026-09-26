from pathlib import Path

import cv2

try:
    import pytesseract
except ImportError:
    pytesseract = None


def detect_text(frame_path: str) -> dict:
    frame = cv2.imread(str(Path(frame_path)))

    if frame is None:
        return {
            "frame_path": frame_path,
            "text": "",
            "word_count": 0,
            "available": False,
        }

    if pytesseract is None:
        return {
            "frame_path": frame_path,
            "text": "",
            "word_count": 0,
            "available": False,
        }

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    thresholded = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )[1]

    text = pytesseract.image_to_string(thresholded)

    cleaned_text = " ".join(text.split())

    return {
        "frame_path": frame_path,
        "text": cleaned_text,
        "word_count": len(cleaned_text.split()),
        "available": True,
    }