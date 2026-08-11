"""
evaluate.py

Orchestrates the full comparison: solves both the deterministic
and scenario-based models, evaluates each against all demand
scenarios, and produces the final KPI comparison table.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from model import build_deterministic_model, build_scenario_model, UNMET_PENALTY
from solve import solve, extract_deterministic_solution, extract_scenario_solution
from scenarios import load_scenarios, apply_scenario
from metrics import (
    production_cost,
    overtime_hours,
    capacity_utilization,
    demand_fulfillment_rate,
    worst_case_cost,
)


def evaluate_plan_across_scenarios(
    production_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    machines_df: pd.DataFrame,
    scenarios_df: pd.DataFrame,
) -> dict:
    """
    Given a fixed production plan (regular/overtime units per job-machine-period),
    evaluate how much demand goes unmet under each demand scenario, and compute
    the resulting KPIs.
    """
    supply = (
        production_df.groupby(["job", "period"])[["regular_units", "overtime_units"]]
        .sum()
        .sum(axis=1)
    )

    scenario_costs = {}
    total_unmet_expected = 0.0
    total_demand_expected = 0.0

    for _, row in scenarios_df.iterrows():
        s = row["scenario"]
        scaled_jobs = apply_scenario(jobs_df, scenarios_df, s)
        demand = scaled_jobs.set_index(["job_id", "period"])["demand_expected"]

        unmet_total = 0.0
        for (j, t), d in demand.items():
            supplied = supply.get((j, t), 0.0)
            unmet_total += max(0.0, d - supplied)

        cost = production_cost(production_df, machines_df) + UNMET_PENALTY * unmet_total
        scenario_costs[s] = cost

        if s == "expected":
            total_unmet_expected = unmet_total
            total_demand_expected = demand.sum()

    return {
        "production_cost": production_cost(production_df, machines_df),
        "overtime_hours": overtime_hours(production_df),
        "capacity_utilization": capacity_utilization(production_df, machines_df),
        "unmet_demand_expected": total_unmet_expected,
        "demand_fulfillment_rate": demand_fulfillment_rate(
            total_demand_expected, total_unmet_expected
        ),
        "worst_case_cost": worst_case_cost(scenario_costs),
    }


def run_comparison(data_dir: str | Path) -> pd.DataFrame:
    """Run both plans and return the final deterministic vs. scenario-based KPI table."""
    data_dir = Path(data_dir)
    jobs_df = pd.read_csv(data_dir / "jobs.csv")
    machines_df = pd.read_csv(data_dir / "machines.csv")
    scenarios_df = load_scenarios(data_dir / "scenarios.csv")

    # Deterministic plan
    det_problem, det_vars = build_deterministic_model(jobs_df, machines_df)
    solve(det_problem)
    det_production, _ = extract_deterministic_solution(det_vars)
    det_kpis = evaluate_plan_across_scenarios(det_production, jobs_df, machines_df, scenarios_df)

    # Scenario-based plan
    scen_problem, scen_vars = build_scenario_model(jobs_df, machines_df, scenarios_df)
    solve(scen_problem)
    scen_production, _ = extract_scenario_solution(scen_vars)
    scen_kpis = evaluate_plan_across_scenarios(scen_production, jobs_df, machines_df, scenarios_df)

    comparison = pd.DataFrame({
        "Deterministic": det_kpis,
        "Scenario-Based": scen_kpis,
    })
    return comparison


if __name__ == "__main__":
    result = run_comparison(Path(__file__).resolve().parent.parent / "data")
    print(result)