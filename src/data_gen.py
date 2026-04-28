"""
Data generation and preprocessing module for PersonaFit.
Creates a synthetic dataset that realistically models lifestyle → health risk patterns.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import yaml
import os

np.random.seed(42)


def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def generate_synthetic_data(n_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic lifestyle data with realistic correlations.
    Risk label: 0=Low, 1=Medium, 2=High
    """
    rng = np.random.RandomState(random_state)

    # Base features
    age = rng.uniform(15, 75, n_samples)
    bmi = rng.normal(25, 5, n_samples).clip(15, 50)
    activity_level = rng.uniform(0, 10, n_samples)          # 0=sedentary, 10=very active
    diet_score = rng.uniform(0, 10, n_samples)               # 0=poor, 10=excellent
    sleep_hours = rng.normal(7, 1.5, n_samples).clip(3, 12)
    smoking_status = rng.choice([0, 1], n_samples, p=[0.75, 0.25])  # 0=No, 1=Yes

    # Compute a raw risk score based on domain knowledge
    risk_score = (
        0.03 * (age - 15)                        # older → higher risk
        + 0.08 * np.maximum(bmi - 25, 0)         # high BMI → higher risk
        - 0.15 * activity_level                   # more activity → lower risk
        - 0.12 * diet_score                       # better diet → lower risk
        - 0.10 * (sleep_hours - 5)               # better sleep → lower risk
        + 0.60 * smoking_status                  # smoking → big risk boost
        + rng.normal(0, 0.3, n_samples)          # noise
    )

    # Bin into 3 classes
    low_thr = np.percentile(risk_score, 40)
    high_thr = np.percentile(risk_score, 75)
    risk_label = np.where(risk_score <= low_thr, 0,
                          np.where(risk_score <= high_thr, 1, 2))

    df = pd.DataFrame({
        "age": age.round(1),
        "bmi": bmi.round(2),
        "activity_level": activity_level.round(2),
        "diet_score": diet_score.round(2),
        "sleep_hours": sleep_hours.round(1),
        "smoking_status": smoking_status,
        "risk_label": risk_label,
    })

    # Introduce ~3% missing values in continuous features
    for col in ["bmi", "activity_level", "diet_score", "sleep_hours"]:
        mask = rng.rand(n_samples) < 0.03
        df.loc[mask, col] = np.nan

    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values, encode categoricals, return clean df."""
    df = df.copy()

    # Impute numeric columns with median
    num_cols = ["age", "bmi", "activity_level", "diet_score", "sleep_hours"]
    for col in num_cols:
        median = df[col].median()
        df[col] = df[col].fillna(median)

    # Impute categorical with mode
    df["smoking_status"] = df["smoking_status"].fillna(df["smoking_status"].mode()[0])

    return df


def scale_features(X_train, X_test=None):
    """Standard-scale feature matrices."""
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    if X_test is not None:
        X_test_sc = scaler.transform(X_test)
        return X_train_sc, X_test_sc, scaler
    return X_train_sc, scaler


if __name__ == "__main__":
    cfg = load_config()
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    print("Generating synthetic lifestyle data …")
    df = generate_synthetic_data(n_samples=cfg["data"]["n_samples"],
                                  random_state=cfg["data"]["random_state"])
    df.to_csv(cfg["data"]["raw_path"], index=False)
    print(f"  Raw data saved → {cfg['data']['raw_path']}  ({len(df)} rows)")

    clean = preprocess(df)
    clean.to_csv(cfg["data"]["processed_path"], index=False)
    print(f"  Processed data saved → {cfg['data']['processed_path']}")
    print(f"  Class distribution:\n{clean['risk_label'].value_counts().sort_index()}")
