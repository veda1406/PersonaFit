# 💚 PersonaFit — Personalized Fitness & Lifestyle Risk Intelligence System

> A full-stack machine learning application that predicts your health risk level and guides you with actionable, plain-language recommendations.

---

## 🎯 Problem Statement

Millions of people live with preventable health risks — poor diet, sedentary lifestyle, smoking — but have no easy way to understand *how* their habits affect their long-term health. PersonaFit bridges this gap: it takes a few lifestyle inputs and produces a clear, explainable health risk assessment, with personalised suggestions to improve it.

---

## 🏗️ Architecture

```
User Inputs (Streamlit)
        │
        ▼
Feature Engineering Pipeline
  ├── BMI-Age Risk Band
  ├── Activity Deficit Score
  ├── Diet-Sleep Index
  ├── Lifestyle Risk Score
  └── PCA Components (3)
        │
        ▼
ML Models (scikit-learn)
  ├── Logistic Regression
  ├── SVM (RBF, GridSearchCV)
  ├── Random Forest ← Best
  └── Naive Bayes
        │
        ▼
SHAP Explainer
  ├── Global Feature Importance
  └── Local (per-prediction) Explanation
        │
        ▼
Risk Output: Low / Medium / High
  + Confidence + Top 3 Factors + Recommendations
```

---

## 📊 Model Comparison (actual results from metrics.json)

| Model               | Accuracy | Macro F1 | ROC-AUC |
|---------------------|----------|----------|---------|\
| Logistic Regression | 79.9%    | 79.6%    | 0.9356  |
| SVM (RBF)           | 78.5%    | 78.3%    | 0.9275  |
| Random Forest       | 79.5%    | 79.5%    | 0.9287  |
| Naive Bayes         | 78.5%    | 78.7%    | 0.9249  |

---

## 🚀 Quick Start (for teammates)

### Prerequisites
- Python 3.11 or later — https://www.python.org/downloads/
- Node.js 18 or later — https://nodejs.org/

### Step 1 — Clone the repo
```bash
git clone <repo-url>
cd CP
```

### Step 2 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Train all models (run once, generates models/ and data/)
```bash
python run_pipeline.py
```
This generates 5,000 synthetic samples, engineers features, trains all 4 models,
and saves artifacts to models/ and results/.

### Step 4 — Start the FastAPI backend
```bash
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```
API will be available at http://127.0.0.1:8000

### Step 5 — Start the React frontend (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 in your browser.

### Alternative — Streamlit interface (simpler, no frontend setup needed)
```bash
streamlit run app/streamlit_app.py
```
Open http://localhost:8501 in your browser.

### Step 6 — Run tests
```bash
pytest tests/ -v
```

### Step 7 — View MLflow experiment history
```bash
mlflow ui --port 5000
```

---

## 📁 Project Structure

```
personafit/
├── app/
│   └── streamlit_app.py       # Streamlit UI
├── configs/
│   └── config.yaml            # All hyperparameters & paths
├── data/
│   ├── raw/                   # Generated raw data
│   └── processed/             # Cleaned + feature-engineered data
├── models/                    # Saved model artifacts (.pkl)
├── results/
│   ├── metrics.json           # Evaluation metrics
│   ├── shap/                  # SHAP plots
│   └── *.png                  # Confusion matrices, PR curves
├── src/
│   ├── data_gen.py            # Data generation & preprocessing
│   ├── features.py            # Feature engineering
│   ├── train.py               # Model training + MLflow tracking
│   ├── explain.py             # SHAP explainability
│   └── predict.py             # Prediction utilities
├── tests/
│   └── test_features.py       # Unit tests
├── .github/workflows/ci.yml   # GitHub Actions CI
├── Dockerfile
├── Makefile
├── requirements.txt
└── run_pipeline.py            # Master pipeline script
```

---

## ✨ Key Features

- **4 ML models** compared with full evaluation metrics
- **SHAP explainability** — understand *why* a prediction was made
- **"What if?" simulator** — see how lifestyle changes affect your risk in real-time
- **MLflow tracking** — full experiment reproducibility
- **Docker-ready** — one command to containerise and deploy
- **Friendly UI** — designed for non-technical users

---

## ⚠️ Disclaimer

PersonaFit is for educational and portfolio purposes only. It does not constitute medical advice. Always consult a qualified healthcare professional for health decisions.
