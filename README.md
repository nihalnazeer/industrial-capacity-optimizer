## Full Project Plan: Capacity & Resource Planning Optimizer (Deterministic vs. Robust)

### 1. Problem Statement

A manufacturing/planning environment has a fixed pool of resources (machines, workstations, or workforce-shifts) with limited capacity per period. Demand for production (jobs/orders) must be allocated to resources within their capacity limits, at minimum cost, while meeting delivery targets. Demand is not known with certainty in advance — it fluctuates.

The project answers: **how much does planning "as if demand is known exactly" cost you when it isn't** — and what's the alternative?

---

### 2. The Underlying Logic (the "physics" of the problem)

There's no physical system here (no forces/energy) — the analogous "physics" is a **conservation and constraint-satisfaction problem**, structurally similar to a flow-network:

- **Conservation:** every unit of demand must be satisfied by some combination of regular-time and overtime capacity, or explicitly logged as unmet.
- **Capacity as a hard limit:** each resource has a maximum throughput per period (like a pipe with a max flow rate) — regular hours are "cheap capacity," overtime is "expensive extra capacity" you can draw on up to a cap.
- **The core tension:** a plan built for one demand level allocates capacity efficiently for *that* level, but capacity commitments made now (e.g., shift assignments) can't costlessly change if demand turns out different — this rigidity is what creates risk. Robust optimization is fundamentally about **not over-committing to one future**, the same intuition as diversification in finance, just applied to production capacity instead of assets.

---

### 3. Mathematical Formulation

**Sets/Indices**
- $j \in J$ — jobs/order types
- $m \in M$ — machines/resources
- $t \in T$ — time periods (e.g. days or shifts)
- $s \in S = \{low, expected, high\}$ — demand scenarios, each with probability $p_s$, $\sum_s p_s = 1$

**Parameters**
- $d_{j,t,s}$ — demand for job $j$ in period $t$ under scenario $s$
- $c_{m}$ — regular capacity of machine $m$ per period
- $o_{m}$ — max overtime capacity of machine $m$ per period
- $r_{j,m}$ — production rate (units/hour) of job $j$ on machine $m$
- $cost_m$ — regular-time cost per unit produced on machine $m$
- $cost^{OT}_m$ — overtime cost per unit (higher than $cost_m$)

**Decision Variables**
- $x_{j,m,t} \geq 0$ — units of job $j$ produced on machine $m$ in period $t$ (regular time)
- $y_{j,m,t} \geq 0$ — units of job $j$ produced on machine $m$ in period $t$ (overtime)
- $u_{j,t,s} \geq 0$ — unmet demand for job $j$, period $t$, scenario $s$ (slack variable, penalized)

#### 3.1 Deterministic Model (baseline — plans against expected demand only)

$$\min \sum_{j,m,t} cost_m \cdot x_{j,m,t} + cost^{OT}_m \cdot y_{j,m,t} + \pi \cdot u_{j,t,\text{expected}}$$

Subject to:
$$\sum_{j} x_{j,m,t} \leq c_m \quad \forall m,t \quad \text{(regular capacity)}$$
$$\sum_{j} y_{j,m,t} \leq o_m \quad \forall m,t \quad \text{(overtime capacity)}$$
$$\sum_m (x_{j,m,t} + y_{j,m,t}) + u_{j,t,\text{expected}} \geq d_{j,t,\text{expected}} \quad \forall j,t$$

($\pi$ = large penalty cost per unit of unmet demand, forcing the model to prioritize satisfying demand.)

This model only ever "sees" the expected-demand scenario — it's optimal for that one future, brittle to any other.

#### 3.2 Robust / Scenario-Based Model

Same decision variables for capacity **committed in advance** ($x_{j,m,t}$, $y_{j,m,t}$ — these can't scenario-vary, since capacity/shift decisions are made before demand is known), but demand fulfillment is evaluated **across all scenarios**:

$$\min \sum_{j,m,t} cost_m \cdot x_{j,m,t} + cost^{OT}_m \cdot y_{j,m,t} + \sum_{s} p_s \cdot \pi \cdot u_{j,t,s}$$

Subject to the same capacity constraints, plus:
$$\sum_m (x_{j,m,t} + y_{j,m,t}) + u_{j,t,s} \geq d_{j,t,s} \quad \forall j,t,s$$

This minimizes **expected** unmet-demand penalty across scenarios — a plan that hedges rather than over-fitting to one forecast. (Optional stronger variant: minimize the *worst-case* scenario cost instead of the expected one — a true minimax robust formulation, if you want to demonstrate you know the distinction between stochastic and robust optimization; worth a one-line mention in the README even if you only implement the expected-value version.)

---

### 4. Metrics Reported (per the earlier suggestion — good addition)

| Metric | Deterministic | Robust |
|---|---|---|
| Production Cost (expected) | ✓ | ✓ |
| Overtime Hours | ✓ | ✓ |
| Capacity Utilization (%) | ✓ | ✓ |
| Demand Fulfillment Rate | ✓ | ✓ |
| Worst-case Scenario Cost | ✓ | ✓ |

The key result you're aiming to demonstrate: deterministic plan wins on expected-case cost but loses badly on worst-case cost/fulfillment; robust plan sacrifices a little expected-case efficiency for much better worst-case resilience.

---

### 5. Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Optimization | **PuLP** (or OR-Tools if you want a faster/more scalable solver) | Clean LP/IP modeling in Python, free CBC solver bundled |
| Data handling | pandas | Standard, matches your other project |
| Scenario logic | plain Python (`scenarios.py`) | No need for anything heavier at 3 scenarios |
| Dashboard | Streamlit | Consistent with your RUL project, fast to build |
| Visualization | matplotlib / plotly | Utilization and cost comparison charts |

---

### 6. Architecture

```
capacity-resource-optimizer/
├── README.md
├── requirements.txt
├── data/
│   ├── jobs.csv          ← job types, demand baseline
│   ├── machines.csv      ← capacity, regular/overtime cost per machine
│   └── scenarios.csv     ← low/expected/high demand multipliers + probabilities
├── src/
│   ├── model.py           ← builds deterministic & robust LP formulations
│   ├── solve.py            ← solves with PuLP, returns allocation
│   ├── scenarios.py        ← scenario generation/probability weighting
│   ├── metrics.py          ← computes utilization, fulfillment, cost KPIs from solved plans
│   └── evaluate.py          ← runs both plans across all scenarios for comparison
├── notebooks/
│   └── 01_optimizer_walkthrough.ipynb   ← formulation walkthrough + results
├── dashboards/
│   └── streamlit_app.py     ← deterministic vs robust KPI comparison view
└── reports/
    └── figures/
```

---

### 7. Build Sequence (so you can timebox it)

1. Define `jobs.csv`/`machines.csv`/`scenarios.csv` with small, realistic synthetic numbers (e.g. 5 jobs, 4 machines, 3 scenarios).
2. `model.py` + `solve.py` — deterministic model first, confirm it solves and gives sane output.
3. Extend to robust/scenario model — reuse most of the same code, just loop demand constraints over scenarios.
4. `metrics.py` — compute the 5-row comparison table above for both plans, evaluated against all 3 scenarios.
5. `evaluate.py` — orchestrates: solve both, evaluate both across all scenarios, output the comparison table.
6. Dashboard — bar chart of the 5 metrics, deterministic vs. robust.
7. README — mirror the structure of your RUL project's README (problem → formulation → results → key takeaway), so the two repos visually read as a matched pair.

Want me to start writing the actual `model.py` formulation in PuLP now, along with a synthetic dataset that produces a clear, tellable result (i.e. numbers that actually show the deterministic-vs-robust trade-off clearly rather than a wash)?
