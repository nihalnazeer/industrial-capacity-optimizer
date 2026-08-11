"""
scenarios.py

Loads demand scenarios and applies scenario multipliers to base
job demand.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_scenarios(path: str | Path) -> pd.DataFrame:
    """Load scenario definitions (scenario, probability, demand_multiplier)."""
    df = pd.read_csv(path)
    assert abs(df["probability"].sum() - 1.0) < 1e-6, "Scenario probabilities must sum to 1."
    return df


def apply_scenario(
    jobs_df: pd.DataFrame,
    scenarios_df: pd.DataFrame,
    scenario_name: str,
) -> pd.DataFrame:
    """Return a copy of jobs_df with demand scaled by the given scenario's multiplier."""
    multiplier = scenarios_df.set_index("scenario").loc[scenario_name, "demand_multiplier"]
    scaled = jobs_df.copy()
    scaled["demand_expected"] = scaled["demand_expected"] * multiplier
    return scaled