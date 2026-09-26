from pathlib import Path
import re

import cv2


CODE_PATTERNS = [
    r"\bdef\s+\w+\s*\(",
    r"\bclass\s+\w+",
    r"\bimport\s+\w+",
    r"\bfrom\s+\w+\s+import\b",
    r"\bfor\s+\w+\s+in\b",
    r"\bwhile\s+.+:",
    r"\bif\s+.+:",
    r"=>",
    r"System\.out\.println",
    r"#include\s*<",
]


def detect_code(frame_path: str) -> dict:
    frame = cv2.imread(str(Path(frame_path)))

    if frame is None:
        return {
            "frame_path": frame_path,
            "is_code": False,
            "code_score": 0.0,
        }

    try:
        import pytesseract
    except ImportError:
        return {
            "frame_path": frame_path,
            "is_code": False,
            "code_score": 0.0,
        }

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)

    matches = 0

    for pattern in CODE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matches += 1

    score = min(matches / 3.0, 1.0)

    return {
        "frame_path": frame_path,
        "is_code": score >= 0.34,
        "code_score": round(score, 4),
    }