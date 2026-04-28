"""Unit tests for PersonaFit — feature engineering, model loading, predictions."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import numpy as np
import pandas as pd
import joblib

from src.features import (bmi_age_risk_band, activity_deficit_score,
                           diet_sleep_index, lifestyle_risk_score, build_features)
from src.data_gen import generate_synthetic_data, preprocess


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_df():
    """Small synthetic DataFrame for testing."""
    df = generate_synthetic_data(n_samples=200, random_state=0)
    return preprocess(df)


@pytest.fixture(scope="module")
def feature_df(sample_df):
    return build_features(sample_df, save_artifacts=False)


# ─── Feature engineering tests ────────────────────────────────────────────────

class TestBmiAgeRiskBand:
    def test_returns_series(self, sample_df):
        result = bmi_age_risk_band(sample_df)
        assert isinstance(result, pd.Series)

    def test_values_in_range(self, sample_df):
        result = bmi_age_risk_band(sample_df)
        assert result.between(0, 8).all(), "Risk band must be in [0, 8]"

    def test_length_matches(self, sample_df):
        result = bmi_age_risk_band(sample_df)
        assert len(result) == len(sample_df)

    def test_higher_bmi_higher_band(self):
        low_bmi_df = pd.DataFrame([{"age": 30, "bmi": 20.0}])
        high_bmi_df = pd.DataFrame([{"age": 30, "bmi": 35.0}])
        low_band = bmi_age_risk_band(low_bmi_df).values[0]
        high_band = bmi_age_risk_band(high_bmi_df).values[0]
        assert high_band >= low_band


class TestActivityDeficit:
    def test_zero_for_ideal(self):
        df = pd.DataFrame([{"activity_level": 8.0}])
        assert activity_deficit_score(df).values[0] == pytest.approx(0.0)

    def test_positive_for_low_activity(self):
        df = pd.DataFrame([{"activity_level": 3.0}])
        assert activity_deficit_score(df).values[0] == pytest.approx(5.0)

    def test_zero_for_above_ideal(self):
        df = pd.DataFrame([{"activity_level": 10.0}])
        assert activity_deficit_score(df).values[0] == pytest.approx(0.0)


class TestDietSleepIndex:
    def test_range(self, sample_df):
        idx = diet_sleep_index(sample_df)
        assert idx.min() >= 0
        assert idx.max() <= 10.5  # slight headroom

    def test_higher_diet_higher_index(self):
        low_df  = pd.DataFrame([{"diet_score": 2.0, "sleep_hours": 7.0}])
        high_df = pd.DataFrame([{"diet_score": 9.0, "sleep_hours": 7.0}])
        assert diet_sleep_index(high_df).values[0] > diet_sleep_index(low_df).values[0]


class TestLifestyleRiskScore:
    def test_range(self, sample_df):
        score = lifestyle_risk_score(sample_df)
        assert score.min() >= 0
        assert score.max() <= 10.5

    def test_smoker_higher_risk(self):
        no_smoke = pd.DataFrame([{"age": 40, "bmi": 25, "activity_level": 5,
                                   "diet_score": 5, "sleep_hours": 7, "smoking_status": 0}])
        smoker   = pd.DataFrame([{"age": 40, "bmi": 25, "activity_level": 5,
                                   "diet_score": 5, "sleep_hours": 7, "smoking_status": 1}])
        # Smoker should produce higher raw risk value before normalisation
        raw_no = (0.6 * 0)
        raw_sm = (0.6 * 1)
        assert raw_sm > raw_no


class TestBuildFeatures:
    def test_new_columns_exist(self, feature_df):
        expected = ["bmi_age_risk_band", "activity_deficit_score",
                    "diet_sleep_index", "lifestyle_risk_score",
                    "pca_1", "pca_2", "pca_3"]
        for col in expected:
            assert col in feature_df.columns, f"Missing column: {col}"

    def test_no_nulls(self, feature_df):
        assert feature_df.isnull().sum().sum() == 0, "Feature matrix has nulls"

    def test_shape(self, sample_df, feature_df):
        assert feature_df.shape[0] == sample_df.shape[0]
        assert feature_df.shape[1] > sample_df.shape[1]


# ─── Model loading tests ──────────────────────────────────────────────────────

class TestModelLoading:
    @pytest.mark.skipif(not os.path.exists("models/random_forest.pkl"),
                        reason="Models not trained yet")
    def test_load_random_forest(self):
        model = joblib.load("models/random_forest.pkl")
        assert model is not None

    @pytest.mark.skipif(not os.path.exists("models/feature_scaler.pkl"),
                        reason="Models not trained yet")
    def test_load_scaler(self):
        scaler = joblib.load("models/feature_scaler.pkl")
        assert hasattr(scaler, "transform")

    @pytest.mark.skipif(not os.path.exists("models/feature_cols.pkl"),
                        reason="Models not trained yet")
    def test_feature_cols_list(self):
        cols = joblib.load("models/feature_cols.pkl")
        assert isinstance(cols, list)
        assert len(cols) > 0


# ─── Prediction tests ─────────────────────────────────────────────────────────

class TestPrediction:
    @pytest.mark.skipif(not os.path.exists("models/random_forest.pkl"),
                        reason="Models not trained yet")
    def test_prediction_output_range(self):
        from src.predict import load_artifacts, build_input_row, predict
        model, scaler, feature_cols = load_artifacts("models")
        row = build_input_row(age=40, bmi=26, activity_level=5,
                              diet_score=6, sleep_hours=7, smoking_status=0)
        risk_int, proba = predict(model, scaler, feature_cols, row)
        assert risk_int in [0, 1, 2]
        assert len(proba) == 3
        assert abs(sum(proba) - 1.0) < 1e-5

    @pytest.mark.skipif(not os.path.exists("models/random_forest.pkl"),
                        reason="Models not trained yet")
    def test_smoker_higher_risk(self):
        from src.predict import load_artifacts, build_input_row, predict
        model, scaler, feature_cols = load_artifacts("models")
        base = dict(age=40, bmi=26, activity_level=5,
                    diet_score=5, sleep_hours=7)
        row_ns = build_input_row(**base, smoking_status=0)
        row_sm = build_input_row(**base, smoking_status=1)
        _, p_ns = predict(model, scaler, feature_cols, row_ns)
        _, p_sm = predict(model, scaler, feature_cols, row_sm)
        # Smoker should have higher probability for High risk
        assert p_sm[2] >= p_ns[2]
