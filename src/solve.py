"""
solve.py

Solve LP/IP models built in model.py and extract results into
tidy pandas DataFrames.
"""

from __future__ import annotations

import pulp
import pandas as pd


def solve(problem: pulp.LpProblem) -> str:
    """Solve a PuLP problem using the bundled CBC solver."""
    problem.solve(pulp.PULP_CBC_CMD(msg=False))
    return pulp.LpStatus[problem.status]


def extract_deterministic_solution(variables: dict):
    """Extract regular/overtime production and unmet demand as tidy DataFrames."""
    rows = []
    for j in variables["jobs"]:
        for m in variables["machines"]:
            for t in variables["periods"]:
                rows.append({
                    "job": j, "machine": m, "period": t,
                    "regular_units": variables["x"][j, m, t].value(),
                    "overtime_units": variables["y"][j, m, t].value(),
                })
    production_df = pd.DataFrame(rows)

    unmet_rows = [
        {"job": j, "period": t, "unmet": variables["u"][j, t].value()}
        for j in variables["jobs"] for t in variables["periods"]
    ]
    unmet_df = pd.DataFrame(unmet_rows)

    return production_df, unmet_df


def extract_scenario_solution(variables: dict):
    """Extract production plan (scenario-independent) and unmet demand (per scenario)."""
    rows = []
    for j in variables["jobs"]:
        for m in variables["machines"]:
            for t in variables["periods"]:
                rows.append({
                    "job": j, "machine": m, "period": t,
                    "regular_units": variables["x"][j, m, t].value(),
                    "overtime_units": variables["y"][j, m, t].value(),
                })
    production_df = pd.DataFrame(rows)

    unmet_rows = [
        {"job": j, "period": t, "scenario": s, "unmet": variables["u"][j, t, s].value()}
        for j in variables["jobs"] for t in variables["periods"] for s in variables["scenarios"]
    ]
    unmet_df = pd.DataFrame(unmet_rows)

    return production_df, unmet_df