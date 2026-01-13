"""
Transmission Correction Algorithm
Implements Algorithm 2 (Function E for RTEP) from the CANOPI paper (Page 6)

This algorithm resolves the impedance feedback effect by finding a fixed point
where x^br = x̂^br (capacity decision equals impedance-defining capacity).
"""

import numpy as np
from typing import Tuple, Optional, Dict

from ..models.network import Network
from ..models.capacity_decision import CapacityDecision


def transmission_correction_rtep(
    network: Network,
    x_non_br: Dict[str, np.ndarray],  # Fixed non-transmission decisions
    p_ni_star: Dict[int, np.ndarray],  # Nodal net injections from BUND
    x_br_hat: np.ndarray,  # Current impedance-defining capacity
    eta_c: float = 1.0,  # Post-contingency rating multiplier
    c_br: Optional[np.ndarray] = None,  # Transmission costs
    c_vio: float = 2000.0,  # Violation penalty
    verbose: bool = True
) -> np.ndarray:
    """
    Solve Restricted Transmission Expansion Problem (RTEP)

    Given fixed non-transmission decisions, re-optimize transmission capacity
    to minimize capacity costs + contingency violations.

    This is Algorithm 2 from the paper, which can be solved analytically
    without LP solver (Proposition 3).

    Args:
        network: Transmission network
        x_non_br: Fixed non-transmission capacity decisions
        p_ni_star: Nodal net power injections for each scenario
        x_br_hat: Current impedance-defining capacity
        eta_c: Post-contingency rating multiplier
        c_br: Transmission capacity costs ($/MW)
        c_vio: Contingency violation penalty ($/MWh)
        verbose: Print progress

    Returns:
        x_br_tilde: Updated transmission capacity
    """
    b = network.b
    n_scenarios = len(p_ni_star)

    if c_br is None:
        c_br = np.ones(b) * 1e6  # Default $1M/MW for transmission

    # Precompute PTDF and LODF with current x̂^br
    PTDF, LODF = compute_power_transfer_matrices(network, x_br_hat)

    x_br_tilde = np.zeros(b)

    # Solve separately for each branch (problem is separable, Eq. 24)
    for i in range(b):
        if verbose and i % 100 == 0:
            print(f"  Processing branch {i}/{b}...")

        # Line 2-7: Compute power flows for all scenarios and times
        delta_base = []  # Base-case violations
        delta_cont = []  # Contingency violations

        for omega in range(n_scenarios):
            p_ni = p_ni_star[omega]  # Shape: (T, n)
            T = p_ni.shape[0]

            for t in range(T):
                # Line 3: Base-case power flow
                # p̂^br_ωti = Φ_i(x̂^br) p^ni*_ωt,[2:n]
                p_br_i = PTDF[i, :] @ p_ni[t, 1:]  # Remove slack bus

                # Line 5: Base-case violation
                delta_base_ti = max(abs(p_br_i) - network.branches[i].capacity_mw, 0.0)
                delta_base.append(delta_base_ti)

                # Line 4-6: Post-contingency flows
                for j in range(b):
                    if i != j and j in network.identify_non_islanding_branches():
                        # Post-contingency flow (Eq. 12a)
                        p_br_j = PTDF[j, :] @ p_ni[t, 1:]
                        p_brc_ij = p_br_i + LODF[i, j] * p_br_j

                        # Contingency violation
                        delta_cont_tij = max(abs(p_brc_ij) - eta_c * network.branches[i].capacity_mw, 0.0)
                        delta_cont.append(delta_cont_tij / eta_c)

        # Line 8: Lower bound from base-case feasibility
        x_br_lb_i = max(delta_base) if delta_base else 0.0

        # Line 9-10: Unconstrained optimum
        # The objective is piecewise linear in x^br_i
        # Find breakpoints and optimal x^br_i

        r_i = c_br[i] / (eta_c * c_vio)  # Ratio of costs

        if len(delta_cont) > 0:
            # Line 10: x^opt_i = r_i-th largest value in {δ^c_ωtij / η^c}
            delta_cont_sorted = sorted(delta_cont, reverse=True)
            r_i_int = int(np.ceil(r_i))
            if r_i_int < len(delta_cont_sorted):
                x_opt_i = delta_cont_sorted[r_i_int]
            else:
                x_opt_i = 0.0
        else:
            x_opt_i = 0.0

        # Line 11: Project to feasible interval [x^br-lb_i, x̄^br_i]
        x_br_max_i = network.branches[i].capacity_mw * 2.0  # Assume can double capacity
        x_br_tilde[i] = np.clip(max(x_br_lb_i, x_opt_i), 0.0, x_br_max_i)

    if verbose:
        total_added = np.sum(x_br_tilde) / 1000.0  # GW
        print(f"  Total transmission added: {total_added:.2f} GW")

    return x_br_tilde


def compute_power_transfer_matrices(
    network: Network,
    x_br: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute PTDF and LODF matrices (Equations 13a-13b)

    Args:
        network: Transmission network
        x_br: Transmission capacity additions

    Returns:
        (PTDF, LODF): Power transfer matrices
    """
    # Get susceptances with impedance feedback
    susceptances = network.get_susceptances(x_br)
    B = np.diag(susceptances)

    # Remove slack bus
    A = network.A_br[1:, :]  # Remove first row (slack bus)
    n_minus_1, b = A.shape

    try:
        # PTDF matrix (Equation 13a)
        # Φ(x^br) = B(x^br) A [A^T B(x^br) A]^{-1}
        ATBA = A.T @ B @ A
        ATBA_inv = np.linalg.inv(ATBA)
        PTDF = B @ A @ ATBA_inv

        # LODF matrix (Equation 13b)
        # Λ_ij = Φ_i·(A^T)_j / (1 - Φ_j·(A^T)_j)
        LODF = np.zeros((b, b))
        for i in range(b):
            for j in range(b):
                if i != j:
                    numerator = PTDF[i, :] @ A[:, j]
                    denominator = 1.0 - (PTDF[j, :] @ A[:, j])
                    if abs(denominator) > 1e-6:
                        LODF[i, j] = numerator / denominator

    except np.linalg.LinAlgError:
        print("Warning: Singular matrix in PTDF/LODF calculation")
        PTDF = np.zeros((b, n_minus_1))
        LODF = np.zeros((b, b))

    return PTDF, LODF


def iterative_transmission_correction(
    network: Network,
    x_star_non_br: Dict[str, np.ndarray],
    p_ni_star: Dict[int, np.ndarray],
    x_br_initial: np.ndarray,
    max_iterations: int = 10,
    tolerance: float = 1e-3,
    verbose: bool = True
) -> Tuple[np.ndarray, bool]:
    """
    Iterative fixed-point algorithm (CORR procedure from Fig. 1 in paper)

    Iterate: x̂^br_{k+1} = E(x̂^br_k) until convergence

    Args:
        network: Transmission network
        x_star_non_br: Fixed non-transmission decisions from BUND
        p_ni_star: Nodal net injections
        x_br_initial: Initial transmission capacity (e.g., from BUND)
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
        verbose: Print progress

    Returns:
        (x_br_final, converged): Final transmission capacity and convergence flag
    """
    x_br_hat = x_br_initial.copy()

    if verbose:
        print("\n" + "="*60)
        print("Transmission Correction (CORR)")
        print("="*60)

    for iteration in range(max_iterations):
        if verbose:
            print(f"\nIteration {iteration + 1}/{max_iterations}")

        # Solve RTEP with current x̂^br
        x_br_tilde = transmission_correction_rtep(
            network=network,
            x_non_br=x_star_non_br,
            p_ni_star=p_ni_star,
            x_br_hat=x_br_hat,
            verbose=verbose
        )

        # Check convergence
        diff = np.linalg.norm(x_br_tilde - x_br_hat) / (1.0 + np.linalg.norm(x_br_hat))

        if verbose:
            print(f"  Change in x^br: {diff:.6f}")

        if diff < tolerance:
            if verbose:
                print(f"\n✓ Converged! ||Δx^br|| = {diff:.6f} < {tolerance}")
            return x_br_tilde, True

        # Update for next iteration
        x_br_hat = x_br_tilde

    if verbose:
        print(f"\n⚠ Did not converge after {max_iterations} iterations")

    return x_br_hat, False
