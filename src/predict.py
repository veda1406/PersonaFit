"""
Prediction utilities for PersonaFit.
Handles loading models and making predictions with explanations.
"""

import os
import numpy as np
import pandas as pd
import joblib
from src.features import (bmi_age_risk_band, activity_deficit_score,
                           diet_sleep_index, lifestyle_risk_score)

RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}
RISK_COLORS = {0: "#2ECC71", 1: "#F39C12", 2: "#E74C3C"}
RISK_EMOJI  = {0: "🟢", 1: "🟡", 2: "🔴"}


def load_artifacts(models_dir: str = "models"):
    """Load scaler, feature columns, and best model (Random Forest by default)."""
    scaler = joblib.load(os.path.join(models_dir, "feature_scaler.pkl"))
    feature_cols = joblib.load(os.path.join(models_dir, "feature_cols.pkl"))
    model = joblib.load(os.path.join(models_dir, "random_forest.pkl"))
    return model, scaler, feature_cols


def build_input_row(age: float, bmi: float, activity_level: float,
                    diet_score: float, sleep_hours: float,
                    smoking_status: int) -> pd.DataFrame:
    """Create a single-row DataFrame from raw user inputs."""
    row = pd.DataFrame([{
        "age": age,
        "bmi": bmi,
        "activity_level": activity_level,
        "diet_score": diet_score,
        "sleep_hours": sleep_hours,
        "smoking_status": smoking_status,
    }])

    # Engineered features
    row["bmi_age_risk_band"] = bmi_age_risk_band(row).values
    row["activity_deficit_score"] = activity_deficit_score(row).values
    row["diet_sleep_index"] = diet_sleep_index(row).values
    row["lifestyle_risk_score"] = lifestyle_risk_score(row).values

    # PCA – load pre-fitted objects
    pca_scaler = joblib.load("models/pca_scaler.pkl")
    pca_model = joblib.load("models/pca_model.pkl")

    base_cols = ["age", "bmi", "activity_level", "diet_score",
                 "sleep_hours", "smoking_status",
                 "bmi_age_risk_band", "activity_deficit_score",
                 "diet_sleep_index", "lifestyle_risk_score"]
    X_pca = pca_model.transform(pca_scaler.transform(row[base_cols].values))
    for i in range(X_pca.shape[1]):
        row[f"pca_{i+1}"] = X_pca[0, i]

    return row


def predict(model, scaler, feature_cols: list, row: pd.DataFrame):
    """Return (risk_label_int, risk_probabilities) for the input row."""
    X = scaler.transform(row[feature_cols].values)
    pred = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    return pred, proba


def simulate_improvement(model, scaler, feature_cols: list,
                          base_inputs: dict, changes: dict):
    """
    Apply *changes* (dict of feature→new_value) to base_inputs and
    return the new predicted risk level and probabilities.
    """
    improved = {**base_inputs, **changes}
    row = build_input_row(**improved)
    return predict(model, scaler, feature_cols, row)
