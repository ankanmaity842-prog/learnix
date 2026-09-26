from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "datasets" / "video_features.csv"

OUTPUT_DIR = (
    ROOT_DIR
    / "backend"
    / "ml_models"
    / "difficulty"
)

MODEL_PATH = OUTPUT_DIR / "difficulty_model.pkl"


FEATURES = [
    "transcript_simplicity",
    "visual_simplicity",
    "explanation_structure",
    "duration_minutes",
    "engagement_score",
]

TARGET = "difficulty"


def main():
    df = pd.read_csv(DATA_PATH)

    df = df.dropna(
        subset=FEATURES + [TARGET]
    )

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
        },
        MODEL_PATH,
    )

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()