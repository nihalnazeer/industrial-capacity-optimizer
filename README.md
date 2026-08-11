# Industrial Capacity & Resource Planning Optimizer

> A scenario-based Operations Research framework for production planning under demand uncertainty.

An Operations Research project that develops a production planning optimizer for manufacturing environments with uncertain demand. The optimizer compares deterministic production planning with scenario-based planning to quantify the operational cost of assuming that demand is known exactly.

---

# Problem Statement

Manufacturing systems operate with a fixed pool of resources such as machines, workstations, or workforce shifts. These resources have limited production capacity, while customer demand varies over time and is rarely known with certainty.

The objective is to allocate production across available resources while:

- minimizing production cost
- respecting machine capacity constraints
- limiting overtime usage
- maximizing demand fulfillment

The project investigates a fundamental planning question:

> **How much does planning as if demand is known exactly cost when demand is actually uncertain?**

---

# Problem Logic

Although this is not a physical simulation, the planning process behaves like a constrained flow network.

## Conservation

Every unit of customer demand must be:

- produced during regular working hours,
- produced using overtime capacity, or
- recorded as unmet demand.

## Capacity Constraints

Each machine has:

- Regular production capacity
- Overtime production capacity

Regular production is cheaper.

Overtime provides flexibility but incurs additional cost.

## Operational Challenge

Capacity decisions (shift allocation, machine loading, workforce assignment) are committed **before** actual demand is observed.

A deterministic plan is optimal only if the forecast is correct.

Scenario-based planning instead evaluates a single production plan across multiple possible demand outcomes.

---

# Mathematical Formulation

## Sets

| Symbol | Description |
|---------|-------------|
| **J** | Jobs / Product Types |
| **M** | Machines / Resources |
| **T** | Planning Periods |
| **S** | Demand Scenarios (Low, Expected, High) |

---

## Scenario Probabilities

| Scenario | Probability |
|-----------|------------:|
| Low | 0.20 |
| Expected | 0.60 |
| High | 0.20 |

---

## Parameters

| Parameter | Description |
|-----------|-------------|
| \(d_{j,t,s}\) | Demand for job *j* during period *t* under scenario *s* |
| \(c_m\) | Regular capacity of machine *m* |
| \(o_m\) | Maximum overtime capacity |
| \(cost_m\) | Regular production cost |
| \(cost^{OT}_m\) | Overtime production cost |
| \(\pi\) | Penalty cost for unmet demand |

---

## Decision Variables

| Variable | Description |
|-----------|-------------|
| \(x_{j,m,t}\) | Regular-time production |
| \(y_{j,m,t}\) | Overtime production |
| \(u_{j,t,s}\) | Unmet demand |

---

# Deterministic Planning Model

The baseline optimizer assumes the expected demand forecast is perfectly accurate.

### Objective

Minimize

- Regular production cost
- Overtime cost
- Unmet demand penalty

subject to

- machine capacity
- overtime capacity
- demand satisfaction

This optimizer only plans for a **single future**.

---

# Scenario-Based Planning Model

The scenario-based formulation keeps the same production decisions but evaluates them under multiple demand scenarios.

Capacity allocations are committed **before** demand is observed.

Demand satisfaction is evaluated under:

- Low Demand
- Expected Demand
- High Demand

weighted by their respective probabilities.

The optimizer minimizes the **expected production cost and unmet demand penalty** across all scenarios.

> **Note**
>
> This implementation is a **scenario-based stochastic programming** model.
>
> It is intentionally distinguished from classical robust optimization, which typically minimizes the worst-case objective or optimizes over uncertainty sets.

---

# Performance Metrics

Both planning approaches are evaluated using the same operational KPIs.

| Metric | Deterministic | Scenario-Based |
|---------|:-------------:|:--------------:|
| Production Cost | ✓ | ✓ |
| Overtime Hours | ✓ | ✓ |
| Capacity Utilization | ✓ | ✓ |
| Demand Fulfillment | ✓ | ✓ |
| Unmet Demand | ✓ | ✓ |
| Worst-Case Scenario Cost | ✓ | ✓ |

### Capacity Utilization

\[
Utilization =
\frac{Regular\ Production + Overtime\ Production}
{Available\ Capacity}
\times 100
\]

Including overtime prevents heavily overloaded schedules from appearing artificially under-utilized.

---

# Expected Outcome

The deterministic optimizer is expected to achieve the lowest cost **only when demand exactly matches the forecast**.

The scenario-based optimizer sacrifices a small amount of expected efficiency in exchange for:

- lower worst-case cost
- higher demand fulfillment
- reduced unmet demand
- improved operational resilience

---

# Dataset Design

The project uses intentionally designed synthetic data rather than randomly generated values.

## Machines

| Machine | Characteristics |
|-----------|----------------|
| Machine A | Low cost, limited capacity |
| Machine B | High cost, large capacity |
| Machine C | High speed, limited overtime |

This forces meaningful allocation decisions rather than trivial optimization.

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Optimization | PuLP (CBC Solver) |
| Data Processing | Pandas |
| Scenario Engine | Python |
| Dashboard | Streamlit |
| Visualization | Matplotlib / Plotly |

---

# Project Structure

```text
industrial-capacity-optimizer/

├── README.md
├── requirements.txt

├── data/
│   ├── jobs.csv
│   ├── machines.csv
│   └── scenarios.csv

├── src/
│   ├── model.py
│   ├── solve.py
│   ├── scenarios.py
│   ├── metrics.py
│   └── evaluate.py

├── notebooks/
│   └── 01_optimizer_walkthrough.ipynb

├── app/
│   └── streamlit_app.py

└── reports/
    └── figures/
```

---

# Scope

The current implementation includes:

- Deterministic production planning
- Scenario-based production planning
- Three demand scenarios
- Production allocation optimization
- KPI comparison dashboard

The following are intentionally excluded to maintain a focused project scope:

- Monte Carlo Simulation
- Reinforcement Learning
- Genetic Algorithms
- Digital Twin Simulation
- Multi-objective Optimization
- Inventory Optimization

---

# Future Work

Potential extensions include:

- Classical minimax robust optimization
- Maintenance-aware production planning
- Dynamic demand forecasting
- Multi-period scheduling
- Inventory optimization
- Supply chain integration

A particularly interesting extension is integrating the companion predictive maintenance project so that predicted machine failures automatically reduce available production capacity before optimization.

---

# Key Takeaway

Rather than building a different optimization model, this project demonstrates how incorporating demand uncertainty into the planning process fundamentally changes operational decisions.

The comparison shows that planning against a single forecast may maximize short-term efficiency but can perform poorly when demand deviates from expectations, whereas a scenario-based planning strategy provides a more resilient production plan with improved performance across uncertain operating conditions.
