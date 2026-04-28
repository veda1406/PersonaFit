"""
Model training module for PersonaFit.
Trains Logistic Regression, SVM, Random Forest, Naive Bayes.
Logs everything to MLflow and saves metrics to results/metrics.json.
"""

import os
import json
import warnings
import yaml
import numpy as np
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import (train_test_split, StratifiedKFold,
                                      cross_val_score, GridSearchCV)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.metrics import (accuracy_score, classification_report,
                              roc_auc_score, confusion_matrix,
                              precision_recall_curve, average_precision_score)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

warnings.filterwarnings("ignore")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_config(path="configs/config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def get_feature_cols(df: pd.DataFrame) -> list:
    drop = {"risk_label"}
    return [c for c in df.columns if c not in drop]


def compute_metrics(model, X_test, y_test, classes) -> dict:
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True,
                                   target_names=["Low", "Medium", "High"])

    # ROC-AUC (one-vs-rest for multiclass)
    y_bin = label_binarize(y_test, classes=classes)
    try:
        proba = model.predict_proba(X_test)
        roc_auc = roc_auc_score(y_bin, proba, multi_class="ovr", average="macro")
    except Exception:
        roc_auc = None

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_f1": report["macro avg"]["f1-score"],
        "macro_precision": report["macro avg"]["precision"],
        "macro_recall": report["macro avg"]["recall"],
        "roc_auc": roc_auc,
        "report": report,
    }


def plot_confusion_matrix(model, X_test, y_test, name, out_dir):
    cm = confusion_matrix(y_test, model.predict(X_test))
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Low", "Med", "High"],
                yticklabels=["Low", "Med", "High"], ax=ax)
    ax.set_title(f"Confusion Matrix – {name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    path = os.path.join(out_dir, f"cm_{name.lower().replace(' ', '_')}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_pr_curve(model, X_test, y_test, name, out_dir):
    classes = sorted(y_test.unique())
    y_bin = label_binarize(y_test, classes=classes)
    try:
        proba = model.predict_proba(X_test)
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#2ECC71", "#F39C12", "#E74C3C"]
    labels = ["Low", "Medium", "High"]
    for i, (col, lbl) in enumerate(zip(colors, labels)):
        p, r, _ = precision_recall_curve(y_bin[:, i], proba[:, i])
        ap = average_precision_score(y_bin[:, i], proba[:, i])
        ax.plot(r, p, color=col, lw=2, label=f"{lbl} (AP={ap:.2f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"Precision–Recall Curve – {name}")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, f"pr_{name.lower().replace(' ', '_')}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_calibration(model, X_test, y_test, name, out_dir):
    classes = sorted(y_test.unique())
    y_bin = label_binarize(y_test, classes=classes)
    try:
        proba = model.predict_proba(X_test)
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ["#2ECC71", "#F39C12", "#E74C3C"]
    labels = ["Low", "Medium", "High"]
    for i, (col, lbl) in enumerate(zip(colors, labels)):
        frac_pos, mean_pred = calibration_curve(y_bin[:, i], proba[:, i], n_bins=10)
        ax.plot(mean_pred, frac_pos, marker="o", color=col, label=lbl)
    ax.plot([0, 1], [0, 1], "k--", label="Perfect")
    ax.set_title(f"Calibration Curve – {name}")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, f"cal_{name.lower().replace(' ', '_')}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


# ─── Model definitions ───────────────────────────────────────────────────────

def build_models(cfg) -> dict:
    rc = cfg["models"]
    rs = rc["random_state"]

    svm_base = SVC(kernel="rbf", probability=True, random_state=rs)
    svm_grid = GridSearchCV(
        svm_base,
        param_grid={"C": [0.1, 1, 10], "gamma": ["scale", "auto"]},
        cv=3, scoring="f1_macro", n_jobs=-1, verbose=0
    )

    return {
        "Logistic Regression": LogisticRegression(
            max_iter=rc["logistic_regression"]["max_iter"],
            C=rc["logistic_regression"]["C"],
            random_state=rs),
        "SVM (RBF)": svm_grid,
        "Random Forest": RandomForestClassifier(
            n_estimators=rc["random_forest"]["n_estimators"],
            max_depth=rc["random_forest"]["max_depth"],
            random_state=rs, n_jobs=-1),
        "Naive Bayes": GaussianNB(),
    }


# ─── Main training pipeline ──────────────────────────────────────────────────

def train(config_path="configs/config.yaml"):
    cfg = load_config(config_path)
    os.makedirs(cfg["paths"]["models_dir"], exist_ok=True)
    os.makedirs(cfg["paths"]["results_dir"], exist_ok=True)
    os.makedirs(cfg["paths"]["shap_dir"], exist_ok=True)

    # Load data
    df = pd.read_csv(cfg["data"]["features_path"])
    feature_cols = get_feature_cols(df)
    X = df[feature_cols]
    y = df["risk_label"]
    classes = sorted(y.unique())

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=cfg["data"]["test_size"],
        stratify=y,
        random_state=cfg["data"]["random_state"]
    )

    # Scale
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    joblib.dump(scaler, os.path.join(cfg["paths"]["models_dir"], "feature_scaler.pkl"))
    joblib.dump(feature_cols, os.path.join(cfg["paths"]["models_dir"], "feature_cols.pkl"))

    # MLflow
    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    models = build_models(cfg)
    all_metrics = {}
    best_f1 = -1
    best_name = None

    cv = StratifiedKFold(n_splits=cfg["models"]["cv_folds"], shuffle=True,
                         random_state=cfg["data"]["random_state"])

    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"  Training: {name}")
        print(f"{'='*50}")

        with mlflow.start_run(run_name=name):
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_sc, y_train,
                                        cv=cv, scoring="f1_macro", n_jobs=-1)
            print(f"  CV F1 (macro): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

            # Fit
            model.fit(X_train_sc, y_train)
            metrics = compute_metrics(model, X_test_sc, y_test, classes)
            metrics["cv_f1_mean"] = float(cv_scores.mean())
            metrics["cv_f1_std"] = float(cv_scores.std())

            # Log to MLflow
            mlflow.log_param("model", name)
            mlflow.log_metrics({
                "accuracy": metrics["accuracy"],
                "macro_f1": metrics["macro_f1"],
                "macro_precision": metrics["macro_precision"],
                "macro_recall": metrics["macro_recall"],
                **({"roc_auc": metrics["roc_auc"]} if metrics["roc_auc"] else {}),
                "cv_f1_mean": metrics["cv_f1_mean"],
            })
            mlflow.sklearn.log_model(model, artifact_path="model")

            # Save plots
            cm_path = plot_confusion_matrix(model, X_test_sc, y_test, name,
                                            cfg["paths"]["results_dir"])
            pr_path = plot_pr_curve(model, X_test_sc, y_test, name,
                                    cfg["paths"]["results_dir"])
            cal_path = plot_calibration(model, X_test_sc, y_test, name,
                                        cfg["paths"]["results_dir"])

            for p in [cm_path, pr_path, cal_path]:
                if p:
                    mlflow.log_artifact(p)

            # Save model
            safe = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            model_path = os.path.join(cfg["paths"]["models_dir"], f"{safe}.pkl")
            joblib.dump(model, model_path)

            all_metrics[name] = {k: v for k, v in metrics.items() if k != "report"}
            print(f"  Accuracy : {metrics['accuracy']:.4f}")
            print(f"  Macro F1 : {metrics['macro_f1']:.4f}")
            if metrics["roc_auc"]:
                print(f"  ROC-AUC  : {metrics['roc_auc']:.4f}")

            if metrics["macro_f1"] > best_f1:
                best_f1 = metrics["macro_f1"]
                best_name = name

    # Save metrics JSON
    metrics_path = os.path.join(cfg["paths"]["results_dir"], "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\n[DONE] Metrics saved -> {metrics_path}")
    print(f"[BEST] Best model: {best_name} (F1={best_f1:.4f})")

    return all_metrics, best_name


if __name__ == "__main__":
    train()
