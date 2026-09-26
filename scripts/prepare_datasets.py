from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "datasets"


REQUIRED_FILES = {
    "video_features.csv": [
        "video_id",
        "topic",
        "relevance_score",
        "transcript_simplicity",
        "visual_simplicity",
        "explanation_structure",
        "duration_minutes",
        "engagement_score",
        "difficulty",
    ],
    "learning_interactions.csv": [
        "user_id",
        "video_id",
        "topic",
        "knowledge_level",
        "watch_percentage",
        "quiz_score",
        "completion",
        "user_rating",
    ],
    "knowledge_gaps.csv": [
        "user_id",
        "topic",
        "prerequisite",
        "knowledge_level",
        "quiz_score",
        "missing",
    ],
}


def validate_file(filename: str, columns: list[str]) -> bool:
    path = DATA_DIR / filename

    if not path.exists():
        print(f"[ERROR] Missing: {path}")
        return False

    df = pd.read_csv(path)

    missing_columns = [
        column for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        print(
            f"[ERROR] {filename} missing columns: "
            f"{missing_columns}"
        )
        return False

    if df.empty:
        print(f"[ERROR] {filename} is empty")
        return False

    print(
        f"[OK] {filename}: "
        f"{len(df)} rows, {len(df.columns)} columns"
    )

    return True


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    valid = True

    for filename, columns in REQUIRED_FILES.items():
        if not validate_file(filename, columns):
            valid = False

    if valid:
        print("\nAll datasets are valid.")
    else:
        print("\nDataset validation failed.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()