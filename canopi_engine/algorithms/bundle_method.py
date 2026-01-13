"""
Bundle Method with Interleaved Contingency Generation
Implements Algorithm 1 from the CANOPI paper (Page 5)

This is the main optimization algorithm that solves the BUND problem
using a level-bundle method with analytic center stabilization.
"""

import numpy as np
from typing import Dict, List, Tuple, Set, Optional, Callable
from dataclasses import dataclass
import time

from ..models.network import Network
from ..models.capacity_decision import CapacityDecision, CapacityLimits, InvestmentCosts
from .operational_subproblem import OperationalSubproblem, ScenarioData, OperationalParameters
from ..solvers.gurobi_interface import GurobiSolver
import gurobipy as gp
from gurobipy import GRB


@dataclass
class BundleIteration:
    """Results from one bundle method iteration"""
    k: int
    x_k: CapacityDecision
    f_k: float  # Upper bound
    L_k: float  # Lower bound
    gap: float
    theta_lev_k: float
    time_elapsed: float


class BundleMethod:
    """
    Bundle method with interleaved contingency generation (Algorithm 1)

    Solves:  min_{x ∈ X} c^T x + Σ_ω h_r(x̂^br, x, ξ_ω, J^full)

    where h_r is the operational subproblem cost with contingencies.
    """

    def __init__(
        self,
        network: Network,
        investment_costs: InvestmentCosts,
        capacity_limits: CapacityLimits,
        scenarios: List[ScenarioData],
        operational_params: OperationalParameters,
        alpha: float = 0.3,
        epsilon: float = 0.01,
        max_iterations: int = 200
    ):
        """
        Initialize bundle method

        Args:
            network: Transmission network
            investment_costs: c in c^T x
            capacity_limits: Upper bounds x̄
            scenarios: List of operational scenarios ξ_ω
            operational_params: Operational parameters
            alpha: Level parameter (0 < α < 1)
            epsilon: Convergence tolerance
            max_iterations: Maximum iterations
        """
        self.network = network
        self.costs = investment_costs
        self.limits = capacity_limits
        self.scenarios = scenarios
        self.op_params = operational_params
        self.alpha = alpha
        self.epsilon = epsilon
        self.max_iterations = max_iterations

        # Bundle state
        self.cutting_planes: Dict[int, List[Tuple[float, np.ndarray]]] = {
            omega: [] for omega in range(len(scenarios))
        }
        self.contingencies: Dict[int, Set[Tuple[int, int, int]]] = {
            omega: set() for omega in range(len(scenarios))
        }

        # History
        self.iterations: List[BundleIteration] = []
        self.start_time = None

    def solve(
        self,
        x_br_hat: np.ndarray,  # Impedance-defining capacity
        progress_callback: Optional[Callable] = None,
        verbose: bool = True
    ) -> Tuple[CapacityDecision, float]:
        """
        Run bundle method optimization

        Args:
            x_br_hat: Impedance-defining transmission capacity
            progress_callback: Optional callback(iteration, results)
            verbose: Print progress

        Returns:
            (x_star, f_star): Optimal capacity decision and objective value
        """
        self.start_time = time.time()

        # Initialize bounds
        L_k = 0.0
        U_k = np.inf

        # Initialize with zero capacity
        x_k = CapacityDecision.zeros(
            n_generators=self.op_params.w_g.shape[0],
            n_storage=self.op_params.w_es_p.shape[0],
            n_branches=self.network.b,
            n_scenarios=len(self.scenarios)
        )

        x_star = None
        y_star = None

        if verbose:
            print("=" * 80)
            print("CANOPI Bundle Method with Interleaved Contingency Generation")
            print("=" * 80)

        for k in range(1, self.max_iterations + 1):
            if verbose:
                print(f"\n--- Iteration {k} ---")

            # Solve operational subproblems in parallel (Lines 4-8)
            theta_k, g_k, sigma_k = self._solve_subproblems(x_k, x_br_hat, verbose)

            # Update cutting planes (Line 6)
            for omega in range(len(self.scenarios)):
                self.cutting_planes[omega].append((theta_k[omega], g_k[omega]))

            # Compute bounds (Lines 9-11)
            f_k = self.costs.calculate_cost(x_k) + sum(theta_k[omega] + sigma_k[omega]
                                                        for omega in range(len(self.scenarios)))
            U_k = min(U_k, f_k)

            if U_k == f_k:
                x_star = x_k
                # y_star would be the operational variables

            # Solve master problem for lower bound
            L_k = self._solve_master_problem(x_k)

            # Check convergence (Line 13)
            gap = (U_k - L_k) / U_k if U_k > 0 else 0.0

            elapsed = time.time() - self.start_time

            iter_result = BundleIteration(
                k=k,
                x_k=x_k,
                f_k=f_k,
                L_k=L_k,
                gap=gap,
                theta_lev_k=0.0,  # Will be set below
                time_elapsed=elapsed
            )
            self.iterations.append(iter_result)

            if verbose:
                print(f"Upper bound: ${U_k/1e9:.3f}B")
                print(f"Lower bound: ${L_k/1e9:.3f}B")
                print(f"Gap: {gap*100:.2f}%")
                print(f"Time: {elapsed:.1f}s")

            if progress_callback:
                progress_callback(k, iter_result)

            if gap < self.epsilon:
                if verbose:
                    print(f"\n✓ Converged! Gap = {gap*100:.2f}% < {self.epsilon*100}%")
                break

            # Compute level (Line 14)
            theta_lev_k = L_k + self.alpha * (U_k - L_k)
            iter_result.theta_lev_k = theta_lev_k

            # Compute next iterate as analytic center (Line 15)
            x_k = self._compute_analytic_center(theta_lev_k, verbose)

        if verbose:
            print("\n" + "=" * 80)
            print(f"Bundle Method Complete: {len(self.iterations)} iterations")
            print(f"Final objective: ${U_k/1e9:.3f}B")
            print(f"Total time: {time.time() - self.start_time:.1f}s")
            print("=" * 80)

        return x_star, U_k

    def _solve_subproblems(
        self,
        x_k: CapacityDecision,
        x_br_hat: np.ndarray,
        verbose: bool
    ) -> Tuple[List[float], List[np.ndarray], List[float]]:
        """
        Solve operational subproblems for all scenarios (Algorithm 1, lines 4-8)

        Returns:
            theta_k: Objectives for each scenario
            g_k: Subgradients for each scenario
            sigma_k: Contingency penalties for each scenario
        """
        n_scenarios = len(self.scenarios)
        theta_k = []
        g_k = []
        sigma_k = []

        for omega in range(n_scenarios):
            # Create operational subproblem
            subproblem = OperationalSubproblem(
                network=self.network,
                params=self.op_params,
                scenario=self.scenarios[omega],
                x_br_hat=x_br_hat,
                contingencies=self.contingencies[omega]
            )

            # Solve
            result, op_vars = subproblem.solve(
                x=x_k,
                x_em_omega=x_k.x_em[omega],
                verbose=False
            )

            if result.status == "optimal":
                theta_k.append(result.objective_value)

                # Compute subgradient (simplified - should use dual values)
                # TODO: Extract actual subgradient from LP duals
                g = np.concatenate([
                    np.zeros_like(x_k.x_g),
                    np.zeros_like(x_k.x_es_p),
                    np.zeros_like(x_k.x_es_e),
                    np.zeros_like(x_k.x_br),
                    np.zeros_like(x_k.x_em)
                ])
                g_k.append(g)

                # Check for violated contingencies
                new_violations = self._identify_violated_contingencies(op_vars, x_k, omega)
                self.contingencies[omega].update(new_violations)

                sigma_k.append(len(new_violations) * self.scenarios[omega].c_vio * 10.0)  # Penalty estimate

                if verbose and len(new_violations) > 0:
                    print(f"  Scenario {omega}: {len(new_violations)} new contingency violations")
            else:
                print(f"Warning: Subproblem {omega} infeasible")
                theta_k.append(1e12)
                g_k.append(np.zeros(len(x_k.x_g) + len(x_k.x_es_p) + len(x_k.x_es_e) + len(x_k.x_br) + len(x_k.x_em)))
                sigma_k.append(0.0)

        return theta_k, g_k, sigma_k

    def _identify_violated_contingencies(
        self,
        op_vars,
        x_k: CapacityDecision,
        omega: int
    ) -> Set[Tuple[int, int, int]]:
        """
        Identify violated contingency constraints (Oracle, Eq. 20c-20e)

        Returns:
            Set of (t, i, j) contingency indices
        """
        violations = set()

        # TODO: Implement full contingency screening
        # For now, return empty set
        return violations

    def _solve_master_problem(self, x_current: CapacityDecision) -> float:
        """
        Solve master LP to get lower bound (Line 11)

        min_{x ∈ X} c^T x + Σ_ω max_{(θ, g) ∈ cuts_ω} {θ + g^T(x - x_k)}
        """
        # Simplified implementation
        # TODO: Build full LP with cutting planes
        return 0.0

    def _compute_analytic_center(self, theta_lev: float, verbose: bool) -> CapacityDecision:
        """
        Compute analytic center of level set (Line 15)

        ac({x ∈ X : f̂_k(x) ≤ θ^lev_k})
        """
        # Simplified: return current iterate with small random perturbation
        # TODO: Implement full analytic center calculation

        x_new = CapacityDecision.zeros(
            n_generators=self.op_params.w_g.shape[0],
            n_storage=self.op_params.w_es_p.shape[0],
            n_branches=self.network.b,
            n_scenarios=len(self.scenarios)
        )

        return x_new
