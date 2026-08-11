# Industrial Capacity & Resource Planning Optimizer: Deterministic vs. Scenario-Based Planning

An Operations Research project comparing two production-planning philosophies — planning against a single demand forecast versus planning across multiple demand scenarios — to quantify the cost of demand uncertainty in capacity allocation.

---

## 1. Problem Statement

A manufacturing/planning environment has a fixed pool of resources (machines, workstations, or workforce shifts) with limited capacity per period. Demand for production (jobs/orders) must be allocated to resources within capacity limits, at minimum cost, while meeting delivery targets — but **demand is not known with certainty in advance**.

This project answers a concrete question: **how much does planning "as if demand is known exactly" cost you when it isn't — and what's the alternative?**

---

## 2. Problem Logic

There's no physical system underlying this problem — the structure is a **constraint-satisfaction and allocation problem**, similar to a flow-network:

- **Conservation:** every unit of demand must be satisfied by some combination of regular-time and overtime capacity, or explicitly logged as unmet.
- **Capacity as a hard limit:** each resource has a maximum throughput per period — regular hours are cheap capacity, overtime is expensive extra capacity available only up to a cap.
- **The core tension:** capacity commitments (e.g. shift assignments) are made *before* actual demand is known. A plan built for one demand level is efficient for that level, but rigid and costly if the real outcome differs. Scenario-based planning addresses this by evaluating a single committed plan against multiple possible futures, rather than optimizing for only one.

---

## 3. Mathematical Formulation

### Sets and Indices
- $j \in J$ — job/order types
- $m \in M$ — machines/resources
- $t \in T$ — time periods (e.g. days or shifts)
- $s \in S = \{\text{low}, \text{expected}, \text{high}\}$ — demand scenarios

### Scenario Probabilities

| Scenario | Probability |
|---|---:|
| Low | 0.20 |
| Expected | 0.60 |
| High | 0.20 |

### Parameters
- $d_{j,t,s}$ — demand for job $j$ in period $t$ under scenario $s$
- $c_m$ — regular capacity of machine $m$ per period
- $o_m$ — maximum overtime capacity of machine $m$ per period
- $cost_m$ — regular-time cost per unit produced on machine $m$
- $cost^{OT}_m$ — overtime cost per unit produced on machine $m$ (> $cost_m$)
- $\pi$ — penalty cost per unit of unmet demand

### Decision Variables
- $x_{j,m,t} \geq 0$ — units of job $j$ produced on machine $m$ in period $t$, regular time
- $y_{j,m,t} \geq 0$ — units of job $j$ produced on machine $m$ in period $t$, overtime
- $u_{j,t,s} \geq 0$ — unmet demand for job $j$, period $t$, scenario $s$

### 3.1 Deterministic Model (baseline)

Plans against the expected-demand scenario only:

$$\min \sum_{j,m,t} cost_m \cdot x_{j,m,t} + cost^{OT}_m \cdot y_{j,m,t} + \pi \cdot u_{j,t,\text{expected}}$$

Subject to:

$$\sum_j x_{j,m,t} \leq c_m \quad \forall m,t$$
$$\sum_j y_{j,m,t} \leq o_m \quad \forall m,t$$
$$\sum_m (x_{j,m,t} + y_{j,m,t}) + u_{j,t,\text{expected}} \geq d_{j,t,\text{expected}} \quad \forall j,t$$

This plan is optimal for exactly one future and has no visibility into what happens if demand deviates.

### 3.2 Scenario-Based Model

Capacity commitments ($x_{j,m,t}$, $y_{j,m,t}$) are made once, in advance — they cannot vary by scenario, since shift/resource decisions are locked in before actual demand is observed. Demand fulfillment is evaluated across **all** scenarios, weighted by probability:

$$\min \sum_{j,m,t} cost_m \cdot x_{j,m,t} + cost^{OT}_m \cdot y_{j,m,t} + \sum_{s} p_s \cdot \pi \cdot u_{j,t,s}$$

Subject to the same capacity constraints, plus:

$$\sum_m (x_{j,m,t} + y_{j,m,t}) + u_{j,t,s} \geq d_{j,t,s} \quad \forall j,t,s$$

This is a **scenario-based (stochastic) programming** formulation — it minimizes *expected* unmet-demand penalty across weighted scenarios, hedging against uncertainty rather than optimizing for a single forecast.

> **Note on terminology:** this is deliberately called *scenario-based* rather than *robust* optimization. Classical robust optimization minimizes the worst case ($\min \max_s Cost_s$) or defines uncertainty sets; this model minimizes expected cost across weighted scenarios, which is stochastic programming. A true minimax-robust variant is noted as future work in Section 8.

---

## 4. Metrics Reported

| Metric | Deterministic | Scenario-Based |
|---|---|---|
| Production Cost (expected) | ✓ | ✓ |
| Overtime Hours | ✓ | ✓ |
| Capacity Utilization (%) | ✓ | ✓ |
| Demand Fulfillment Rate | ✓ | ✓ |
| Unmet Demand (units) | ✓ | ✓ |
| Worst-case Scenario Cost | ✓ | ✓ |

**Capacity Utilization** is computed as:

$$\text{Utilization} = \frac{\text{Regular Production} + \text{Overtime Production}}{\text{Available Capacity (Regular + Overtime)}} \times 100$$

Overtime is included in the numerator so that a plan leaning heavily on overtime isn't misleadingly reported as "low utilization."

**Unmet Demand** is reported explicitly — this is the quantity ($u_{j,t,s}$) the optimizer is directly minimizing, and it deserves visibility rather than staying buried inside the cost total.

**Expected result:** the deterministic plan wins on expected-case cost but degrades sharply in worst-case cost and fulfillment when demand deviates from the forecast. The scenario-based plan trades a small amount of expected-case efficiency for materially better worst-case resilience.

---

## 5. Dataset Design

Synthetic data, deliberately structured (not randomly generated) so the optimizer faces genuinely interesting trade-offs:

| Machine | Profile |
|---|---|
| A | Cheap, low capacity |
| B | Expensive, high capacity |
| C | Fast, limited overtime availability |

This mix forces the model to make real allocation trade-offs between cost and flexibility, rather than trivially assigning everything to one "best" resource.

---

## 6. Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Optimization | PuLP (CBC solver) | Clean LP/IP modeling in Python, free bundled solver |
| Data handling | pandas | Standard, consistent with the companion RUL project |
| Scenario logic | Plain Python (`scenarios.py`) | No need for simulation machinery at 3 scenarios |
| Dashboard | Streamlit | Consistent with the RUL project's dashboard |
| Visualization | matplotlib / plotly | Utilization and cost comparison charts |

---

## 7. Architecture

```
capacity-resource-optimizer/
├── README.md
├── requirements.txt
├── data/
│   ├── jobs.csv          ← job types, demand baseline
│   ├── machines.csv      ← capacity, regular/overtime cost per machine
│   └── scenarios.csv     ← low/expected/high demand multipliers + probabilities
├── src/
│   ├── model.py           ← builds deterministic & scenario-based LP formulations
│   ├── solve.py            ← solves with PuLP, returns allocation
│   ├── scenarios.py        ← scenario generation and probability weighting
│   ├── metrics.py          ← computes utilization, fulfillment, unmet demand, cost KPIs
│   └── evaluate.py          ← runs both plans across all scenarios for comparison
├── notebooks/
│   └── 01_optimizer_walkthrough.ipynb   ← formulation walkthrough + results
├── app/
│   └── streamlit_app.py     ← deterministic vs. scenario-based KPI comparison view
└── reports/
    └── figures/
```

---

## 8. Scope and Future Work

**Locked scope for this project:** one LP/IP core model, deterministic vs. scenario-based comparison, 3 demand scenarios, the KPI table above. Deliberately excluded from this version: Monte Carlo simulation, reinforcement learning, genetic algorithms, digital-twin simulation, multi-objective optimization, and inventory optimization — worthwhile directions, kept out to preserve a focused, finishable scope.

**Future extensions:**
- A true minimax robust formulation ($\min \max_s Cost_s$), to complement the current expected-cost scenario model
- Linking predicted equipment failures (from a companion predictive-maintenance model) as a capacity constraint, so a predicted maintenance event automatically reduces available capacity in the optimizer — connecting prediction to operational decision-making

---

## 9. Key Takeaway

Planning against a single demand forecast is efficient only if that forecast is correct. This project quantifies the cost of that assumption failing, and shows that a modest, well-defined hedge — a scenario-based formulation using the same underlying optimization model — meaningfully improves resilience without requiring a fundamentally different (or more complex) approach.
