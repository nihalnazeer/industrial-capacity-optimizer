# Industrial Capacity Optimizer

A scenario-based capacity and resource planning optimizer for manufacturing systems using Linear Programming (LP) and Integer Programming (IP).

The project compares traditional deterministic production planning with robust optimization under demand uncertainty, demonstrating how operational plans can be made more resilient while balancing production cost, overtime, and resource utilization.

---

## Overview

Manufacturing organizations typically create production plans using a single demand forecast. In reality, demand and resource availability are uncertain, often resulting in schedule disruptions, excessive overtime, and reduced service levels.

This project develops a capacity planning optimizer that evaluates production plans under multiple demand scenarios and compares:

- Deterministic Optimization (single forecast)
- Robust Optimization (multiple demand scenarios)

The objective is to quantify the trade-off between operational efficiency and resilience under uncertainty.

---

## Objectives

- Develop a production planning optimizer using Linear Programming.
- Allocate jobs to available resources while satisfying operational constraints.
- Compare deterministic and robust planning strategies.
- Evaluate production performance under multiple demand scenarios.
- Visualize operational trade-offs using an interactive dashboard.

---

## Features

- Linear Programming optimization
- Resource allocation
- Capacity planning
- Shift scheduling
- Machine constraints
- Overtime optimization
- Multi-scenario demand planning
- Robust optimization
- Performance dashboard
- Comparative analytics

---

## Demand Scenarios

The optimizer evaluates production plans across three operational demand conditions.

| Scenario | Description |
|----------|-------------|
| Low Demand | Reduced customer demand |
| Expected Demand | Forecast production demand |
| High Demand | Peak production demand |

---

## Optimization Strategies

### Deterministic Planning

Optimizes production using a single demand forecast.

### Robust Planning

Generates production plans that remain feasible across multiple demand scenarios while minimizing operational risk.

---

## Performance Metrics

The project evaluates each planning strategy using:

- Total Production Cost
- Overtime Hours
- Capacity Utilization
- Resource Utilization
- Demand Fulfillment
- On-Time Delivery Rate
- Worst-Case Scenario Cost

---

## Technology Stack

- Python
- PuLP
- Pandas
- NumPy
- Plotly
- Streamlit
- Matplotlib

---

## Project Structure

```text
industrial-capacity-optimizer/

│
├── data/
│   ├── jobs.csv
│   ├── machines.csv
│   ├── scenarios.csv
│
├── src/
│   ├── model.py
│   ├── solve.py
│   ├── scenarios.py
│   ├── metrics.py
│   └── dashboard.py
│
├── notebooks/
│   └── analysis.ipynb
│
├── app.py
│
├── requirements.txt
│
└── README.md
```

---

## Future Improvements

- Workforce planning
- Maintenance-aware scheduling
- Multi-objective optimization
- Inventory optimization
- Supply chain integration
- Real-time demand updates
- AI-assisted demand forecasting
- Digital twin integration

---

## License

MIT License
