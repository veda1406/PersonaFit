"""
PersonaFit FastAPI backend.
Wraps the trained scikit-learn models and exposes REST endpoints.
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from src.predict import build_input_row, predict, simulate_improvement, RISK_LABELS
from src.features import lifestyle_risk_score

app = FastAPI(title="PersonaFit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load artifacts once at startup ────────────────────────────────────────────
MODEL = None
SCALER = None
FEATURE_COLS = None

@app.on_event("startup")
def load_models():
    global MODEL, SCALER, FEATURE_COLS
    from src.predict import load_artifacts
    MODEL, SCALER, FEATURE_COLS = load_artifacts("models")
    print("Models loaded.")


# ── Schemas ───────────────────────────────────────────────────────────────────

class LifestyleInput(BaseModel):
    age: float = Field(..., ge=15, le=75)
    bmi: float = Field(..., ge=15, le=50)
    activity_level: float = Field(..., ge=0, le=10)
    diet_score: float = Field(..., ge=0, le=10)
    sleep_hours: float = Field(..., ge=3, le=12)
    smoking_status: int = Field(..., ge=0, le=1)


class SimulateInput(LifestyleInput):
    new_activity: Optional[float] = None
    new_diet: Optional[float] = None
    new_sleep: Optional[float] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

RISK_FRIENDLY = {
    0: "You're in great shape!",
    1: "You may have some areas to improve",
    2: "You may be at higher health risk",
}

RISK_DESC = {
    0: "Your lifestyle habits look healthy overall. Keep up the good work and stay consistent.",
    1: "A few targeted changes — like moving more or sleeping better — can significantly lower your risk.",
    2: "Your current habits suggest some health risks. Small, consistent changes can make a real difference.",
}

RISK_COLOR = {0: "#8FB78F", 1: "#D98CA1", 2: "#E9B18A"}

def compute_factors(inputs: dict) -> list[dict]:
    """Rule-based top-factor computation — user-friendly, no jargon."""
    age, bmi, activity, diet, sleep, smoking = (
        inputs["age"], inputs["bmi"], inputs["activity_level"],
        inputs["diet_score"], inputs["sleep_hours"], inputs["smoking_status"],
    )
    factors = [
        {
            "name": "Physical Activity",
            "impact": round((10 - activity) / 10, 3),
            "description": "Low activity is one of the biggest drivers of health risk.",
        },
        {
            "name": "Diet Quality",
            "impact": round((10 - diet) / 10, 3),
            "description": "A poor diet raises cardiovascular and metabolic risks.",
        },
        {
            "name": "BMI",
            "impact": round(min(max((bmi - 22) / 28, 0), 1), 3),
            "description": "A higher BMI is linked to many chronic conditions.",
        },
        {
            "name": "Sleep Quality",
            "impact": round(min(abs(sleep - 7.5) / 4.5, 1), 3),
            "description": "Both too little and too much sleep affect your health.",
        },
        {
            "name": "Age",
            "impact": round((age - 15) / 60, 3),
            "description": "Risk naturally increases with age — lifestyle can counteract this.",
        },
        {
            "name": "Smoking",
            "impact": float(smoking),
            "description": "Smoking is one of the strongest risk factors for serious illness.",
        },
    ]
    factors.sort(key=lambda x: x["impact"], reverse=True)
    return factors[:3]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict_risk(body: LifestyleInput):
    inputs = body.model_dump()
    row = build_input_row(**inputs)
    risk_int, proba = predict(MODEL, SCALER, FEATURE_COLS, row)

    return {
        "risk_level": risk_int,
        "risk_label": RISK_LABELS[risk_int],
        "risk_friendly": RISK_FRIENDLY[risk_int],
        "risk_description": RISK_DESC[risk_int],
        "risk_color": RISK_COLOR[risk_int],
        "confidence": round(float(proba[risk_int]) * 100, 1),
        "probabilities": {
            "low": round(float(proba[0]) * 100, 1),
            "medium": round(float(proba[1]) * 100, 1),
            "high": round(float(proba[2]) * 100, 1),
        },
        "top_factors": compute_factors(inputs),
    }


@app.post("/simulate")
def simulate(body: SimulateInput):
    base = {
        "age": body.age,
        "bmi": body.bmi,
        "activity_level": body.activity_level,
        "diet_score": body.diet_score,
        "sleep_hours": body.sleep_hours,
        "smoking_status": body.smoking_status,
    }
    changes = {}
    if body.new_activity is not None:
        changes["activity_level"] = body.new_activity
    if body.new_diet is not None:
        changes["diet_score"] = body.new_diet
    if body.new_sleep is not None:
        changes["sleep_hours"] = body.new_sleep

    sim_risk_int, sim_proba = simulate_improvement(
        MODEL, SCALER, FEATURE_COLS, base, changes
    )
    return {
        "risk_level": sim_risk_int,
        "risk_label": RISK_LABELS[sim_risk_int],
        "risk_friendly": RISK_FRIENDLY[sim_risk_int],
        "risk_color": RISK_COLOR[sim_risk_int],
        "confidence": round(float(sim_proba[sim_risk_int]) * 100, 1),
        "health_score": round(float(sim_proba[0]) * 100),
    }
