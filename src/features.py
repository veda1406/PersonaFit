"""
Feature engineering module for PersonaFit.
Creates domain-driven features and PCA projections.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib
import os


# ─── Domain feature creators ─────────────────────────────────────────────────

def bmi_age_risk_band(df: pd.DataFrame) -> pd.Series:
    """
    Combines BMI category × age group into a single ordinal risk band (0–8).
    Higher = riskier combination.
    """
    bmi = df["bmi"]
    age = df["age"]

    bmi_cat = pd.cut(bmi, bins=[0, 18.5, 25, 30, 100],
                     labels=[0, 1, 2, 3]).astype(float)
    age_cat = pd.cut(age, bins=[0, 30, 50, 100],
                     labels=[0, 1, 2]).astype(float)

    # Risk band: weighted sum (BMI slightly more important)
    band = (bmi_cat * 2 + age_cat).clip(0, 8)
    return band.rename("bmi_age_risk_band")


def activity_deficit_score(df: pd.DataFrame) -> pd.Series:
    """
    Deficit = how much below the ideal activity level (8/10) a person is.
    Positive means under-active; 0 means meets or exceeds ideal.
    """
    deficit = (8.0 - df["activity_level"]).clip(lower=0)
    return deficit.rename("activity_deficit_score")


def diet_sleep_index(df: pd.DataFrame) -> pd.Series:
    """
    Composite of diet quality and sleep adequacy, normalised to [0, 10].
    Higher index = healthier lifestyle.
    """
    sleep_score = ((df["sleep_hours"] - 4) / (10 - 4) * 10).clip(0, 10)
    index = (df["diet_score"] * 0.55 + sleep_score * 0.45)
    return index.rename("diet_sleep_index")


def lifestyle_risk_score(df: pd.DataFrame) -> pd.Series:
    """
    A composite risk signal derived from all base features.
    Higher = higher risk.
    """
    score = (
        0.03 * (df["age"] - 15)
        + 0.08 * (df["bmi"] - 25).clip(lower=0)
        - 0.15 * df["activity_level"]
        - 0.12 * df["diet_score"]
        - 0.10 * (df["sleep_hours"] - 5)
        + 0.60 * df["smoking_status"]
    )
    # Normalise to 0-10 using fixed theoretical range
    # Min (young, healthy, active, no smoke): 0.03*0 + 0 - 1.5 - 1.2 - 0.7 + 0 = -3.4
    # Max (old, obese, sedentary, smoker):    0.03*60 + 0.08*25 - 0 - 0 - 0 + 0.6 = 4.6
    SCORE_MIN, SCORE_MAX = -3.4, 4.6
    score = ((score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN) * 10).clip(0, 10)
    return score.rename("lifestyle_risk_score")


# ─── PCA ─────────────────────────────────────────────────────────────────────

def apply_pca(X: np.ndarray, n_components: int = 3,
              scaler=None, pca=None, fit: bool = True):
    """
    Scale and project features into PCA space.
    Returns (pca_df, scaler, pca_object).
    """
    if fit:
        scaler = StandardScaler()
        pca = PCA(n_components=n_components, random_state=42)
        X_sc = scaler.fit_transform(X)
        X_pca = pca.fit_transform(X_sc)
    else:
        X_sc = scaler.transform(X)
        X_pca = pca.transform(X_sc)

    cols = [f"pca_{i+1}" for i in range(n_components)]
    pca_df = pd.DataFrame(X_pca, columns=cols)
    return pca_df, scaler, pca


# ─── Main pipeline ────────────────────────────────────────────────────────────

def build_features(df: pd.DataFrame, n_pca: int = 3,
                   save_artifacts: bool = True) -> pd.DataFrame:
    """
    Add engineered features to *df* and append PCA components.
    Returns the enriched DataFrame.
    """
    out = df.copy()

    out["bmi_age_risk_band"] = bmi_age_risk_band(out).values
    out["activity_deficit_score"] = activity_deficit_score(out).values
    out["diet_sleep_index"] = diet_sleep_index(out).values
    out["lifestyle_risk_score"] = lifestyle_risk_score(out).values

    base_cols = ["age", "bmi", "activity_level", "diet_score",
                 "sleep_hours", "smoking_status",
                 "bmi_age_risk_band", "activity_deficit_score",
                 "diet_sleep_index", "lifestyle_risk_score"]
    X = out[base_cols].values

    pca_df, scaler, pca_obj = apply_pca(X, n_components=n_pca, fit=True)
    pca_df.index = out.index
    out = pd.concat([out, pca_df], axis=1)

    if save_artifacts:
        os.makedirs("models", exist_ok=True)
        joblib.dump(scaler, "models/pca_scaler.pkl")
        joblib.dump(pca_obj, "models/pca_model.pkl")

    return out


if __name__ == "__main__":
    import yaml

    with open("configs/config.yaml") as f:
        cfg = yaml.safe_load(f)

    df = pd.read_csv(cfg["data"]["processed_path"])
    print("Building features …")
    feat_df = build_features(df)
    feat_df.to_csv(cfg["data"]["features_path"], index=False)
    print(f"Feature matrix shape: {feat_df.shape}")
    print("New columns:", [c for c in feat_df.columns if c not in df.columns])
