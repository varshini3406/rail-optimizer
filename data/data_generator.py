"""
Rail Optimizer - Realistic Indian Railways Sample Data Generator
Simulates a section between major stations
"""

import random
import time
from typing import List, Dict, Tuple
from models.railway_models import (
    Train, TrackSection, Station, TrainType,
    TrainStatus, TrackStatus, KPIMetrics
)

# Simulated section: Nagpur - Wardha - Sevagram - Wardha - Dhamangaon - Badnera
STATIONS_DATA = [
    ("NGP", "Nagpur", 8, 6, 0.0),
    ("WR",  "Wardha",  4, 3, 75.0),
    ("SEG", "Sevagram", 2, 2, 83.0),
    ("DGN", "Dhamangaon", 3, 2, 118.0),
    ("BD",  "Badnera", 5, 4, 157.0),
    ("AMR", "Amravati", 4, 3, 164.0),
    ("AKT", "Akola", 6, 5, 233.0),
]

SECTIONS_DATA = [
    ("NGP-WR",  "NGP", "WR",  75.0,  110, True),
    ("WR-SEG",  "WR",  "SEG",  8.0,   80, False),
    ("SEG-DGN", "SEG", "DGN", 35.0,  100, False),
    ("DGN-BD",  "DGN", "BD",  39.0,  110, True),
    ("BD-AMR",  "BD",  "AMR",  7.0,   80, False),
    ("AMR-AKT", "AMR", "AKT", 69.0,  110, True),
]

TRAINS_DATA = [
    ("12101", "Vidarbha Express", TrainType.EXPRESS, "NGP", "AKT", "NGP", "WR"),
    ("12105", "Gondwana Express", TrainType.SUPERFAST, "NGP", "AKT", "WR", "DGN"),
    ("12625", "Kerala Express", TrainType.EXPRESS, "NGP", "AKT", "DGN", "BD"),
    ("12139", "Sewagram Express", TrainType.EXPRESS, "NGP", "SEG", "NGP", "WR"),
    ("22127", "Anandwan Express", TrainType.SUPERFAST, "NGP", "AKT", "SEG", "DGN"),
    ("12434", "Hazrat Nizamuddin Rajdhani", TrainType.RAJDHANI, "NGP", "AKT", "NGP", "WR"),
    ("52101", "Nagpur Freight", TrainType.FREIGHT, "NGP", "AKT", "WR", "SEG"),
    ("07331", "Wardha Special", TrainType.SPECIAL, "WR", "AKT", "WR", "DGN"),
    ("71401", "Nagpur-Wardha Local", TrainType.LOCAL, "NGP", "WR", "NGP", "WR"),
    ("00500", "Maint Block Vidarbha", TrainType.MAINTENANCE, "DGN", "BD", "DGN", "BD"),
    ("12151", "Samarsata Express", TrainType.SUPERFAST, "NGP", "AKT", "BD", "AMR"),
    ("11071", "Kamayani Express", TrainType.EXPRESS, "AKT", "NGP", "AKT", "AMR"),
    ("12810", "Mumbai Howrah Mail", TrainType.EXPRESS, "AKT", "NGP", "AMR", "BD"),
    ("12534", "Pushpak SF Express", TrainType.SUPERFAST, "AKT", "NGP", "BD", "DGN"),
    ("12702", "Hussain Sagar Express", TrainType.EXPRESS, "NGP", "AKT", "NGP", "WR"),
]


def generate_stations() -> Dict[str, Station]:
    stations = {}
    for code, name, plat_count, plat_avail, pos in STATIONS_DATA:
        stations[code] = Station(code, name, plat_count, plat_avail, pos)
    return stations


def generate_sections() -> Dict[str, TrackSection]:
    sections = {}
    occupied = ["WR-SEG", "DGN-BD"]
    for sid, frm, to, length, speed, double in SECTIONS_DATA:
        status = TrackStatus.OCCUPIED if sid in occupied else TrackStatus.CLEAR
        occupied_by = None
        if sid == "WR-SEG":
            occupied_by = "52101"
        elif sid == "DGN-BD":
            occupied_by = "12625"
        sections[sid] = TrackSection(
            section_id=sid,
            from_station=frm,
            to_station=to,
            length_km=length,
            max_speed_kmh=speed,
            is_double_line=double,
            status=status,
            occupied_by=occupied_by,
        )
    return sections


def generate_trains() -> List[Train]:
    trains = []
    delays = [0, 0, 5, 12, 0, 0, 28, 8, 3, 0, 15, 7, 22, 4, 0]
    statuses = [
        TrainStatus.RUNNING, TrainStatus.RUNNING, TrainStatus.DELAYED,
        TrainStatus.DELAYED, TrainStatus.RUNNING, TrainStatus.ON_TIME,
        TrainStatus.DELAYED, TrainStatus.DELAYED, TrainStatus.RUNNING,
        TrainStatus.HALTED, TrainStatus.DELAYED, TrainStatus.DELAYED,
        TrainStatus.DELAYED, TrainStatus.RUNNING, TrainStatus.ON_TIME,
    ]
    speeds = [95, 105, 88, 82, 100, 115, 65, 78, 60, 0, 98, 90, 85, 102, 110]
    sections = [
        "NGP-WR", "WR-SEG", "DGN-BD", None, "SEG-DGN",
        "NGP-WR", "WR-SEG", "WR-SEG", "NGP-WR", "DGN-BD",
        "BD-AMR", "AMR-AKT", "AMR-BD", "BD-DGN", "NGP-WR",
    ]

    base_time = 480.0  # 8:00 AM in minutes
    for i, (no, name, ttype, orig, dest, cur, nxt) in enumerate(TRAINS_DATA):
        sched = base_time + i * 12 + random.uniform(-5, 5)
        delay = delays[i] + random.uniform(-1, 2)
        delay = max(0, delay)
        train = Train(
            train_no=no,
            name=name,
            train_type=ttype,
            origin=orig,
            destination=dest,
            current_station=cur,
            next_station=nxt,
            scheduled_departure=sched,
            actual_departure=sched + delay,
            delay_minutes=delay,
            speed_kmh=speeds[i],
            status=statuses[i],
            coaches=random.choice([18, 20, 22, 24]),
            current_section=sections[i],
        )
        trains.append(train)
    return trains


def compute_kpis(trains: List[Train], conflicts_detected: int, conflicts_resolved: int) -> KPIMetrics:
    active = [t for t in trains if t.status != TrainStatus.CANCELLED]
    on_time = sum(1 for t in active if t.delay_minutes < 5)
    avg_delay = sum(t.delay_minutes for t in active) / max(len(active), 1)
    return KPIMetrics(
        total_trains=len(active),
        on_time_percentage=(on_time / max(len(active), 1)) * 100,
        avg_delay_minutes=avg_delay,
        throughput_per_hour=round(len(active) / 3.5, 1),
        platform_utilization=round(random.uniform(65, 85), 1),
        section_utilization=round(random.uniform(70, 90), 1),
        conflicts_detected=conflicts_detected,
        conflicts_resolved=conflicts_resolved,
    )
