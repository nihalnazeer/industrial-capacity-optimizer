"""
model.py

LP/IP formulation for the Capacity & Resource Planning Optimizer.
Builds both the deterministic (single-scenario) model and the
scenario-based (multi-scenario) model using PuLP.
"""

from __future__ import annotations

import pulp
import pandas as pd


UNMET_PENALTY = 1000  # pi: large penalty per unit of unmet demand


def build_deterministic_model(
    jobs_df: pd.DataFrame,
    machines_df: pd.DataFrame,
):
    """
    Build the deterministic model, planning only against the
    'expected' demand baseline in jobs_df.

    Returns
    -------
    problem : pulp.LpProblem
    variables : dict of decision variables, for result extraction
    """
    jobs = jobs_df["job_id"].unique()
    periods = jobs_df["period"].unique()
    machines = machines_df["machine_id"].unique()

    problem = pulp.LpProblem("Deterministic_Capacity_Plan", pulp.LpMinimize)

    x = {
        (j, m, t): pulp.LpVariable(f"x_{j}_{m}_{t}", lowBound=0)
        for j in jobs for m in machines for t in periods
    }
    y = {
        (j, m, t): pulp.LpVariable(f"y_{j}_{m}_{t}", lowBound=0)
        for j in jobs for m in machines for t in periods
    }
    u = {
        (j, t): pulp.LpVariable(f"u_{j}_{t}", lowBound=0)
        for j in jobs for t in periods
    }

    machine_params = machines_df.set_index("machine_id")
    demand = jobs_df.set_index(["job_id", "period"])["demand_expected"]

    # Objective: minimize regular + overtime production cost + unmet demand penalty
    problem += (
        pulp.lpSum(
            machine_params.loc[m, "regular_cost"] * x[j, m, t]
            + machine_params.loc[m, "overtime_cost"] * y[j, m, t]
            for j in jobs for m in machines for t in periods
        )
        + UNMET_PENALTY * pulp.lpSum(u[j, t] for j in jobs for t in periods)
    )

    # Capacity constraints
    for m in machines:
        for t in periods:
            problem += (
                pulp.lpSum(x[j, m, t] for j in jobs) <= machine_params.loc[m, "regular_capacity"]
            )
            problem += (
                pulp.lpSum(y[j, m, t] for j in jobs) <= machine_params.loc[m, "overtime_capacity"]
            )

    # Demand fulfillment constraints
    for j in jobs:
        for t in periods:
            problem += (
                pulp.lpSum(x[j, m, t] + y[j, m, t] for m in machines) + u[j, t]
                >= demand.loc[j, t]
            )

    variables = {
        "x": x, "y": y, "u": u,
        "jobs": jobs, "machines": machines, "periods": periods,
    }
    return problem, variables


def build_scenario_model(
    jobs_df: pd.DataFrame,
    machines_df: pd.DataFrame,
    scenarios_df: pd.DataFrame,
):
    """
    Build the scenario-based model. Capacity commitments (x, y) are
    made once, in advance; demand fulfillment (u) is evaluated
    separately per scenario, weighted by probability.
    """
    jobs = jobs_df["job_id"].unique()
    periods = jobs_df["period"].unique()
    machines = machines_df["machine_id"].unique()
    scenarios = scenarios_df["scenario"].unique()

    problem = pulp.LpProblem("Scenario_Based_Capacity_Plan", pulp.LpMinimize)

    x = {
        (j, m, t): pulp.LpVariable(f"x_{j}_{m}_{t}", lowBound=0)
        for j in jobs for m in machines for t in periods
    }
    y = {
        (j, m, t): pulp.LpVariable(f"y_{j}_{m}_{t}", lowBound=0)
        for j in jobs for m in machines for t in periods
    }
    u = {
        (j, t, s): pulp.LpVariable(f"u_{j}_{t}_{s}", lowBound=0)
        for j in jobs for t in periods for s in scenarios
    }

    machine_params = machines_df.set_index("machine_id")
    base_demand = jobs_df.set_index(["job_id", "period"])["demand_expected"]
    scenario_params = scenarios_df.set_index("scenario")

    def scenario_demand(j, t, s):
        return base_demand.loc[j, t] * scenario_params.loc[s, "demand_multiplier"]

    problem += (
        pulp.lpSum(
            machine_params.loc[m, "regular_cost"] * x[j, m, t]
            + machine_params.loc[m, "overtime_cost"] * y[j, m, t]
            for j in jobs for m in machines for t in periods
        )
        + pulp.lpSum(
            scenario_params.loc[s, "probability"] * UNMET_PENALTY * u[j, t, s]
            for j in jobs for t in periods for s in scenarios
        )
    )

    for m in machines:
        for t in periods:
            problem += (
                pulp.lpSum(x[j, m, t] for j in jobs) <= machine_params.loc[m, "regular_capacity"]
            )
            problem += (
                pulp.lpSum(y[j, m, t] for j in jobs) <= machine_params.loc[m, "overtime_capacity"]
            )

    for j in jobs:
        for t in periods:
            for s in scenarios:
                problem += (
                    pulp.lpSum(x[j, m, t] + y[j, m, t] for m in machines) + u[j, t, s]
                    >= scenario_demand(j, t, s)
                )

    variables = {
        "x": x, "y": y, "u": u,
        "jobs": jobs, "machines": machines, "periods": periods, "scenarios": scenarios,
    }
    return problem, variables