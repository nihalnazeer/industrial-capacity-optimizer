"""
metrics.py

KPI computation for comparing deterministic vs. scenario-based
capacity plans: cost, overtime, utilization, fulfillment,
unmet demand, and worst-case scenario cost.
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