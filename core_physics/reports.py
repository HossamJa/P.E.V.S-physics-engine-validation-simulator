from dataclasses import dataclass
from typing import List

@dataclass
class EngineReport:
    exhaust_momentum: List[float] = None
    energy_drawn: float = 0.0
    mass_spent: float = 0.0
    field_work: float = 0.0
    exhaust_energy: float = 0.0
    radiation_energy: float = 0.0
    active: bool = False

    source: str = "engine"
    channel: str = "ship"

    def __post_init__(self):
        if self.exhaust_momentum is None:
            self.exhaust_momentum = [0.0, 0.0, 0.0]


@dataclass
class EnvironmentReport:
    momentum_exchange: List[float] = None
    energy_exchange: float = 0.0
    mass_exchange: float = 0.0
    field_work: float = 0.0
    source: str = "environment"
    channel: str = "field"
    field_momentum = [0.0, 0.0, 0.0]

    def __post_init__(self):
        if self.momentum_exchange is None:
            self.momentum_exchange = [0.0, 0.0, 0.0]
