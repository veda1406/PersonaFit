"""
PersonaFit — Streamlit Application
A friendly, non-intimidating health risk prediction interface.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import json
import joblib
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from src.predict import (load_artifacts, build_input_row, predict,
                          simulate_improvement, RISK_LABELS, RISK_COLORS, RISK_EMOJI)

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PersonaFit — Health Risk Intelligence",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%); }

/* Hero */
.hero-box {
    background: linear-gradient(135deg, #1a2744 0%, #0d2137 100%);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #68d391);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-sub {
    color: #a0aec0;
    font-size: 1.05rem;
    margin-top: 0.6rem;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}
.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.8rem;
}

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1rem;
}
.risk-low    { background: rgba(46,204,113,0.2); color: #2ECC71; border: 1px solid #2ECC71; }
.risk-medium { background: rgba(243,156,18,0.2); color: #F39C12; border: 1px solid #F39C12; }
.risk-high   { background: rgba(231,76,60,0.2);  color: #E74C3C; border: 1px solid #E74C3C; }

/* Factor pill */
.factor-pill {
    display: inline-block;
    background: rgba(99,179,237,0.15);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    margin: 0.2rem;
    font-size: 0.85rem;
    color: #90cdf4;
}

/* Metric chip */
.metric-chip {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    text-align: center;
}
.metric-chip .val { font-size: 1.4rem; font-weight: 700; color: #68d391; }
.metric-chip .lbl { font-size: 0.78rem; color: #718096; }

/* Section header */
.section-header {
    font-size: 1.3rem;
    font-weight: 600;
    color: #e2e8f0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid rgba(99,179,237,0.3);
    margin-bottom: 1rem;
}

/* Stbutton overrides */
div.stButton > button {
    background: linear-gradient(135deg, #3182ce, #2b6cb0);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.8rem;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.85; }

/* Slider labels */
.slider-label { color: #a0aec0; font-size: 0.82rem; margin-bottom: -0.5rem; }

.tip-box {
    background: rgba(104,211,145,0.08);
    border-left: 4px solid #68d391;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    color: #c6f6d5;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Load models ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models():
    try:
        model, scaler, feature_cols = load_artifacts("models")
        metrics = {}
        if os.path.exists("results/metrics.json"):
            with open("results/metrics.json") as f:
                metrics = json.load(f)
        return model, scaler, feature_cols, metrics, True
    except Exception as e:
        return None, None, None, {}, False


model, scaler, feature_cols, metrics, models_ready = load_models()


# ─── Session state ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
  <p class="hero-title">💚 PersonaFit</p>
  <p class="hero-sub">
    Your personalised health risk companion — understand your lifestyle,<br>
    see what matters most, and discover simple steps to feel better.
  </p>
</div>
""", unsafe_allow_html=True)

if not models_ready:
    st.error("⚠️ Models not found. Please run `python run_pipeline.py` first to train the models.")
    st.stop()


# ─── Layout: two columns ──────────────────────────────────────────────────────
left, right = st.columns([1, 1.4], gap="large")


# ══════════════════════════════════════════════════════════════════════════════
# LEFT — Input panel
# ══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<p class="section-header">📋 Tell us about yourself</p>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<p class="slider-label">🎂 Your age</p>', unsafe_allow_html=True)
        age = st.slider("Age", 15, 75, 35, label_visibility="collapsed")

        st.markdown('<p class="slider-label">⚖️ Your BMI (Body Mass Index)</p>', unsafe_allow_html=True)
        bmi = st.slider("BMI", 15.0, 50.0, 24.0, 0.1, label_visibility="collapsed")

        bmi_note = ("Underweight" if bmi < 18.5 else
                    "Healthy weight" if bmi < 25 else
                    "Overweight" if bmi < 30 else "Obese")
        st.caption(f"BMI category: **{bmi_note}**")

        st.markdown('<p class="slider-label">🏃 Physical Activity (0 = none · 10 = very active)</p>', unsafe_allow_html=True)
        activity = st.slider("Activity", 0.0, 10.0, 5.0, 0.5, label_visibility="collapsed")

        st.markdown('<p class="slider-label">🥗 Diet Quality (0 = poor · 10 = excellent)</p>', unsafe_allow_html=True)
        diet = st.slider("Diet", 0.0, 10.0, 5.0, 0.5, label_visibility="collapsed")

        st.markdown('<p class="slider-label">😴 Sleep Hours per night</p>', unsafe_allow_html=True)
        sleep = st.slider("Sleep", 3.0, 12.0, 7.0, 0.5, label_visibility="collapsed")

        smoking = st.radio(
            "🚬 Do you smoke?",
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            horizontal=True,
        )

    predict_btn = st.button("🔍 Analyse My Health Risk", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — Results panel
# ══════════════════════════════════════════════════════════════════════════════
with right:
    if predict_btn or st.session_state.get("last_inputs"):

        # Build row & predict
        inputs = dict(age=age, bmi=bmi, activity_level=activity,
                      diet_score=diet, sleep_hours=sleep,
                      smoking_status=smoking)
        row = build_input_row(**inputs)
        risk_int, proba = predict(model, scaler, feature_cols, row)
        risk_name = RISK_LABELS[risk_int]
        risk_color = RISK_COLORS[risk_int]
        risk_em = RISK_EMOJI[risk_int]

        # Save to state
        st.session_state.last_inputs = inputs
        if predict_btn:
            st.session_state.history.append({
                "time": datetime.now().strftime("%H:%M"),
                "risk": risk_int,
                "label": risk_name,
                "score": round(float(proba[risk_int]) * 100, 1),
            })

        # ── Risk gauge ──────────────────────────────────────────────────────
        st.markdown('<p class="section-header">🎯 Your Health Risk Level</p>',
                    unsafe_allow_html=True)

        badge_cls = f"risk-{risk_name.lower()}"
        st.markdown(f"""
        <div class="card" style="text-align:center">
          <div style="font-size:3.5rem">{risk_em}</div>
          <div class="risk-badge {badge_cls}" style="margin:0.5rem auto; display:inline-block">
            {risk_name} Risk
          </div>
          <p style="color:#a0aec0; margin-top:0.6rem; font-size:0.9rem">
            Model confidence: <strong style="color:{risk_color}">{proba[risk_int]*100:.0f}%</strong>
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Probability bar chart
        fig_gauge = go.Figure(go.Bar(
            x=["Low", "Medium", "High"],
            y=[proba[0]*100, proba[1]*100, proba[2]*100],
            marker_color=["#2ECC71", "#F39C12", "#E74C3C"],
            text=[f"{v*100:.0f}%" for v in proba],
            textposition="auto",
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0",
            margin=dict(l=10, r=10, t=10, b=30),
            height=200,
            yaxis=dict(range=[0, 100], showgrid=False, title="Likelihood (%)"),
            xaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # ── Plain-language explanation ────────────────────────────────────
        explanations = {
            0: ("Great news! Based on your lifestyle, your health risk is currently **low**. "
                "Keep up the good habits — you're on the right track! 🎉"),
            1: ("Your lifestyle shows some areas of concern. A few targeted changes — "
                "like moving more or sleeping better — could significantly lower your risk. 💪"),
            2: ("Your current lifestyle patterns suggest a **higher risk** of health issues. "
                "This is a signal to make some meaningful changes — small, consistent steps "
                "can make a big difference. 🌱"),
        }
        st.info(explanations[risk_int])

        st.divider()

        # ── Why this result? (Top 3 factors) ─────────────────────────────
        st.markdown('<p class="section-header">🔍 Why this result?</p>',
                    unsafe_allow_html=True)

        # Simple rule-based factor importance (user-friendly)
        factor_scores = {
            "Physical Activity": (10 - activity) / 10,
            "Diet Quality": (10 - diet) / 10,
            "BMI": max(0, (bmi - 22) / 28),
            "Sleep Hours": max(0, abs(sleep - 7.5) / 4.5),
            "Age": (age - 15) / 60,
            "Smoking": float(smoking),
        }
        top3 = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        factor_tips = {
            "Physical Activity": "Low activity is a major driver of health risk.",
            "Diet Quality": "Poor diet quality raises cardiovascular and metabolic risks.",
            "BMI": "A higher BMI is linked to many chronic conditions.",
            "Sleep Hours": "Both too little and too much sleep affects health.",
            "Age": "Risk naturally increases with age, but lifestyle can counteract this.",
            "Smoking": "Smoking is one of the strongest risk factors for serious illness.",
        }

        for fname, fscore in top3:
            impact = "High impact" if fscore > 0.6 else "Moderate impact" if fscore > 0.3 else "Low impact"
            bar_color = "#E74C3C" if fscore > 0.6 else "#F39C12" if fscore > 0.3 else "#2ECC71"
            st.markdown(f"""
            <div class="card" style="margin-bottom:0.6rem">
              <div style="display:flex; justify-content:space-between; align-items:center">
                <span style="color:#e2e8f0; font-weight:600">{fname}</span>
                <span style="color:{bar_color}; font-size:0.8rem">{impact}</span>
              </div>
              <div style="background:rgba(255,255,255,0.06); border-radius:999px; height:6px; margin:0.5rem 0">
                <div style="background:{bar_color}; width:{min(fscore*100,100):.0f}%; height:6px; border-radius:999px"></div>
              </div>
              <p style="color:#718096; font-size:0.82rem; margin:0">{factor_tips[fname]}</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── What can I improve? ────────────────────────────────────────────
        st.markdown('<p class="section-header">🌱 What if I made changes?</p>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            new_activity = st.slider("🏃 Activity", 0.0, 10.0,
                                     min(activity + 2, 10.0), 0.5, key="sim_act")
        with c2:
            new_diet = st.slider("🥗 Diet", 0.0, 10.0,
                                 min(diet + 2, 10.0), 0.5, key="sim_diet")
        with c3:
            new_sleep = st.slider("😴 Sleep hrs", 3.0, 12.0,
                                  min(sleep + 1, 10.0), 0.5, key="sim_sleep")

        sim_risk_int, sim_proba = simulate_improvement(
            model, scaler, feature_cols, inputs,
            {"activity_level": new_activity, "diet_score": new_diet, "sleep_hours": new_sleep}
        )
        sim_name = RISK_LABELS[sim_risk_int]
        sim_em = RISK_EMOJI[sim_risk_int]
        delta_conf = (proba[risk_int] - sim_proba[sim_risk_int]) * 100

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-chip">
              <div class="val">{risk_em} {risk_name}</div>
              <div class="lbl">Current Risk</div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            arrow = "⬇️" if sim_risk_int < risk_int else ("⬆️" if sim_risk_int > risk_int else "➡️")
            st.markdown(f"""
            <div class="metric-chip">
              <div class="val">{sim_em} {sim_name}</div>
              <div class="lbl">After Changes {arrow}</div>
            </div>""", unsafe_allow_html=True)

        if sim_risk_int < risk_int:
            st.success(f"🎉 These changes could lower your risk from **{risk_name}** to **{sim_name}**!")
        elif sim_risk_int == risk_int:
            st.info("These changes maintain your current risk level. Try bigger adjustments!")
        else:
            st.warning("This combination would increase risk — try different values.")

        st.divider()

        # ── Recommendations ────────────────────────────────────────────────
        st.markdown('<p class="section-header">💡 Simple Steps You Can Take</p>',
                    unsafe_allow_html=True)

        recs = []
        if activity < 5:
            recs.append("🚶 Aim for a 30-minute walk daily — it's one of the most effective lifestyle changes.")
        if diet < 5:
            recs.append("🥦 Add more vegetables and whole grains to your meals, even small swaps help.")
        if sleep < 6 or sleep > 9:
            recs.append("🌙 Try to get 7–8 hours of sleep. A consistent bedtime routine really helps.")
        if smoking:
            recs.append("🚭 Quitting smoking is the single biggest improvement you can make for your health.")
        if bmi > 27:
            recs.append("⚖️ Even a 5% reduction in body weight can significantly lower health risks.")
        if not recs:
            recs.append("✅ You're doing great! Keep maintaining your healthy habits.")
            recs.append("💧 Stay well-hydrated and manage stress with mindful activities.")

        for r in recs:
            st.markdown(f'<div class="tip-box">{r}</div>', unsafe_allow_html=True)

    else:
        # Placeholder before prediction
        st.markdown("""
        <div class="card" style="text-align:center; padding:3rem 2rem">
          <div style="font-size:4rem">💚</div>
          <h3 style="color:#e2e8f0">Fill in your details</h3>
          <p style="color:#718096">
            Adjust the sliders on the left and click<br>
            <strong style="color:#63b3ed">Analyse My Health Risk</strong>
            to get your personalised report.
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Show model metrics teaser
        if metrics:
            st.markdown('<p class="section-header" style="margin-top:1rem">📊 Model Performance</p>',
                        unsafe_allow_html=True)
            rows = []
            for name, m in metrics.items():
                rows.append({
                    "Model": name,
                    "Accuracy": f"{m.get('accuracy', 0)*100:.1f}%",
                    "F1 Score": f"{m.get('macro_f1', 0)*100:.1f}%",
                    "ROC-AUC": f"{m.get('roc_auc') or 0:.3f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─── Progress tracking (sidebar-style bottom section) ─────────────────────────
if st.session_state.history and len(st.session_state.history) > 1:
    st.divider()
    st.markdown('<p class="section-header">📈 Your Session Progress</p>',
                unsafe_allow_html=True)
    hist_df = pd.DataFrame(st.session_state.history)
    color_map = {"Low": "#2ECC71", "Medium": "#F39C12", "High": "#E74C3C"}
    fig_hist = px.line(hist_df, x="time", y="score",
                       color_discrete_sequence=["#63b3ed"],
                       labels={"score": "Confidence %", "time": "Check"},
                       title="Risk Confidence Over This Session")
    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#a0aec0", height=200,
                           margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#4a5568; font-size:0.78rem; margin-top:2rem; padding:1rem">
  PersonaFit uses machine learning for educational purposes only.<br>
  This is <strong>not</strong> medical advice. Always consult a healthcare professional.
</div>
""", unsafe_allow_html=True)
