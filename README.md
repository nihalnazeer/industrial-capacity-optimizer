Capacity & Resource Planning Optimizer: Deterministic vs. Scenario-Based Planning

An Operations Research project comparing two production-planning philosophies — planning against a single demand forecast versus planning across multiple demand scenarios — to quantify the cost of demand uncertainty in capacity allocation.

1. Problem Statement

A manufacturing/planning environment has a fixed pool of resources (machines, workstations, or workforce shifts) with limited capacity per period. Demand for production (jobs/orders) must be allocated to resources within capacity limits, at minimum cost, while meeting delivery targets — but demand is not known with certainty in advance.

This project answers a concrete question: how much does planning "as if demand is known exactly" cost you when it isn't — and what's the alternative?

2. Problem Logic

There's no physical system underlying this problem — the structure is a constraint-satisfaction and allocation problem, similar to a flow-network:

Conservation: every unit of demand must be satisfied by some combination of regular-time and overtime capacity, or explicitly logged as unmet.
Capacity as a hard limit: each resource has a maximum throughput per period — regular hours are cheap capacity, overtime is expensive extra capacity available only up to a cap.
The core tension: capacity commitments (e.g. shift assignments) are made before actual demand is known. A plan built for one demand level is efficient for that level, but rigid and costly if the real outcome differs. Scenario-based planning addresses this by evaluating a single committed plan against multiple possible futures, rather than optimizing for only one.
3. Mathematical Formulation
Sets and Indices
𝑗
∈
𝐽
j∈J — job/order types
𝑚
∈
𝑀
m∈M — machines/resources
𝑡
∈
𝑇
t∈T — time periods (e.g. days or shifts)
𝑠
∈
𝑆
=
{
low
,
expected
,
high
}
s∈S={low,expected,high} — demand scenarios
Scenario Probabilities
Scenario	Probability
Low	0.20
Expected	0.60
High	0.20
Parameters
𝑑
𝑗
,
𝑡
,
𝑠
d
j,t,s
	​

 — demand for job 
𝑗
j in period 
𝑡
t under scenario 
𝑠
s
𝑐
𝑚
c
m
	​

 — regular capacity of machine 
𝑚
m per period
𝑜
𝑚
o
m
	​

 — maximum overtime capacity of machine 
𝑚
m per period
𝑐
𝑜
𝑠
𝑡
𝑚
cost
m
	​

 — regular-time cost per unit produced on machine 
𝑚
m
𝑐
𝑜
𝑠
𝑡
𝑚
𝑂
𝑇
cost
m
OT
	​

 — overtime cost per unit produced on machine 
𝑚
m (> 
𝑐
𝑜
𝑠
𝑡
𝑚
cost
m
	​

)
𝜋
π — penalty cost per unit of unmet demand
Decision Variables
𝑥
𝑗
,
𝑚
,
𝑡
≥
0
x
j,m,t
	​

≥0 — units of job 
𝑗
j produced on machine 
𝑚
m in period 
𝑡
t, regular time
𝑦
𝑗
,
𝑚
,
𝑡
≥
0
y
j,m,t
	​

≥0 — units of job 
𝑗
j produced on machine 
𝑚
m in period 
𝑡
t, overtime
𝑢
𝑗
,
𝑡
,
𝑠
≥
0
u
j,t,s
	​

≥0 — unmet demand for job 
𝑗
j, period 
𝑡
t, scenario 
𝑠
s
3.1 Deterministic Model (baseline)

Plans against the expected-demand scenario only:

min
⁡
∑
𝑗
,
𝑚
,
𝑡
𝑐
𝑜
𝑠
𝑡
𝑚
⋅
𝑥
𝑗
,
𝑚
,
𝑡
+
𝑐
𝑜
𝑠
𝑡
𝑚
𝑂
𝑇
⋅
𝑦
𝑗
,
𝑚
,
𝑡
+
𝜋
⋅
𝑢
𝑗
,
𝑡
,
expected
min
j,m,t
∑
	​

cost
m
	​

⋅x
j,m,t
	​

+cost
m
OT
	​

⋅y
j,m,t
	​

+π⋅u
j,t,expected
	​


Subject to:

∑
𝑗
𝑥
𝑗
,
𝑚
,
𝑡
≤
𝑐
𝑚
∀
𝑚
,
𝑡
j
∑
	​

x
j,m,t
	​

≤c
m
	​

∀m,t
∑
𝑗
𝑦
𝑗
,
𝑚
,
𝑡
≤
𝑜
𝑚
∀
𝑚
,
𝑡
j
∑
	​

y
j,m,t
	​

≤o
m
	​

∀m,t
∑
𝑚
(
𝑥
𝑗
,
𝑚
,
𝑡
+
𝑦
𝑗
,
𝑚
,
𝑡
)
+
𝑢
𝑗
,
𝑡
,
expected
≥
𝑑
𝑗
,
𝑡
,
expected
∀
𝑗
,
𝑡
m
∑
	​

(x
j,m,t
	​

+y
j,m,t
	​

)+u
j,t,expected
	​

≥d
j,t,expected
	​

∀j,t

This plan is optimal for exactly one future and has no visibility into what happens if demand deviates.

3.2 Scenario-Based Model

Capacity commitments (
𝑥
𝑗
,
𝑚
,
𝑡
x
j,m,t
	​

, 
𝑦
𝑗
,
𝑚
,
𝑡
y
j,m,t
	​

) are made once, in advance — they cannot vary by scenario, since shift/resource decisions are locked in before actual demand is observed. Demand fulfillment is evaluated across all scenarios, weighted by probability:

min
⁡
∑
𝑗
,
𝑚
,
𝑡
𝑐
𝑜
𝑠
𝑡
𝑚
⋅
𝑥
𝑗
,
𝑚
,
𝑡
+
𝑐
𝑜
𝑠
𝑡
𝑚
𝑂
𝑇
⋅
𝑦
𝑗
,
𝑚
,
𝑡
+
∑
𝑠
𝑝
𝑠
⋅
𝜋
⋅
𝑢
𝑗
,
𝑡
,
𝑠
min
j,m,t
∑
	​

cost
m
	​

⋅x
j,m,t
	​

+cost
m
OT
	​

⋅y
j,m,t
	​

+
s
∑
	​

p
s
	​

⋅π⋅u
j,t,s
	​


Subject to the same capacity constraints, plus:

∑
𝑚
(
𝑥
𝑗
,
𝑚
,
𝑡
+
𝑦
𝑗
,
𝑚
,
𝑡
)
+
𝑢
𝑗
,
𝑡
,
𝑠
≥
𝑑
𝑗
,
𝑡
,
𝑠
∀
𝑗
,
𝑡
,
𝑠
m
∑
	​

(x
j,m,t
	​

+y
j,m,t
	​

)+u
j,t,s
	​

≥d
j,t,s
	​

∀j,t,s

This is a scenario-based (stochastic) programming formulation — it minimizes expected unmet-demand penalty across weighted scenarios, hedging against uncertainty rather than optimizing for a single forecast.

Note on terminology: this is deliberately called scenario-based rather than robust optimization. Classical robust optimization minimizes the worst case (
min
⁡
max
⁡
𝑠
𝐶
𝑜
𝑠
𝑡
𝑠
minmax
s
	​

Cost
s
	​

) or defines uncertainty sets; this model minimizes expected cost across weighted scenarios, which is stochastic programming. A true minimax-robust variant is noted as future work in Section 8.

4. Metrics Reported
Metric	Deterministic	Scenario-Based
Production Cost (expected)	✓	✓
Overtime Hours	✓	✓
Capacity Utilization (%)	✓	✓
Demand Fulfillment Rate	✓	✓
Unmet Demand (units)	✓	✓
Worst-case Scenario Cost	✓	✓

Capacity Utilization is computed as:

Utilization
=
Regular Production
+
Overtime Production
Available Capacity (Regular + Overtime)
×
100
Utilization=
Available Capacity (Regular + Overtime)
Regular Production+Overtime Production
	​

×100

Overtime is included in the numerator so that a plan leaning heavily on overtime isn't misleadingly reported as "low utilization."

Unmet Demand is reported explicitly — this is the quantity (
𝑢
𝑗
,
𝑡
,
𝑠
u
j,t,s
	​

) the optimizer is directly minimizing, and it deserves visibility rather than staying buried inside the cost total.

Expected result: the deterministic plan wins on expected-case cost but degrades sharply in worst-case cost and fulfillment when demand deviates from the forecast. The scenario-based plan trades a small amount of expected-case efficiency for materially better worst-case resilience.

5. Dataset Design

Synthetic data, deliberately structured (not randomly generated) so the optimizer faces genuinely interesting trade-offs:

Machine	Profile
A	Cheap, low capacity
B	Expensive, high capacity
C	Fast, limited overtime availability

This mix forces the model to make real allocation trade-offs between cost and flexibility, rather than trivially assigning everything to one "best" resource.

6. Tech Stack
Layer	Tool	Why
Optimization	PuLP (CBC solver)	Clean LP/IP modeling in Python, free bundled solver
Data handling	pandas	Standard, consistent with the companion RUL project
Scenario logic	Plain Python (scenarios.py)	No need for simulation machinery at 3 scenarios
Dashboard	Streamlit	Consistent with the RUL project's dashboard
Visualization	matplotlib / plotly	Utilization and cost comparison charts
7. Architecture
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
8. Scope and Future Work

Locked scope for this project: one LP/IP core model, deterministic vs. scenario-based comparison, 3 demand scenarios, the KPI table above. Deliberately excluded from this version: Monte Carlo simulation, reinforcement learning, genetic algorithms, digital-twin simulation, multi-objective optimization, and inventory optimization — worthwhile directions, kept out to preserve a focused, finishable scope.

Future extensions:

A true minimax robust formulation (
min
⁡
max
⁡
𝑠
𝐶
𝑜
𝑠
𝑡
𝑠
minmax
s
	​

Cost
s
	​

), to complement the current expected-cost scenario model
Linking predicted equipment failures (from a companion predictive-maintenance model) as a capacity constraint, so a predicted maintenance event automatically reduces available capacity in the optimizer — connecting prediction to operational decision-making
9. Key Takeaway

Planning against a single demand forecast is efficient only if that forecast is correct. This project quantifies the cost of that assumption failing, and shows that a modest, well-defined hedge — a scenario-based formulation using the same underlying optimization model — meaningfully improves resilience without requiring a fundamentally different (or more complex) approach.
