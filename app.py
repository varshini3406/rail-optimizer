"""
Rail Optimizer - Flask Backend
REST API for Rail Optimization Decision Support System
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, render_template
import random
import time

from models.railway_models import TrainStatus, TrackStatus
from data.data_generator import (
    generate_trains, generate_stations, generate_sections, compute_kpis
)
from algorithms.optimizer import (
    ConflictDetector, PrecedenceScheduler, GreedyOptimizer, WhatIfSimulator
)

app = Flask(__name__)

# ── In-memory state ──────────────────────────────────────────────────────────
trains = generate_trains()
stations = generate_stations()
sections = generate_sections()
detector = ConflictDetector()
scheduler = PrecedenceScheduler()
optimizer = GreedyOptimizer()
simulator = WhatIfSimulator()
audit_log = []

conflicts = detector.detect_conflicts(trains, sections)
resolved_count = sum(1 for c in conflicts if c.resolved)


def log_action(action: str, details: str):
    audit_log.append({
        "timestamp": time.strftime("%H:%M:%S"),
        "action": action,
        "details": details,
        "user": "Controller-01",
    })
    if len(audit_log) > 50:
        audit_log.pop(0)


# ── API Routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard")
def dashboard():
    global conflicts, resolved_count
    kpis = compute_kpis(trains, len(conflicts), resolved_count)
    return jsonify({
        "kpis": kpis.to_dict(),
        "trains": [t.to_dict() for t in trains],
        "stations": {k: v.to_dict() for k, v in stations.items()},
        "sections": {k: v.to_dict() for k, v in sections.items()},
        "conflicts": [c.to_dict() for c in conflicts if not c.resolved],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.route("/api/trains")
def get_trains():
    return jsonify([t.to_dict() for t in trains])


@app.route("/api/conflicts")
def get_conflicts():
    return jsonify([c.to_dict() for c in conflicts])


@app.route("/api/schedule")
def get_schedule():
    order = scheduler.schedule(trains)
    return jsonify(order)


@app.route("/api/optimize")
def optimize():
    result = optimizer.optimize(trains, iterations=100)
    log_action("OPTIMIZE", f"Ran greedy optimizer. Saved {result['improvement']} min delay.")
    return jsonify(result)


@app.route("/api/conflict/resolve/<conflict_id>", methods=["POST"])
def resolve_conflict(conflict_id):
    global resolved_count
    for c in conflicts:
        if c.conflict_id == conflict_id:
            c.resolved = True
            resolved_count += 1
            log_action("RESOLVE_CONFLICT", f"Resolved {conflict_id} between {c.train_a} and {c.train_b}")
            return jsonify({"success": True, "message": f"Conflict {conflict_id} resolved"})
    return jsonify({"success": False, "message": "Conflict not found"}), 404


@app.route("/api/train/action", methods=["POST"])
def train_action():
    data = request.get_json()
    train_no = data.get("train_no")
    action = data.get("action")

    for train in trains:
        if train.train_no == train_no:
            if action == "HOLD":
                train.status = TrainStatus.HALTED
                train.speed_kmh = 0
                log_action("HOLD_TRAIN", f"Train {train_no} ({train.name}) held at {train.current_station}")
                return jsonify({"success": True, "message": f"{train.name} held at {train.current_station}"})
            elif action == "PROCEED":
                train.status = TrainStatus.RUNNING
                train.speed_kmh = max(60, train.speed_kmh or 80)
                log_action("RELEASE_TRAIN", f"Train {train_no} ({train.name}) released")
                return jsonify({"success": True, "message": f"{train.name} cleared to proceed"})
            elif action == "EXPEDITE":
                train.delay_minutes = max(0, train.delay_minutes - 5)
                log_action("EXPEDITE_TRAIN", f"Train {train_no} priority expedited")
                return jsonify({"success": True, "message": f"{train.name} expedited"})
            elif action == "REROUTE":
                train.status = TrainStatus.REROUTED
                train.delay_minutes += 8
                log_action("REROUTE_TRAIN", f"Train {train_no} rerouted")
                return jsonify({"success": True, "message": f"{train.name} rerouted via alternate path"})

    return jsonify({"success": False, "message": "Train not found"}), 404


@app.route("/api/simulate/whatif", methods=["POST"])
def what_if():
    data = request.get_json()
    scenario_type = data.get("type", "hold")
    train_no = data.get("train_no")

    train = next((t for t in trains if t.train_no == train_no), None)
    if not train:
        return jsonify({"error": "Train not found"}), 404

    if scenario_type == "hold":
        result = simulator.simulate_hold(train, data.get("hold_minutes", 10))
    elif scenario_type == "reroute":
        result = simulator.simulate_reroute(train, data.get("alt_route", "Alt Route"))
    else:
        result = {"error": "Unknown scenario type"}

    log_action("WHAT_IF", f"Simulated {scenario_type} for {train_no}")
    return jsonify(result)


@app.route("/api/audit")
def get_audit():
    return jsonify(list(reversed(audit_log)))


@app.route("/api/refresh", methods=["POST"])
def refresh_data():
    """Simulate real-time data refresh with slight changes"""
    for train in trains:
        if train.status == TrainStatus.RUNNING:
            # Simulate movement
            delta = random.uniform(-0.5, 1.5)
            train.delay_minutes = max(0, train.delay_minutes + delta)
            train.speed_kmh = max(50, min(130, train.speed_kmh + random.uniform(-3, 3)))

    global conflicts, resolved_count
    conflicts = detector.detect_conflicts(trains, sections)
    resolved_count = sum(1 for c in conflicts if c.resolved)
    log_action("DATA_REFRESH", "Real-time data refreshed from TMS")
    return jsonify({"success": True, "message": "Data refreshed"})


@app.route("/api/section/status")
def section_status():
    return jsonify({k: v.to_dict() for k, v in sections.items()})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  RAIL OPTIMIZER — Decision Support System")
    print("  SIH 2024 | Indian Railways")
    print("  Server: http://localhost:5000")
    print("=" * 60 + "\n")
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
