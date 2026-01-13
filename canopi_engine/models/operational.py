"""
Operational variables for the subproblem
Implements y_ω from Section II-B of the paper
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class OperationalVariables:
    """
    Operational decision variables for a single scenario ω

    Corresponds to Section II-B operational subproblem:
    - p^g: generation output (T × G)
    - r^g: generator reserves (T × G)
    - p^es: storage net output (T × S)
    - p^chg, p^dis: storage charge/discharge (T × S)
    - q: state of charge (T × S)
    - p^br: branch power flows (T × b)
    - p^dc: HVDC flows (T × β)
    - p^sh: load shedding (T × D)
    - p^brc: post-contingency branch flows (T × b × B)
    - s^c: contingency slack variables (T × b × B)
    """

    # Generation
    p_g: np.ndarray  # Generation output (T, G)
    r_g: np.ndarray  # Generator reserves (T, G)

    # Storage
    p_es: np.ndarray  # Storage net output (T, S)
    p_chg: np.ndarray  # Storage charging (T, S)
    p_dis: np.ndarray  # Storage discharging (T, S)
    r_dis: np.ndarray  # Storage reserve contribution (T, S)
    q: np.ndarray  # State of charge (T, S)

    # Power flows
    p_br: np.ndarray  # Branch flows (T, b)
    p_dc: np.ndarray  # HVDC flows (T, β)

    # Reliability
    p_sh: np.ndarray  # Load shedding (T, D)

    # Contingencies (optional, may be added iteratively)
    p_brc: Optional[np.ndarray] = None  # Post-contingency flows (T, b, B)
    s_c: Optional[np.ndarray] = None  # Contingency slack (T, b, B)

    def __post_init__(self):
        """Validate dimensions and constraints"""
        T = self.p_g.shape[0]

        # Check time dimension consistency
        assert self.r_g.shape[0] == T
        assert self.p_es.shape[0] == T
        assert self.p_br.shape[0] == T
        assert self.p_sh.shape[0] == T

        # Non-negativity
        assert np.all(self.p_g >= -1e-6), "Generation must be non-negative"
        assert np.all(self.r_g >= -1e-6), "Reserves must be non-negative"
        assert np.all(self.p_chg >= -1e-6), "Charging must be non-negative"
        assert np.all(self.p_dis >= -1e-6), "Discharging must be non-negative"
        assert np.all(self.q >= -1e-6), "State of charge must be non-negative"
        assert np.all(self.p_sh >= -1e-6), "Load shedding must be non-negative"

    @property
    def T(self) -> int:
        """Number of time periods"""
        return self.p_g.shape[0]

    @property
    def total_generation_gwh(self) -> float:
        """Total generation across all time periods (GWh)"""
        return np.sum(self.p_g) / 1000.0

    @property
    def total_load_shed_gwh(self) -> float:
        """Total load shedding (GWh)"""
        return np.sum(self.p_sh) / 1000.0

    @property
    def max_branch_utilization(self) -> float:
        """Maximum branch utilization across all time periods"""
        # This would require branch capacities as input
        # For now, return the maximum flow
        return np.max(np.abs(self.p_br))

    def calculate_objective(
        self,
        c_g: np.ndarray,  # Generator operating costs (T, G)
        c_sh: float,  # Load shedding penalty ($/MWh)
        c_vio: float,  # Contingency violation penalty ($/MWh)
    ) -> float:
        """
        Calculate operational subproblem objective (Equation 14)

        z^T_ω y_ω = Σ_t [(c^g_ωt)^T p^g_ωt + c^sh 1^T p^sh_ωt + c^vio 1^T s^c_ωt]
        """
        # Generation costs
        gen_cost = np.sum(c_g * self.p_g)

        # Load shedding penalty
        shed_cost = c_sh * np.sum(self.p_sh)

        # Contingency violation penalty
        vio_cost = 0.0
        if self.s_c is not None:
            vio_cost = c_vio * np.sum(self.s_c)

        return gen_cost + shed_cost + vio_cost

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        result = {
            "T": self.T,
            "total_generation_gwh": self.total_generation_gwh,
            "total_load_shed_gwh": self.total_load_shed_gwh,
            "max_branch_flow": self.max_branch_utilization,
            "p_g": self.p_g.tolist(),
            "p_br": self.p_br.tolist(),
        }

        # Include contingency data if available
        if self.p_brc is not None:
            result["has_contingencies"] = True
            result["n_contingencies"] = self.p_brc.shape[2]
        else:
            result["has_contingencies"] = False

        return result

    @classmethod
    def zeros(
        cls,
        T: int,  # Time periods
        G: int,  # Generators
        S: int,  # Storage devices
        b: int,  # Branches
        β: int,  # HVDC lines
        D: int,  # Loads
    ):
        """Create zero operational variables (infeasible, just for initialization)"""
        return cls(
            p_g=np.zeros((T, G)),
            r_g=np.zeros((T, G)),
            p_es=np.zeros((T, S)),
            p_chg=np.zeros((T, S)),
            p_dis=np.zeros((T, S)),
            r_dis=np.zeros((T, S)),
            q=np.zeros((T, S)),
            p_br=np.zeros((T, b)),
            p_dc=np.zeros((T, β)),
            p_sh=np.zeros((T, D)),
        )

    def __repr__(self) -> str:
        return (
            f"OperationalVariables(T={self.T}, "
            f"gen={self.total_generation_gwh:.1f}GWh, "
            f"shed={self.total_load_shed_gwh:.3f}GWh)"
        )
