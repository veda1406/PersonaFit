"""
Master pipeline script for PersonaFit.
Run this once to generate data, engineer features, train models, and create SHAP plots.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_gen import load_config, generate_synthetic_data, preprocess
from src.features import build_features
from src.train import train
from src.explain import run_shap_analysis

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split


def main():
    print("\n" + "=" * 60)
    print("  PersonaFit - ML Pipeline")
    print("=" * 60)

    cfg = load_config("configs/config.yaml")
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # 1. Generate & clean data
    print("\n[1/4] Generating synthetic data...")
    df_raw = generate_synthetic_data(
        n_samples=cfg["data"]["n_samples"],
        random_state=cfg["data"]["random_state"]
    )
    df_raw.to_csv(cfg["data"]["raw_path"], index=False)
    df_clean = preprocess(df_raw)
    df_clean.to_csv(cfg["data"]["processed_path"], index=False)
    print(f"  Samples: {len(df_clean)}")
    print(f"  Class distribution: {dict(df_clean['risk_label'].value_counts().sort_index())}")

    # 2. Feature engineering
    print("\n[2/4] Engineering features...")
    df_feat = build_features(df_clean)
    df_feat.to_csv(cfg["data"]["features_path"], index=False)
    print(f"  Feature matrix: {df_feat.shape}")

    # 3. Train all models
    print("\n[3/4] Training models...")
    all_metrics, best_name = train("configs/config.yaml")

    # 4. SHAP analysis on best model (Random Forest)
    print("\n[4/4] Running SHAP analysis...")
    drop_cols = {"risk_label"}
    feature_cols = [c for c in df_feat.columns if c not in drop_cols]
    X = df_feat[feature_cols].values
    y = df_feat["risk_label"].values

    X_train, X_test, _, _ = train_test_split(
        X, y, test_size=0.2, stratify=y,
        random_state=cfg["data"]["random_state"]
    )
    scaler = joblib.load("models/feature_scaler.pkl")
    model = joblib.load("models/random_forest.pkl")
    X_train_sc = scaler.transform(X_train)
    X_test_sc = scaler.transform(X_test)

    run_shap_analysis(model, scaler, X_train_sc, X_test_sc,
                      feature_cols, cfg["paths"]["shap_dir"])

    print("\n" + "=" * 60)
    print("  [OK] Pipeline complete! Run the app with:")
    print("     streamlit run app/streamlit_app.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
