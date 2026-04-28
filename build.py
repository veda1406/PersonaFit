"""
Lightweight build script for Render deployment.
Generates data, engineers features, and trains models.
Skips SHAP analysis to avoid build timeouts on free tier.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_gen import load_config, generate_synthetic_data, preprocess
from src.features import build_features
from src.train import train

def main():
    print("\n" + "=" * 60)
    print("  PersonaFit - Build Pipeline (Render)")
    print("=" * 60)

    cfg = load_config("configs/config.yaml")
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # 1. Generate & clean data
    print("\n[1/3] Generating synthetic data...")
    df_raw = generate_synthetic_data(
        n_samples=cfg["data"]["n_samples"],
        random_state=cfg["data"]["random_state"]
    )
    df_raw.to_csv(cfg["data"]["raw_path"], index=False)
    df_clean = preprocess(df_raw)
    df_clean.to_csv(cfg["data"]["processed_path"], index=False)
    print(f"  Samples: {len(df_clean)}")

    # 2. Feature engineering
    print("\n[2/3] Engineering features...")
    df_feat = build_features(df_clean)
    df_feat.to_csv(cfg["data"]["features_path"], index=False)
    print(f"  Feature matrix: {df_feat.shape}")

    # 3. Train all models
    print("\n[3/3] Training models...")
    all_metrics, best_name = train("configs/config.yaml")
    print(f"  Best model: {best_name}")

    print("\n" + "=" * 60)
    print("  [OK] Build complete! Models saved to models/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
