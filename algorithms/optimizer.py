"""
Rail Optimizer - Core Optimization Algorithms
Implements conflict detection, precedence resolution, and greedy schedule optimization
"""

import heapq
import random
from typing import List, Dict, Tuple, Optional
from models.railway_models import (
    Train, TrackSection, Station, Conflict,
    TrainStatus, TrackStatus, TrainType
)


class ConflictDetector:
    """Detects crossing and precedence conflicts between trains"""

    def detect_conflicts(
        self,
        trains: List[Train],
        sections: Dict[str, TrackSection]
    ) -> List[Conflict]:
        conflicts = []
        conflict_id = 1

        for i, train_a in enumerate(trains):
            for j, train_b in enumerate(trains):
                if i >= j:
                    continue
                if train_a.status in [TrainStatus.CANCELLED, TrainStatus.HALTED]:
                    continue
                if train_b.status in [TrainStatus.CANCELLED, TrainStatus.HALTED]:
                    continue

                # Check if both trains are heading to the same next station
                if train_a.next_station == train_b.next_station:
                    section_key = f"{train_a.current_station}-{train_a.next_station}"
                    section = sections.get(section_key)

                    if section and not section.is_double_line:
                        # Single line conflict - crossing needed
                        time_to_conflict = abs(train_a.delay_minutes - train_b.delay_minutes) + random.uniform(2, 8)

                        if train_a.priority <= train_b.priority:
                            rec = f"Hold {train_b.train_no} at {train_b.current_station}; allow {train_a.train_no} ({train_a.train_type.value}) to proceed first"
                        else:
                            rec = f"Hold {train_a.train_no} at {train_a.current_station}; allow {train_b.train_no} ({train_b.train_type.value}) to proceed first"

                        conflict = Conflict(
                            conflict_id=f"CF{conflict_id:04d}",
                            train_a=train_a.train_no,
                            train_b=train_b.train_no,
                            section=section_key,
                            conflict_type="CROSSING",
                            time_to_conflict=time_to_conflict,
                            recommendation=rec,
                        )
                        conflicts.append(conflict)
                        conflict_id += 1

                # Check platform conflict at next station
                if (train_a.next_station == train_b.next_station and
                        abs(train_a.delay_minutes - train_b.delay_minutes) < 5):
                    station_code = train_a.next_station
                    conflict = Conflict(
                        conflict_id=f"CF{conflict_id:04d}",
                        train_a=train_a.train_no,
                        train_b=train_b.train_no,
                        section=station_code,
                        conflict_type="PLATFORM",
                        time_to_conflict=random.uniform(3, 12),
                        recommendation=f"Assign separate platforms at {station_code}; delay {train_b.train_no} arrival by 4 min",
                        resolved=random.random() > 0.5,
                    )
                    conflicts.append(conflict)
                    conflict_id += 1

        return conflicts[:12]  # Return top conflicts


class PrecedenceScheduler:
    """
    Priority-based greedy scheduler using a min-heap.
    Assigns train movement order based on type, delay, and section capacity.
    """

    def schedule(self, trains: List[Train]) -> List[Dict]:
        heap = []
        for train in trains:
            if train.status not in [TrainStatus.CANCELLED]:
                # Score: lower is higher priority
                score = train.priority * 10 - train.delay_minutes * 0.5
                heapq.heappush(heap, (score, train.train_no, train))

        schedule_order = []
        slot = 0
        while heap:
            score, tno, train = heapq.heappop(heap)
            schedule_order.append({
                "slot": slot + 1,
                "train_no": train.train_no,
                "name": train.name,
                "type": train.train_type.value,
                "priority": train.priority,
                "action": self._decide_action(train, slot),
                "from": train.current_station,
                "to": train.next_station,
                "delay": round(train.delay_minutes, 1),
                "status": train.status.value,
            })
            slot += 1

        return schedule_order

    def _decide_action(self, train: Train, slot: int) -> str:
        if train.delay_minutes > 20:
            return "EXPEDITE - Grant Green Signal Priority"
        elif train.status == TrainStatus.HALTED:
            return "RELEASE - Clear for departure"
        elif slot == 0:
            return "PROCEED - Immediate green signal"
        elif slot < 3:
            return "PROCEED - Next available slot"
        else:
            return "HOLD - Await clearance"


class GreedyOptimizer:
    """
    Greedy optimization to minimize total delay across section.
    Uses exchange-based local search to improve initial greedy solution.
    """

    def optimize(self, trains: List[Train], iterations: int = 50) -> Dict:
        active = [t for t in trains if t.status != TrainStatus.CANCELLED]
        if not active:
            return {"improvement": 0, "optimized_delay": 0, "baseline_delay": 0}

        baseline_delay = sum(t.delay_minutes for t in active)

        # Local search: try swapping pairs to reduce total delay
        best_order = list(active)
        best_delay = self._evaluate(best_order)

        for _ in range(iterations):
            i, j = random.sample(range(len(best_order)), 2)
            candidate = best_order[:]
            candidate[i], candidate[j] = candidate[j], candidate[i]
            candidate_delay = self._evaluate(candidate)
            if candidate_delay < best_delay:
                best_delay = candidate_delay
                best_order = candidate

        improvement = max(0, baseline_delay - best_delay)
        return {
            "improvement": round(improvement, 1),
            "optimized_delay": round(best_delay, 1),
            "baseline_delay": round(baseline_delay, 1),
            "optimized_order": [t.train_no for t in best_order],
        }

    def _evaluate(self, trains: List[Train]) -> float:
        """Weighted delay: higher priority trains contribute more penalty"""
        total = 0.0
        for idx, train in enumerate(trains):
            weight = (9 - train.priority) + 1  # higher priority = higher weight
            position_penalty = idx * 0.5  # later in queue = more delay
            total += (train.delay_minutes + position_penalty) * weight
        return total


class WhatIfSimulator:
    """Simulates alternate scenarios for what-if analysis"""

    def simulate_hold(self, train: Train, hold_minutes: float) -> Dict:
        new_delay = train.delay_minutes + hold_minutes
        return {
            "scenario": f"Hold {train.train_no} for {hold_minutes} min",
            "original_delay": round(train.delay_minutes, 1),
            "new_delay": round(new_delay, 1),
            "impact": f"+{hold_minutes:.0f} min delay to {train.name}",
            "recommendation": "Only if higher priority train needs clearance",
        }

    def simulate_reroute(self, train: Train, alt_route: str) -> Dict:
        extra_distance = random.uniform(10, 40)
        extra_time = extra_distance / train.speed_kmh * 60
        return {
            "scenario": f"Reroute {train.train_no} via {alt_route}",
            "extra_distance_km": round(extra_distance, 1),
            "extra_time_min": round(extra_time, 1),
            "original_delay": round(train.delay_minutes, 1),
            "new_delay": round(train.delay_minutes + extra_time, 1),
            "feasibility": "High" if extra_time < 20 else "Medium",
        }

    def simulate_platform_swap(self, train_a: Train, train_b: Train) -> Dict:
        return {
            "scenario": f"Swap platforms: {train_a.train_no} ↔ {train_b.train_no}",
            "benefit": f"Reduces platform conflict at {train_a.next_station}",
            "time_saved_min": round(random.uniform(2, 8), 1),
            "feasibility": "High",
            "recommendation": "Execute if platform assignments are flexible",
        }
