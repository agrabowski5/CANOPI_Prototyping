"""
Network topology representation
Implements the network data structures from Section II of the CANOPI paper
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Node:
    """Electrical bus/node in the transmission network"""
    id: int
    name: str
    latitude: float
    longitude: float
    voltage_kv: int
    is_slack: bool = False


@dataclass
class Branch:
    """AC transmission line or transformer"""
    id: int
    from_node: int  # Node index
    to_node: int  # Node index
    capacity_mw: float  # w_br in paper
    impedance: float  # χ_0 in paper (per unit)
    voltage_kv: int
    length_km: Optional[float] = None


@dataclass
class HVDCLine:
    """High-voltage DC transmission line"""
    id: int
    from_node: int
    to_node: int
    capacity_mw: float  # w_dc in paper


class Network:
    """
    Transmission network topology

    Corresponds to Section II model parameters:
    - n nodes
    - b AC branches
    - β HVDC lines
    - A^br: branch incidence matrix
    - A^dc: HVDC incidence matrix
    """

    def __init__(
        self,
        nodes: List[Node],
        branches: List[Branch],
        hvdc_lines: Optional[List[HVDCLine]] = None
    ):
        self.nodes = nodes
        self.branches = branches
        self.hvdc_lines = hvdc_lines or []

        # Dimensions (from paper notation)
        self.n = len(nodes)  # Number of nodes
        self.b = len(branches)  # Number of AC branches
        self.β = len(self.hvdc_lines)  # Number of HVDC lines (beta)

        # Build incidence matrices
        self.A_br = self._build_branch_incidence_matrix()
        if self.hvdc_lines:
            self.A_dc = self._build_hvdc_incidence_matrix()
        else:
            self.A_dc = np.zeros((self.n, 0))

        # Cycle basis (will be computed by cycle_basis algorithm)
        self.D: Optional[np.ndarray] = None
        self.n_c: Optional[int] = None  # Number of cycles

    def _build_branch_incidence_matrix(self) -> np.ndarray:
        """
        Build branch incidence matrix A^br ∈ {-1, 0, 1}^{n×b}

        For each branch j with arbitrarily assigned "from" and "to" buses:
        - A^br[i_from, j] = -1
        - A^br[i_to, j] = 1
        - All other entries are 0

        (See Section II in paper)
        """
        A_br = np.zeros((self.n, self.b), dtype=int)

        for j, branch in enumerate(self.branches):
            A_br[branch.from_node, j] = -1
            A_br[branch.to_node, j] = 1

        return A_br

    def _build_hvdc_incidence_matrix(self) -> np.ndarray:
        """
        Build HVDC incidence matrix A^dc ∈ {-1, 0, 1}^{n×β}
        Similar to AC branch incidence
        """
        A_dc = np.zeros((self.n, self.β), dtype=int)

        for j, line in enumerate(self.hvdc_lines):
            A_dc[line.from_node, j] = -1
            A_dc[line.to_node, j] = 1

        return A_dc

    def get_branch_capacities(self) -> np.ndarray:
        """Get vector of branch capacities w^br ∈ R^b"""
        return np.array([b.capacity_mw for b in self.branches])

    def get_branch_impedances(self) -> np.ndarray:
        """Get vector of branch impedances χ^0 ∈ R^b"""
        return np.array([b.impedance for b in self.branches])

    def get_susceptances(self, capacity_additions: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculate branch susceptances B = diag(χ)^{-1}

        Args:
            capacity_additions: Optional x^br capacity additions for impedance feedback

        Returns:
            Susceptance vector (inverse of impedances)
        """
        impedances = self.get_branch_impedances()

        if capacity_additions is not None:
            # Apply impedance feedback: χ_j(x^br_j) = χ^0_j * w^br_j / (w^br_j + x^br_j)
            # (Equation 10 in paper)
            w_br = self.get_branch_capacities()
            impedances = impedances * w_br / (w_br + capacity_additions)

        return 1.0 / impedances

    def identify_non_islanding_branches(self) -> List[int]:
        """
        Identify non-bridge edges (branches that don't disconnect the graph when removed)
        These are the branches that should be included in contingency analysis

        Returns:
            List of branch indices for n-1 contingency analysis
        """
        # TODO: Implement graph connectivity check
        # An edge is a bridge if and only if it is not contained in any cycle
        # For now, assume all branches are non-islanding (conservative)
        return list(range(self.b))

    def set_cycle_basis(self, D: np.ndarray):
        """
        Set the cycle basis matrix computed by Algorithm 3

        Args:
            D: Cycle basis matrix ∈ {-1, 0, 1}^{n_c × b}
        """
        self.D = D
        self.n_c = D.shape[0]

    def __repr__(self) -> str:
        return (
            f"Network(nodes={self.n}, branches={self.b}, "
            f"hvdc={self.β}, cycles={self.n_c})"
        )
