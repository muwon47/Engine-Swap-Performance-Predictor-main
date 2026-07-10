from __future__ import annotations

import pandas as pd
import streamlit as st

from src.dataset import BASE_ENGINES, CHASSIS
from src.predictor import EngineSwapPredictor


st.set_page_config(
    page_title="Engine Swap Performance Predictor",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #0b1020; color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc; }
    [data-testid="stMetricValue"] { color: #60a5fa; }
    .small-note { color: #94a3b8; font-size: 0.95rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_predictor() -> EngineSwapPredictor:
    return EngineSwapPredictor()


predictor = get_predictor()
metadata = predictor.metadata()
engine_options = {f"{engine['name']} ({engine['code']})": engine["code"] for engine in BASE_ENGINES}
chassis_options = {f"{chassis['name']} ({chassis['code']})": chassis["code"] for chassis in CHASSIS}

st.title("🏎️ Engine Swap Performance Predictor")
st.caption("Predict horsepower, torque, 0–60 mph, compatibility, feature importance, and tuning tips for common engine swap combinations.")

with st.sidebar:
    st.header("Swap Configuration")
    engine_label = st.selectbox("Donor engine", list(engine_options.keys()))
    chassis_label = st.selectbox("Recipient chassis", list(chassis_options.keys()))
    tune_level = st.slider("Tune level", 0.0, 1.0, 0.65, 0.05)
    cooling_capacity_index = st.slider("Cooling readiness", 0.0, 1.0, 0.74, 0.05)
    tire_grip_index = st.slider("Tire grip", 0.0, 1.0, 0.78, 0.05)
    suspension_index = st.slider("Suspension readiness", 0.0, 1.0, 0.72, 0.05)
    gear_ratio = st.slider("Final drive / gear ratio", 3.20, 4.80, 4.30, 0.05)
    run_prediction = st.button("Predict Swap", type="primary", use_container_width=True)

payload = {
    "engine_code": engine_options[engine_label],
    "chassis_code": chassis_options[chassis_label],
    "tune_level": tune_level,
    "cooling_capacity_index": cooling_capacity_index,
    "tire_grip_index": tire_grip_index,
    "suspension_index": suspension_index,
    "gear_ratio": gear_ratio,
}

if run_prediction or True:
    result = predictor.predict(payload)
    predictions = result["predictions"]
    compatibility = result["compatibility"]

    st.subheader("Prediction")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Horsepower", f"{predictions['horsepower']:.1f} hp")
    col2.metric("Torque", f"{predictions['torque_nm']:.1f} Nm")
    col3.metric("0–60 mph", f"{predictions['zero_to_sixty_s']:.2f} s")
    col4.metric("Compatibility", f"{compatibility['score']:.1f}/100", compatibility["label"])

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Compatibility Breakdown")
        breakdown_df = pd.DataFrame(
            [{"factor": key.replace("_", " ").title(), "score": value} for key, value in compatibility["breakdown"].items()]
        )
        st.bar_chart(breakdown_df, x="factor", y="score", height=320)

    with right:
        st.subheader("Feature Importance")
        importance_df = pd.DataFrame(result["feature_importance"])
        if not importance_df.empty:
            name_col = "feature" if "feature" in importance_df.columns else importance_df.columns[0]
            value_col = "importance" if "importance" in importance_df.columns else importance_df.columns[-1]
            importance_df = importance_df[[name_col, value_col]].head(12)
            st.bar_chart(importance_df, x=name_col, y=value_col, height=320)
        else:
            st.info("Feature importance is unavailable for this model.")

    st.subheader("Tuning Tips")
    for tip in result["tuning_tips"]:
        st.write(f"- {tip}")

    with st.expander("Confidence Intervals"):
        st.json(result["confidence_intervals"])

st.divider()

st.subheader("Compare Donor Engines")
compare_payload = dict(payload)
compare_payload["candidate_engines"] = [engine["code"] for engine in BASE_ENGINES]
comparison = predictor.compare(compare_payload)
comparison_df = pd.DataFrame(
    [
        {
            "Rank": row["rank"],
            "Engine": row["engine"]["name"],
            "HP": row["predictions"]["horsepower"],
            "0-60 s": row["predictions"]["zero_to_sixty_s"],
            "Compatibility": row["compatibility_score"],
            "Rank Score": row["rank_score"],
        }
        for row in comparison["candidates"]
    ]
)
st.dataframe(comparison_df, hide_index=True, use_container_width=True)

with st.expander("Project Metadata"):
    st.write(f"Training rows: {metadata['training_rows']}")
    st.write(f"Hybrid ML artifact active: {metadata['hybrid_ml_active']}")
    st.write(metadata["demo_note"])