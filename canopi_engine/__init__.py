"""
CANOPI Optimization Engine
Implementation of the CANOPI algorithm from:
Lee, T., & Sun, A. (2025). CANOPI: Contingency-Aware Nodal Optimal
Power Investments with High Temporal Resolution.
"""

__version__ = "0.1.0"
__author__ = "CANOPI Development Team"

from .models.network import Network
from .models.capacity_decision import CapacityDecision
from .models.operational import OperationalVariables

__all__ = [
    "Network",
    "CapacityDecision",
    "OperationalVariables",
]
