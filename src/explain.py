"""
SHAP explainability module for PersonaFit.
Generates global feature importance and per-sample local explanations.
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

LABEL_MAP = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
FRIENDLY_NAMES = {
    "age": "Age",
    "bmi": "BMI",
    "activity_level": "Physical Activity",
    "diet_score": "Diet Quality",
    "sleep_hours": "Sleep Hours",
    "smoking_status": "Smoking",
    "bmi_age_risk_band": "BMI-Age Risk Band",
    "activity_deficit_score": "Activity Deficit",
    "diet_sleep_index": "Diet-Sleep Index",
    "lifestyle_risk_score": "Lifestyle Risk Score",
    "pca_1": "Vitals Component 1",
    "pca_2": "Vitals Component 2",
    "pca_3": "Vitals Component 3",
}


def get_explainer(model, X_train: np.ndarray):
    """Return a SHAP TreeExplainer or KernelExplainer based on model type."""
    model_name = type(model).__name__
    if model_name in ("RandomForestClassifier", "GradientBoostingClassifier"):
        return shap.TreeExplainer(model)
    else:
        # Use a small background sample for speed
        bg = shap.sample(X_train, min(100, len(X_train)))
        predict_fn = (model.predict_proba
                      if hasattr(model, "predict_proba")
                      else model.predict)
        return shap.KernelExplainer(predict_fn, bg)


def plot_global_importance(shap_values, feature_names: list,
                           out_dir: str, top_n: int = 10):
    """Bar plot of mean absolute SHAP values across all classes."""
    os.makedirs(out_dir, exist_ok=True)

    if isinstance(shap_values, list):
        # multiclass: average across classes
        mean_abs = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
    else:
        mean_abs = np.abs(shap_values).mean(axis=0)
        if mean_abs.ndim > 1:
            mean_abs = mean_abs.mean(axis=1)

    friendly = [FRIENDLY_NAMES.get(f, f) for f in feature_names]
    importance_df = pd.DataFrame({"feature": friendly, "importance": mean_abs})
    importance_df = importance_df.nlargest(top_n, "importance")

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(importance_df)))
    bars = ax.barh(importance_df["feature"][::-1],
                   importance_df["importance"][::-1], color=colors[::-1])
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Top Feature Influences on Health Risk Prediction")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    path = os.path.join(out_dir, "global_importance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Global importance plot -> {path}")
    return importance_df


def explain_sample(model, scaler, feature_cols: list,
                   sample: pd.Series, X_train: np.ndarray,
                   out_dir: str) -> dict:
    """
    Compute and return SHAP values for a single sample.
    Returns a dict of {feature_friendly_name: shap_value} for the predicted class.
    """
    os.makedirs(out_dir, exist_ok=True)

    X_sample = scaler.transform(sample.values.reshape(1, -1))
    explainer = get_explainer(model, X_train)
    sv = explainer.shap_values(X_sample)

    pred_class = model.predict(X_sample)[0]

    if isinstance(sv, list):
        sv_class = sv[pred_class][0]
    else:
        sv_class = sv[0] if sv.ndim == 1 else sv[0, :, pred_class]

    result = {}
    for feat, val in zip(feature_cols, sv_class):
        friendly = FRIENDLY_NAMES.get(feat, feat)
        result[friendly] = float(val)

    return result, pred_class


def run_shap_analysis(model, scaler, X_train: np.ndarray,
                      X_test: np.ndarray, feature_cols: list,
                      out_dir: str = "results/shap"):
    """Full SHAP analysis: global importance + sample waterfall."""
    print("  Computing SHAP values (this may take a minute)...")
    explainer = get_explainer(model, X_train)

    # Use subset of test for speed
    subset = X_test[:200]
    sv = explainer.shap_values(subset)

    importance_df = plot_global_importance(sv, feature_cols, out_dir)
    return importance_df


if __name__ == "__main__":
    import yaml
    from sklearn.model_selection import train_test_split

    with open("configs/config.yaml") as f:
        cfg = yaml.safe_load(f)

    df = pd.read_csv(cfg["data"]["features_path"])
    drop_cols = {"risk_label"}
    feature_cols = [c for c in df.columns if c not in drop_cols]
    X = df[feature_cols].values
    y = df["risk_label"].values

    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.2,
                                              stratify=y, random_state=42)

    scaler = joblib.load("models/feature_scaler.pkl")
    model = joblib.load("models/random_forest.pkl")

    X_train_sc = scaler.transform(X_train)
    X_test_sc = scaler.transform(X_test)

    run_shap_analysis(model, scaler, X_train_sc, X_test_sc,
                      feature_cols, cfg["paths"]["shap_dir"])
