"""
streamlit_app.py

Interactive dashboard comparing the deterministic and
scenario-based capacity plans.
"""

import sys
from pathlib import Path

import streamlit as st
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from evaluate import run_comparison

st.set_page_config(page_title="Industrial Capacity Optimizer", layout="wide")

st.title("Industrial Capacity & Resource Planning Optimizer")
st.caption("Deterministic vs. Scenario-Based Planning under Demand Uncertainty")

data_dir = Path(__file__).resolve().parent.parent / "data"
comparison = run_comparison(data_dir)

st.subheader("KPI Comparison")
st.dataframe(comparison.style.format("{:.2f}"))

metrics_to_plot = [
    "production_cost", "overtime_hours", "capacity_utilization",
    "unmet_demand_expected", "demand_fulfillment_rate", "worst_case_cost",
]

st.subheader("Deterministic vs. Scenario-Based")
cols = st.columns(3)
for i, metric in enumerate(metrics_to_plot):
    with cols[i % 3]:
        fig, ax = plt.subplots(figsize=(4, 3))
        comparison.loc[metric].plot(kind="bar", ax=ax, color=["#4C72B0", "#55A868"])
        ax.set_title(metric.replace("_", " ").title())
        ax.set_ylabel("")
        st.pyplot(fig)