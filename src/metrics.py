"""
metrics.py

KPI computation for comparing deterministic vs. scenario-based
capacity plans: cost, overtime, utilization, fulfillment,
unmet demand, and worst-case scenario cost. Also includes
helpers that reshape production plans for visualization
(machine-level utilization, machine x job production matrix).
"""

from __future__ import annotations

import pandas as pd


def production_cost(production_df: pd.DataFrame, machines_df: pd.DataFrame) -> float:
    """Total regular + overtime production cost for a solved plan."""
    machine_params = machines_df.set_index("machine_id")
    merged = production_df.merge(machine_params, left_on="machine", right_index=True)
    return float(
        (merged["regular_units"] * merged["regular_cost"]).sum()
        + (merged["overtime_units"] * merged["overtime_cost"]).sum()
    )


def overtime_hours(production_df: pd.DataFrame) -> float:
    """Total overtime units scheduled across the plan."""
    return float(production_df["overtime_units"].sum())


def capacity_utilization(production_df: pd.DataFrame, machines_df: pd.DataFrame) -> float:
    """
    Utilization = (regular + overtime production) / (available regular + overtime capacity).
    Overtime is included in both numerator and denominator so overtime-heavy
    plans aren't misreported as low utilization.
    """
    used = production_df["regular_units"].sum() + production_df["overtime_units"].sum()
    n_periods = production_df["period"].nunique()
    available = (
        (machines_df["regular_capacity"] + machines_df["overtime_capacity"]).sum() * n_periods
    )
    return float(100 * used / available) if available > 0 else 0.0


def demand_fulfillment_rate(total_demand: float, total_unmet: float) -> float:
    """Percentage of total demand actually satisfied."""
    if total_demand == 0:
        return 100.0
    return float(100 * (total_demand - total_unmet) / total_demand)


def worst_case_cost(scenario_costs: dict) -> float:
    """Highest total cost (production + unmet penalty) across evaluated scenarios."""
    return float(max(scenario_costs.values()))


def utilization_by_machine(production_df: pd.DataFrame, machines_df: pd.DataFrame) -> pd.DataFrame:
    """
    Utilization percentage per individual machine, for gauge/bar
    visualizations (as opposed to the single aggregate figure
    from capacity_utilization()).
    """
    machine_params = machines_df.set_index("machine_id")
    n_periods = production_df["period"].nunique()
    rows = []
    for m, row in machine_params.iterrows():
        used = production_df.loc[
            production_df["machine"] == m, ["regular_units", "overtime_units"]
        ].sum().sum()
        available = (row["regular_capacity"] + row["overtime_capacity"]) * n_periods
        utilization = float(100 * used / available) if available > 0 else 0.0
        rows.append({"machine": m, "utilization": utilization})
    return pd.DataFrame(rows)


def production_matrix(production_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot total production units (regular + overtime, summed across periods)
    into a machine x job matrix — the shape needed for a heatmap or
    3D surface plot of the allocation.
    """
    df = production_df.copy()
    df["total_units"] = df["regular_units"] + df["overtime_units"]
    matrix = df.groupby(["machine", "job"])["total_units"].sum().unstack(fill_value=0)
    return matrix