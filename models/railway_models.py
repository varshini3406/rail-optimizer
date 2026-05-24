"""
Rail Optimizer - Core Data Models
SIH Problem: Indian Railways Train Optimization
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum
import random
import time


class TrainType(Enum):
    EXPRESS = "Express"
    SUPERFAST = "Superfast"
    RAJDHANI = "Rajdhani"
    SHATABDI = "Shatabdi"
    LOCAL = "Local"
    FREIGHT = "Freight"
    SPECIAL = "Special"
    MAINTENANCE = "Maintenance Block"


class TrainStatus(Enum):
    ON_TIME = "On Time"
    DELAYED = "Delayed"
    HALTED = "Halted"
    REROUTED = "Rerouted"
    CANCELLED = "Cancelled"
    RUNNING = "Running"


class TrackStatus(Enum):
    CLEAR = "Clear"
    OCCUPIED = "Occupied"
    BLOCKED = "Blocked"
    MAINTENANCE = "Maintenance"


TRAIN_PRIORITY = {
    TrainType.RAJDHANI: 1,
    TrainType.SHATABDI: 2,
    TrainType.SUPERFAST: 3,
    TrainType.EXPRESS: 4,
    TrainType.SPECIAL: 5,
    TrainType.LOCAL: 6,
    TrainType.FREIGHT: 7,
    TrainType.MAINTENANCE: 8,
}


@dataclass
class Station:
    code: str
    name: str
    platform_count: int
    platforms_available: int
    position_km: float  # distance from section start

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "platform_count": self.platform_count,
            "platforms_available": self.platforms_available,
            "position_km": self.position_km,
        }


@dataclass
class TrackSection:
    section_id: str
    from_station: str
    to_station: str
    length_km: float
    max_speed_kmh: float
    is_double_line: bool
    status: TrackStatus = TrackStatus.CLEAR
    occupied_by: Optional[str] = None  # train number

    def to_dict(self):
        return {
            "section_id": self.section_id,
            "from_station": self.from_station,
            "to_station": self.to_station,
            "length_km": round(self.length_km, 1),
            "max_speed_kmh": self.max_speed_kmh,
            "is_double_line": self.is_double_line,
            "status": self.status.value,
            "occupied_by": self.occupied_by,
        }


@dataclass
class Train:
    train_no: str
    name: str
    train_type: TrainType
    origin: str
    destination: str
    current_station: str
    next_station: str
    scheduled_departure: float   # minutes from epoch
    actual_departure: Optional[float]
    delay_minutes: float
    speed_kmh: float
    status: TrainStatus
    priority: int = field(init=False)
    coaches: int = 20
    current_section: Optional[str] = None

    def __post_init__(self):
        self.priority = TRAIN_PRIORITY[self.train_type]

    def to_dict(self):
        return {
            "train_no": self.train_no,
            "name": self.name,
            "train_type": self.train_type.value,
            "origin": self.origin,
            "destination": self.destination,
            "current_station": self.current_station,
            "next_station": self.next_station,
            "scheduled_departure": self.scheduled_departure,
            "actual_departure": self.actual_departure,
            "delay_minutes": round(self.delay_minutes, 1),
            "speed_kmh": round(self.speed_kmh, 1),
            "status": self.status.value,
            "priority": self.priority,
            "coaches": self.coaches,
            "current_section": self.current_section,
        }


@dataclass
class Conflict:
    conflict_id: str
    train_a: str
    train_b: str
    section: str
    conflict_type: str  # "CROSSING", "PRECEDENCE", "PLATFORM"
    time_to_conflict: float  # minutes
    recommendation: str
    resolved: bool = False

    def to_dict(self):
        return {
            "conflict_id": self.conflict_id,
            "train_a": self.train_a,
            "train_b": self.train_b,
            "section": self.section,
            "conflict_type": self.conflict_type,
            "time_to_conflict": round(self.time_to_conflict, 1),
            "recommendation": self.recommendation,
            "resolved": self.resolved,
        }


@dataclass
class KPIMetrics:
    total_trains: int
    on_time_percentage: float
    avg_delay_minutes: float
    throughput_per_hour: float
    platform_utilization: float
    section_utilization: float
    conflicts_detected: int
    conflicts_resolved: int

    def to_dict(self):
        return {
            "total_trains": self.total_trains,
            "on_time_percentage": round(self.on_time_percentage, 1),
            "avg_delay_minutes": round(self.avg_delay_minutes, 1),
            "throughput_per_hour": round(self.throughput_per_hour, 1),
            "platform_utilization": round(self.platform_utilization, 1),
            "section_utilization": round(self.section_utilization, 1),
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
        }
