# 🚂 RailOptimizer — Decision Support System
### SIH 2024 | Indian Railways Train Optimization

A full-stack intelligent decision-support system for Indian Railways section controllers.
Built for the Smart India Hackathon problem statement on Rail Optimization.

---

## Features

| Module | Description |
|--------|-------------|
| **Dashboard** | Live KPIs, track diagram, conflict overview, delay charts |
| **Train Status** | Real-time table of all trains with filter, hold/proceed/expedite actions |
| **Conflicts** | Automated CROSSING & PLATFORM conflict detection with recommendations |
| **Schedule** | Priority-weighted movement schedule using greedy heap-based scheduler |
| **Optimizer** | Local-search greedy optimizer minimizing weighted total delay |
| **What-If Simulator** | Scenario analysis — Hold / Reroute simulations |
| **Section Map** | Track section status (Clear / Occupied / Maintenance), single/double line |
| **Audit Trail** | Full log of all controller actions with timestamps |

---

## Setup

```bash
cd rail_optimizer

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Then open: **http://localhost:5000**

---

## Architecture

```
rail_optimizer/
├── app.py                   # Flask REST API backend
├── requirements.txt
├── models/
│   └── railway_models.py    # Dataclasses: Train, Station, TrackSection, Conflict, KPIs
├── algorithms/
│   └── optimizer.py         # ConflictDetector, PrecedenceScheduler, GreedyOptimizer, WhatIfSimulator
├── data/
│   └── data_generator.py    # Realistic Indian Railways sample data (NGP–AKT section)
└── templates/
    └── index.html           # Full single-page UI (industrial control-room aesthetic)
```

---

## Algorithms

### Conflict Detection
- Graph-based traversal across train pairs
- Detects CROSSING conflicts (single-line sections) and PLATFORM conflicts
- Computes time-to-conflict and generates natural-language recommendations

### Precedence Scheduler
- Min-heap priority queue (priority = train type weight × 10 − delay × 0.5)
- Assigns ordered movement slots with action labels (PROCEED / HOLD / EXPEDITE)

### Greedy Optimizer
- Baseline: sequential by train list
- Local search: random pair exchanges over 100 iterations
- Objective: minimize Σ(priority_weight × (delay + position_penalty))

### What-If Simulator
- Hold: models delay propagation from holding a train
- Reroute: estimates extra distance/time via alternate path

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Full dashboard data (KPIs, trains, conflicts, sections) |
| GET | `/api/trains` | All trains |
| GET | `/api/conflicts` | All conflicts |
| GET | `/api/schedule` | Optimized movement schedule |
| GET | `/api/optimize` | Run greedy optimizer |
| POST | `/api/conflict/resolve/<id>` | Resolve a conflict |
| POST | `/api/train/action` | Hold / Proceed / Expedite / Reroute a train |
| POST | `/api/simulate/whatif` | Run what-if scenario |
| GET | `/api/audit` | Audit trail |
| POST | `/api/refresh` | Simulate TMS data refresh |
| GET | `/api/section/status` | Track section statuses |

---

## Section Modeled
**Nagpur (NGP) → Akola (AKT)** — ~233 km
Stations: NGP · WR · SEG · DGN · BD · AMR · AKT

Trains: Express, Superfast, Rajdhani, Local, Freight, Special, Maintenance Block

---

*Built for SIH 2024. Designed to assist, not replace, the experienced section controller.*
