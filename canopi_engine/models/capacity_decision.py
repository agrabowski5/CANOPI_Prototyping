"""
Capacity decision variables
Implements x = (x^g, x^es, x^br, x^em) from Section II-A of the paper
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class CapacityDecision:
    """
    Capacity expansion decision variables

    Corresponds to Section II-A:
    - x^g: new generation capacities (G generators)
    - x^es-p: storage power capacities (S storage devices)
    - x^es-e: storage energy capacities (S storage devices)
    - x^br: transmission capacity additions (b branches)
    - x^em: emissions allocation across scenarios (|Ω| scenarios)
    """

    x_g: np.ndarray  # Generation capacity additions (G,)
    x_es_p: np.ndarray  # Storage power capacity (S,)
    x_es_e: np.ndarray  # Storage energy capacity (S,)
    x_br: np.ndarray  # Transmission capacity additions (b,)
    x_em: np.ndarray  # Emissions allocation (|Ω|,)

    def __post_init__(self):
        """Validate dimensions and values"""
        # All capacities must be non-negative
        assert np.all(self.x_g >= 0), "Generation capacities must be non-negative"
        assert np.all(self.x_es_p >= 0), "Storage power must be non-negative"
        assert np.all(self.x_es_e >= 0), "Storage energy must be non-negative"
        assert np.all(self.x_br >= 0), "Transmission additions must be non-negative"
        assert np.all(self.x_em >= 0), "Emissions must be non-negative"

        # Storage energy must be consistent with power (e.g., 4-hour batteries)
        # This constraint can be enforced in the optimization problem

    @property
    def total_generation_gw(self) -> float:
        """Total new generation capacity in GW"""
        return np.sum(self.x_g) / 1000.0

    @property
    def total_storage_power_gw(self) -> float:
        """Total storage power capacity in GW"""
        return np.sum(self.x_es_p) / 1000.0

    @property
    def total_storage_energy_gwh(self) -> float:
        """Total storage energy capacity in GWh"""
        return np.sum(self.x_es_e) / 1000.0

    @property
    def total_transmission_gw(self) -> float:
        """Total transmission capacity additions in GW"""
        return np.sum(self.x_br) / 1000.0

    @property
    def total_emissions(self) -> float:
        """Total emissions allocation across all scenarios"""
        return np.sum(self.x_em)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "generation_gw": self.total_generation_gw,
            "storage_power_gw": self.total_storage_power_gw,
            "storage_energy_gwh": self.total_storage_energy_gwh,
            "transmission_gw": self.total_transmission_gw,
            "total_emissions": self.total_emissions,
            "x_g": self.x_g.tolist(),
            "x_es_p": self.x_es_p.tolist(),
            "x_es_e": self.x_es_e.tolist(),
            "x_br": self.x_br.tolist(),
            "x_em": self.x_em.tolist(),
        }

    @classmethod
    def zeros(cls, n_generators: int, n_storage: int, n_branches: int, n_scenarios: int):
        """Create a zero capacity decision (no investments)"""
        return cls(
            x_g=np.zeros(n_generators),
            x_es_p=np.zeros(n_storage),
            x_es_e=np.zeros(n_storage),
            x_br=np.zeros(n_branches),
            x_em=np.zeros(n_scenarios),
        )

    def __repr__(self) -> str:
        return (
            f"CapacityDecision(gen={self.total_generation_gw:.1f}GW, "
            f"storage={self.total_storage_power_gw:.1f}GW, "
            f"trans={self.total_transmission_gw:.1f}GW)"
        )


class CapacityLimits:
    """
    Upper bounds on capacity decisions
    Corresponds to x̄ in the feasibility region X (Equation 1)
    """

    def __init__(
        self,
        x_g_max: np.ndarray,
        x_es_p_max: np.ndarray,
        x_es_e_max: np.ndarray,
        x_br_max: np.ndarray,
        x_em_max: float,
    ):
        self.x_g_max = x_g_max
        self.x_es_p_max = x_es_p_max
        self.x_es_e_max = x_es_e_max
        self.x_br_max = x_br_max
        self.x_em_max = x_em_max

    def is_feasible(self, x: CapacityDecision) -> bool:
        """Check if a capacity decision satisfies upper bounds"""
        return (
            np.all(x.x_g <= self.x_g_max)
            and np.all(x.x_es_p <= self.x_es_p_max)
            and np.all(x.x_es_e <= self.x_es_e_max)
            and np.all(x.x_br <= self.x_br_max)
            and np.sum(x.x_em) <= self.x_em_max
        )


class InvestmentCosts:
    """
    Investment cost coefficients
    Corresponds to c in c^T x (Equation 2)
    """

    def __init__(
        self,
        c_g: np.ndarray,  # Generation capex ($/MW)
        c_es_p: np.ndarray,  # Storage power capex ($/MW)
        c_es_e: np.ndarray,  # Storage energy capex ($/MWh)
        c_br: np.ndarray,  # Transmission capex ($/MW)
        c_em: np.ndarray,  # Emissions penalty ($/ton CO2)
    ):
        self.c_g = c_g
        self.c_es_p = c_es_p
        self.c_es_e = c_es_e
        self.c_br = c_br
        self.c_em = c_em

    def calculate_cost(self, x: CapacityDecision) -> float:
        """Calculate total investment cost c^T x"""
        return (
            np.dot(self.c_g, x.x_g)
            + np.dot(self.c_es_p, x.x_es_p)
            + np.dot(self.c_es_e, x.x_es_e)
            + np.dot(self.c_br, x.x_br)
            + np.dot(self.c_em, x.x_em)
        )
