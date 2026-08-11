"""
streamlit_app.py

Interactive dashboard comparing the deterministic and
scenario-based capacity plans: a dynamically computed
recommendation summary, KPI cards, cost/percentage/unit metrics
on separate scales, worst-case-scenario unmet demand, and a
large machine x job allocation heatmap.
"""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from evaluate import run_comparison
from metrics import production_matrix

st.set_page_config(page_title="Industrial Capacity Optimizer", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Industrial Capacity & Resource Planning Optimizer")
st.caption("Deterministic vs. Scenario-Based Planning under Demand Uncertainty")

data_dir = Path(__file__).resolve().parent.parent / "data"
results = run_comparison(data_dir)
comparison = results["comparison"]

det = comparison["Deterministic"]
scen = comparison["Scenario-Based"]

# ---------------------------------------------------------------
# Recommendation summary — every figure here is computed directly
# from the solved results, not hardcoded, so it stays accurate if
# the underlying data changes.
# ---------------------------------------------------------------
worst_case_reduction_pct = 100 * (det["worst_case_cost"] - scen["worst_case_cost"]) / det["worst_case_cost"]
cost_increase_pct = 100 * (scen["production_cost"] - det["production_cost"]) / det["production_cost"]
unmet_reduction_pct = (
    100 * (det["unmet_demand_worst_case"] - scen["unmet_demand_worst_case"]) / det["unmet_demand_worst_case"]
    if det["unmet_demand_worst_case"] > 0 else 0
)

st.success(
    f"""
### Executive Recommendation: Scenario-Based Planning

Both planning strategies satisfy **100% of demand under the expected-demand forecast**.
However, they behave very differently when demand increases.

Under the **{det['worst_case_scenario'].title()}-Demand Scenario**:

- **Deterministic Plan:** **{det['unmet_demand_worst_case']:.0f} units** of unmet demand
- **Scenario-Based Plan:** **{scen['unmet_demand_worst_case']:.0f} units** of unmet demand
- **Reduction in Unmet Demand:** **{unmet_reduction_pct:.0f}%**

This translates into a **{worst_case_reduction_pct:.0f}% reduction in worst-case operating cost**
(from **${det['worst_case_cost']:,.0f}** to **${scen['worst_case_cost']:,.0f}**),
while requiring a **{cost_increase_pct:.0f}% increase in expected production cost**
(from **${det['production_cost']:,.0f}** to **${scen['production_cost']:,.0f}**).

**Business Interpretation**

The deterministic model minimizes expected operating cost when the forecast is accurate.
The scenario-based model deliberately allocates additional capacity and overtime,
accepting a modest increase in expected production cost in exchange for substantially
greater resilience under demand uncertainty.
"""
)
st.divider()

# ---------------------------------------------------------------
# KPI cards — shown side by side per plan, no colored delta
# (a "cheaper" or "lower" number here isn't automatically the
# better choice, so red/green would misleadingly imply a winner)
# ---------------------------------------------------------------
st.subheader("Key Metrics")

kpi_col1, kpi_col2 = st.columns(2)

with kpi_col1:
    st.markdown("**Deterministic**")
    a, b = st.columns(2)
    a.metric("Production Cost", f"${det['production_cost']:,.0f}")
    b.metric("Worst-Case Cost", f"${det['worst_case_cost']:,.0f}")
    a.metric("Utilization", f"{det['capacity_utilization']:.1f}%")
    b.metric("Fulfillment (Expected)", f"{det['demand_fulfillment_rate']:.1f}%")
    st.caption(f"Unmet demand under {det['worst_case_scenario']}-demand scenario: {det['unmet_demand_worst_case']:.0f} units")

with kpi_col2:
    st.markdown("**Scenario-Based**")
    a, b = st.columns(2)
    a.metric("Production Cost", f"${scen['production_cost']:,.0f}")
    b.metric("Worst-Case Cost", f"${scen['worst_case_cost']:,.0f}")
    a.metric("Utilization", f"{scen['capacity_utilization']:.1f}%")
    b.metric("Fulfillment (Expected)", f"{scen['demand_fulfillment_rate']:.1f}%")
    st.caption(f"Unmet demand under {scen['worst_case_scenario']}-demand scenario: {scen['unmet_demand_worst_case']:.0f} units")

st.divider()

# ---------------------------------------------------------------
# Full KPI table
# ---------------------------------------------------------------
st.subheader("Full Comparison")
display_table = comparison.drop(index="worst_case_scenario")
st.dataframe(display_table.style.format("{:.2f}"), use_container_width=True)

st.divider()

# ---------------------------------------------------------------
# Cost metrics and percentage metrics on separate charts —
# plotting them together made the percentage metrics invisible
# next to cost figures in the thousands.
# ---------------------------------------------------------------
st.subheader("Metric Comparison")

cost_metrics = ["production_cost", "worst_case_cost"]
pct_metrics = ["capacity_utilization", "demand_fulfillment_rate"]
count_metrics = ["overtime_hours", "unmet_demand_worst_case"]


def grouped_bar(metric_list, title):
    df = (
        comparison.loc[metric_list]
        .reset_index()
        .melt(id_vars="index", var_name="Plan", value_name="Value")
        .rename(columns={"index": "Metric"})
    )
    fig = px.bar(
        df, x="Metric", y="Value", color="Plan", barmode="group",
        template="plotly_dark", title=title,
        color_discrete_sequence=["#4C72B0", "#55A868"],
    )
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
    return fig


col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(grouped_bar(cost_metrics, "Cost ($)"), use_container_width=True)
with col2:
    st.plotly_chart(grouped_bar(pct_metrics, "Percentage (%)"), use_container_width=True)
with col3:
    st.plotly_chart(grouped_bar(count_metrics, "Units (Overtime / Worst-Case Unmet)"), use_container_width=True)

st.divider()

# ---------------------------------------------------------------
# Allocation heatmap — the clearest visualization of what the
# optimizer actually decided, so it gets the most screen space.
# ---------------------------------------------------------------
st.subheader("Machine x Job Allocation Heatmap")
plan_choice = st.radio("Plan", ["Deterministic", "Scenario-Based"], horizontal=True)
plan_key = "deterministic_plan" if plan_choice == "Deterministic" else "scenario_plan"

matrix = production_matrix(results[plan_key])

fig_heatmap = px.imshow(
    matrix,
    text_auto=True,
    color_continuous_scale="Plasma",
    labels=dict(x="Job", y="Machine", color="Units"),
    template="plotly_dark",
    aspect="auto",
)
fig_heatmap.update_layout(height=520, margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig_heatmap, use_container_width=True)