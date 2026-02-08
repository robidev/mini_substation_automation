"""
Data models for relay system
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict


class BreakerState(Enum):
    """Breaker status enumeration"""
    INTERMEDIATE = "INTERMEDIATE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


@dataclass
class RelayData:
    """Data structure for relay measurements and status"""
    name: str
    voltage_l1: float = 0.0
    voltage_l2: float = 0.0
    voltage_l3: float = 0.0
    current_l1: float = 0.0
    current_l2: float = 0.0
    current_l3: float = 0.0
    breaker_state: BreakerState = BreakerState.UNKNOWN
    connected: bool = False
    # Additional IEC61850 data
    cbr1_state: str = "UNKNOWN"
    swi1_state: str = "UNKNOWN"
    swi2_state: str = "UNKNOWN"
    swi3_state: str = "UNKNOWN"
    ctr1_data: Optional[Dict] = None
    vtr1_data: Optional[Dict] = None
    vtr2_data: Optional[Dict] = None
    set0_loc: str = "UNKNOWN"
    set1_Ilarge: float = 0.0
    set2_Tm: float = 0.0
