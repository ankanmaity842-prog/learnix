from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "datasets"
    / "learning_interactions.csv"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "backend"
    / "ml_models"
    / "recommendation"
)

MODEL_PATH = OUTPUT_DIR / "recommendation_model.pkl"


FEATURES = [
    "knowledge_level",
    "watch_percentage",
    "quiz_score",
    "completion",
]

TARGET = "user_rating"


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
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print(f"MAE: {mae:.4f}")
    print(f"R2: {r2:.4f}")

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

    print(
        f"Model saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()