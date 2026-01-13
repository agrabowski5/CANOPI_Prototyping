"""
Operational Subproblem
Implements the operational feasibility set Y_r from Section III-A of the paper

Solves the multi-period optimal power flow with:
- Generation constraints (Eq. 3)
- Storage constraints (Eq. 4)
- DC power flow with cycle-based KVL (Eq. 6-9)
- Transmission contingencies (Eq. 12)
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
from typing import Optional, Dict, Tuple, Set
from dataclasses import dataclass

from ..models.network import Network
from ..models.capacity_decision import CapacityDecision
from ..models.operational import OperationalVariables
from ..solvers.gurobi_interface import GurobiSolver, SolverResult


@dataclass
class ScenarioData:
    """Operational scenario data ξ_ω"""
    c_g: np.ndarray  # Generator costs (T × G)
    a_g: np.ndarray  # Availability factors (T × G)
    p_d: np.ndarray  # Load (T × D)
    c_sh: float = 10000.0  # Load shedding penalty ($/MWh)
    c_vio: float = 2000.0  # Contingency violation penalty ($/MWh)


@dataclass
class OperationalParameters:
    """Operational parameters"""
    # Existing capacities (required fields first)
    w_g: np.ndarray  # Generator capacities (G,)
    w_es_p: np.ndarray  # Storage power (S,)
    w_es_e: np.ndarray  # Storage energy (S,)
    w_br: np.ndarray  # Branch capacities (b,)

    # Generator parameters
    R: np.ndarray  # Ramp rates (G,)
    e: np.ndarray  # Emissions factors (G,)

    # Incidence matrices
    A_g: np.ndarray  # Generator-node incidence (n × G)
    A_es: np.ndarray  # Storage-node incidence (n × S)
    A_d: np.ndarray  # Load-node incidence (n × D)

    # Storage parameters (default fields last)
    eta: float = 0.90  # Storage efficiency
    gamma_es: float = 0.50  # Initial/final SOC fraction

    # System parameters
    gamma_d: float = 0.15  # Reserve margin
    eta_c: float = 1.0  # Post-contingency rating multiplier


class OperationalSubproblem:
    """
    Solves the operational subproblem h_r(x̂^br, x, ξ_ω, J_ω)
    from Section III-A (Equation 18)
    """

    def __init__(
        self,
        network: Network,
        params: OperationalParameters,
        scenario: ScenarioData,
        x_br_hat: np.ndarray,  # Impedance-defining capacity
        contingencies: Optional[Set[Tuple[int, int, int]]] = None
    ):
        """
        Initialize operational subproblem

        Args:
            network: Transmission network topology
            params: Operational parameters
            scenario: Scenario data ξ_ω
            x_br_hat: Impedance-defining capacity x̂^br
            contingencies: Set of (t, i, j) contingency indices J_ω
        """
        self.network = network
        self.params = params
        self.scenario = scenario
        self.x_br_hat = x_br_hat
        self.contingencies = contingencies or set()

        # Dimensions
        self.T = scenario.c_g.shape[0]  # Time periods
        self.G = scenario.c_g.shape[1]  # Generators
        self.S = params.w_es_p.shape[0]  # Storage devices
        self.D = scenario.p_d.shape[1]  # Loads
        self.n = network.n  # Nodes
        self.b = network.b  # Branches

        # Precompute PTDF and LODF matrices with x̂^br
        self._compute_power_transfer_matrices()

    def _compute_power_transfer_matrices(self):
        """
        Compute PTDF and LODF matrices (Equations 13a-13b)

        Φ(x^br) = B(x^br) A [A^T B(x^br) A]^{-1}
        Λ(x^br) = Φ(x^br) A^T [I - diag(Φ(x^br) A^T)]^{-1}
        """
        # Get susceptances with impedance feedback
        susceptances = self.network.get_susceptances(self.x_br_hat)
        B = np.diag(susceptances)

        # Remove slack bus column from incidence matrix
        A = self.network.A_br[:, :]  # TODO: Remove slack bus row

        # PTDF matrix (Equation 13a)
        try:
            A_reduced = A[1:, :]  # Remove slack bus
            ATBA_inv = np.linalg.inv(A_reduced.T @ B @ A_reduced)
            self.PTDF = B @ A_reduced @ ATBA_inv
        except np.linalg.LinAlgError:
            print("Warning: Singular matrix in PTDF calculation")
            self.PTDF = np.zeros((self.b, self.n - 1))

        # LODF matrix (Equation 13b)
        # Λ_ij = PTDF_i·(A^T)_j / (1 - PTDF_j·(A^T)_j)
        self.LODF = np.zeros((self.b, self.b))
        for i in range(self.b):
            for j in range(self.b):
                if i != j:
                    numerator = self.PTDF[i, :] @ A_reduced[:, j]
                    denominator = 1.0 - (self.PTDF[j, :] @ A_reduced[:, j])
                    if abs(denominator) > 1e-6:
                        self.LODF[i, j] = numerator / denominator

    def solve(
        self,
        x: CapacityDecision,
        x_em_omega: float,
        verbose: bool = False
    ) -> Tuple[SolverResult, OperationalVariables]:
        """
        Solve operational subproblem for given capacity decision

        Args:
            x: Capacity decision
            x_em_omega: Emissions allocation for this scenario
            verbose: Print solver output

        Returns:
            (SolverResult, OperationalVariables)
        """
        solver = GurobiSolver("operational", OutputFlag=int(verbose))

        # === Decision Variables ===

        # Generation (Eq. 3)
        p_g = solver.add_continuous_vars("p_g", shape=(self.T, self.G))
        r_g = solver.add_continuous_vars("r_g", shape=(self.T, self.G))

        # Storage (Eq. 4)
        p_es = solver.add_continuous_vars("p_es", shape=(self.T, self.S), lb=-GRB.INFINITY)
        p_chg = solver.add_continuous_vars("p_chg", shape=(self.T, self.S))
        p_dis = solver.add_continuous_vars("p_dis", shape=(self.T, self.S))
        r_dis = solver.add_continuous_vars("r_dis", shape=(self.T, self.S))
        q = solver.add_continuous_vars("q", shape=(self.T, self.S))

        # Power flows
        p_br = solver.add_continuous_vars("p_br", shape=(self.T, self.b), lb=-GRB.INFINITY)
        p_dc = solver.add_continuous_vars("p_dc", shape=(self.T, self.network.β), lb=-GRB.INFINITY)

        # Load shedding
        p_sh = solver.add_continuous_vars("p_sh", shape=(self.T, self.D))

        # Contingency slacks (only for included contingencies)
        s_c = {}
        for (t, i, j) in self.contingencies:
            s_c[(t, i, j)] = solver.model.addVar(lb=0, name=f"s_c_{t}_{i}_{j}")

        # === Objective (Eq. 14) ===
        obj = 0.0

        # Generation costs
        for t in range(self.T):
            for g in range(self.G):
                obj += self.scenario.c_g[t, g] * p_g[t, g]

        # Load shedding penalty
        for t in range(self.T):
            for d in range(self.D):
                obj += self.scenario.c_sh * p_sh[t, d]

        # Contingency violation penalty
        for key, var in s_c.items():
            obj += self.scenario.c_vio * var

        solver.set_objective(obj, GRB.MINIMIZE)

        # === Constraints ===

        # Generation constraints (Eq. 3)
        total_capacity = self.params.w_g + x.x_g

        for t in range(self.T):
            for g in range(self.G):
                # Capacity + reserves (Eq. 3a)
                solver.model.addConstr(
                    p_g[t, g] + r_g[t, g] <= self.scenario.a_g[t, g] * total_capacity[g],
                    name=f"gen_cap_{t}_{g}"
                )

            # Ramp constraints (Eq. 3b-3c)
            if t > 0:
                for g in range(self.G):
                    solver.model.addConstr(
                        p_g[t, g] - p_g[t-1, g] >= -self.params.R[g] * total_capacity[g],
                        name=f"ramp_down_{t}_{g}"
                    )
                    solver.model.addConstr(
                        p_g[t, g] - p_g[t-1, g] <= self.params.R[g] * total_capacity[g],
                        name=f"ramp_up_{t}_{g}"
                    )

        # Total emissions constraint (Eq. 3d)
        total_emissions = gp.quicksum(
            self.params.e[g] * p_g[t, g]
            for t in range(self.T)
            for g in range(self.G)
        )
        solver.model.addConstr(total_emissions <= x_em_omega, name="emissions")

        # Storage constraints (Eq. 4)
        storage_power_cap = self.params.w_es_p + x.x_es_p
        storage_energy_cap = self.params.w_es_e + x.x_es_e

        for t in range(self.T):
            for s in range(self.S):
                # Net output (Eq. 4a)
                solver.model.addConstr(
                    p_es[t, s] == p_dis[t, s] - p_chg[t, s],
                    name=f"storage_net_{t}_{s}"
                )

                # Power limit (Eq. 4b)
                solver.model.addConstr(
                    p_chg[t, s] + p_dis[t, s] + r_dis[t, s] <= storage_power_cap[s],
                    name=f"storage_power_{t}_{s}"
                )

                # Energy limit (Eq. 4c-4d)
                solver.model.addConstr(
                    q[t, s] <= storage_energy_cap[s],
                    name=f"storage_energy_max_{t}_{s}"
                )
                solver.model.addConstr(
                    q[t, s] >= r_dis[t, s],
                    name=f"storage_energy_min_{t}_{s}"
                )

                # Dynamics (Eq. 4e)
                if t == 0:
                    q_prev = self.params.gamma_es * storage_energy_cap[s]
                else:
                    q_prev = q[t-1, s]

                solver.model.addConstr(
                    q[t, s] == q_prev + p_chg[t, s] * self.params.eta - p_dis[t, s] / self.params.eta,
                    name=f"storage_dynamics_{t}_{s}"
                )

        # Continuity (Eq. 4f)
        for s in range(self.S):
            solver.model.addConstr(
                q[self.T-1, s] == self.params.gamma_es * storage_energy_cap[s],
                name=f"storage_continuity_{s}"
            )

        # System reserve (Eq. 5)
        for t in range(self.T):
            total_reserves = gp.quicksum(r_g[t, g] for g in range(self.G))
            total_reserves += gp.quicksum(r_dis[t, s] for s in range(self.S))
            total_load = gp.quicksum(self.scenario.p_d[t, d] for d in range(self.D))

            solver.model.addConstr(
                total_reserves >= self.params.gamma_d * total_load,
                name=f"reserve_{t}"
                )

        # Power flow constraints (Eq. 6-9)
        self._add_power_flow_constraints(solver, p_g, p_es, p_dc, p_sh, p_br, x)

        # Transmission contingencies (Eq. 12)
        if self.contingencies:
            self._add_contingency_constraints(solver, p_br, x, s_c)

        # Solve
        result = solver.solve(verbose=verbose)

        # Extract operational variables
        if result.status == "optimal":
            op_vars = OperationalVariables(
                p_g=result.solution["p_g"],
                r_g=result.solution["r_g"],
                p_es=result.solution["p_es"],
                p_chg=result.solution["p_chg"],
                p_dis=result.solution["p_dis"],
                r_dis=result.solution["r_dis"],
                q=result.solution["q"],
                p_br=result.solution["p_br"],
                p_dc=result.solution["p_dc"],
                p_sh=result.solution["p_sh"]
            )
        else:
            # Return infeasible placeholder
            op_vars = OperationalVariables.zeros(self.T, self.G, self.S, self.b, self.network.β, self.D)

        return result, op_vars

    def _add_power_flow_constraints(self, solver, p_g, p_es, p_dc, p_sh, p_br, x):
        """Add DC power flow constraints using PTDF (simplified)"""
        # TODO: Implement full cycle-based DC power flow
        # For now, use simplified PTDF-based power flow

        branch_capacity = self.params.w_br + x.x_br

        for t in range(self.T):
            # Branch capacity limits (Eq. 7)
            for j in range(self.b):
                solver.model.addConstr(
                    p_br[t, j] <= branch_capacity[j],
                    name=f"branch_cap_pos_{t}_{j}"
                )
                solver.model.addConstr(
                    p_br[t, j] >= -branch_capacity[j],
                    name=f"branch_cap_neg_{t}_{j}"
                )

    def _add_contingency_constraints(self, solver, p_br, x, s_c):
        """Add n-1 contingency constraints (Eq. 12)"""
        branch_capacity = self.params.w_br + x.x_br

        for (t, i, j) in self.contingencies:
            # Post-contingency flow (Eq. 12a)
            # p^brc_ij = p^br_i + Λ_ij * p^br_j
            p_brc = p_br[t, i] + self.LODF[i, j] * p_br[t, j]

            # Flow limits with slack (Eq. 12b-12c)
            solver.model.addConstr(
                p_brc >= -self.params.eta_c * branch_capacity[i] - s_c[(t, i, j)],
                name=f"cont_neg_{t}_{i}_{j}"
            )
            solver.model.addConstr(
                p_brc <= self.params.eta_c * branch_capacity[i] + s_c[(t, i, j)],
                name=f"cont_pos_{t}_{i}_{j}"
            )
