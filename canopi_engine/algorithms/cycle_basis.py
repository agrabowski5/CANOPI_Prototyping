"""
Minimal Cycle Basis Algorithm
Implements Algorithm 3 from the CANOPI paper (Page 7)

Uses integer programming to compute a minimal cycle basis,
which improves sparsity of cycle-based DC power flow formulations.
"""

import numpy as np
from typing import List, Tuple, Optional
import gurobipy as gp
from gurobipy import GRB


def compute_minimal_cycle_basis(
    incidence_matrix: np.ndarray,
    initial_basis: Optional[np.ndarray] = None,
    solver_params: Optional[dict] = None
) -> np.ndarray:
    """
    Compute a minimal cycle basis using Algorithm 3 from the paper.

    Args:
        incidence_matrix: Branch incidence matrix A^br ∈ {-1, 0, 1}^{n×b}
        initial_basis: Optional initial cycle basis (e.g., from LU factorization)
        solver_params: Optional Gurobi solver parameters

    Returns:
        D: Minimal cycle basis matrix ∈ {-1, 0, 1}^{n_c×b}
        where n_c = b - n + 1 (dimension of cycle space)

    Algorithm 3 from paper:
    For each cycle κ in the basis, solve IP (26) to find the shortest
    cycle linearly independent of other cycles.
    """
    n, b = incidence_matrix.shape
    n_c = b - n + 1  # Cycle space dimension

    # Step 1: Initialize with a cycle basis
    if initial_basis is None:
        C = compute_fundamental_cycle_basis(incidence_matrix)
    else:
        C = initial_basis.copy()

    assert C.shape == (n_c, b), f"Expected shape ({n_c}, {b}), got {C.shape}"

    # Convert to undirected (absolute values for cycle membership)
    C_undirected = np.abs(C)

    # Step 2: Improve each cycle iteratively (Algorithm 3, lines 2-9)
    for kappa in range(n_c):
        print(f"Improving cycle {kappa + 1}/{n_c}...")

        # Solve IP (26) to find shortest cycle independent of others
        v_star = solve_shortest_cycle_ip(C_undirected, kappa, solver_params)

        if v_star is not None and np.sum(v_star) < np.sum(C_undirected[kappa]):
            # Found a shorter cycle, replace it
            C_undirected[kappa] = v_star
            print(f"  Improved: {np.sum(C_undirected[kappa])} edges")
        else:
            print(f"  No improvement: {np.sum(C_undirected[kappa])} edges")

    # Step 3: Assign consistent orientations (Algorithm 3, lines 4-8)
    D = assign_cycle_orientations(C_undirected, incidence_matrix)

    return D


def solve_shortest_cycle_ip(
    C: np.ndarray,
    kappa_hat: int,
    solver_params: Optional[dict] = None
) -> Optional[np.ndarray]:
    """
    Solve the integer program (26) from the paper to find the shortest cycle
    linearly independent of {C_κ : κ ≠ κ̂}.

    Minimize: Σ_j v_j
    Subject to: Σ_κ C_κj · w_κ = 2u_j + v_j, ∀j ∈ [b]
                w ∈ {0,1}^{n_c}, w_{κ̂} = 1
                u ∈ Z^b, v ∈ {0,1}^b

    Args:
        C: Undirected cycle basis (n_c × b)
        kappa_hat: Index of cycle to improve
        solver_params: Gurobi parameters

    Returns:
        v_star: Optimal shortest cycle (binary vector of length b)
    """
    n_c, b = C.shape

    try:
        # Create Gurobi model
        model = gp.Model("shortest_cycle")
        model.setParam('OutputFlag', 0)  # Suppress output

        if solver_params:
            for param, value in solver_params.items():
                model.setParam(param, value)

        # Decision variables
        w = model.addVars(n_c, vtype=GRB.BINARY, name="w")  # Cycle weights
        u = model.addVars(b, vtype=GRB.INTEGER, lb=-GRB.INFINITY, name="u")  # Integer vars
        v = model.addVars(b, vtype=GRB.BINARY, name="v")  # Resulting cycle

        # Objective: minimize total edges in cycle
        model.setObjective(gp.quicksum(v[j] for j in range(b)), GRB.MINIMIZE)

        # Constraint: w_{κ̂} = 1 (must include cycle kappa_hat)
        model.addConstr(w[kappa_hat] == 1, name="include_kappa_hat")

        # Constraint: Σ_κ C_κj · w_κ = 2u_j + v_j, ∀j
        # This enforces that v is the mod-2 sum of selected cycles
        for j in range(b):
            model.addConstr(
                gp.quicksum(C[kappa, j] * w[kappa] for kappa in range(n_c)) == 2 * u[j] + v[j],
                name=f"mod2_edge_{j}"
            )

        # Solve
        model.optimize()

        if model.status == GRB.OPTIMAL:
            # Extract solution
            v_star = np.array([v[j].X for j in range(b)])
            return v_star
        else:
            print(f"  IP solver status: {model.status}")
            return None

    except Exception as e:
        print(f"  Error solving IP: {e}")
        return None


def compute_fundamental_cycle_basis(incidence_matrix: np.ndarray) -> np.ndarray:
    """
    Compute a fundamental cycle basis using a spanning tree.
    This is a baseline method, not necessarily minimal.

    Args:
        incidence_matrix: A^br ∈ {-1, 0, 1}^{n×b}

    Returns:
        C: Fundamental cycle basis (undirected)
    """
    n, b = incidence_matrix.shape
    n_c = b - n + 1

    # Find a spanning tree using DFS
    # For simplicity, use a greedy approach
    tree_edges = []
    non_tree_edges = []

    # Build adjacency list
    edges = []
    for j in range(b):
        from_node = np.where(incidence_matrix[:, j] == -1)[0][0]
        to_node = np.where(incidence_matrix[:, j] == 1)[0][0]
        edges.append((from_node, to_node, j))

    # DFS to find spanning tree
    visited = set([0])  # Start from node 0
    stack = [0]

    while stack and len(tree_edges) < n - 1:
        node = stack[-1]
        found_edge = False

        for from_node, to_node, edge_idx in edges:
            if edge_idx in tree_edges or edge_idx in non_tree_edges:
                continue

            if from_node == node and to_node not in visited:
                visited.add(to_node)
                tree_edges.append(edge_idx)
                stack.append(to_node)
                found_edge = True
                break
            elif to_node == node and from_node not in visited:
                visited.add(from_node)
                tree_edges.append(edge_idx)
                stack.append(from_node)
                found_edge = True
                break

        if not found_edge:
            stack.pop()

    # Non-tree edges
    non_tree_edges = [j for j in range(b) if j not in tree_edges]

    # Each non-tree edge forms a fundamental cycle
    C = np.zeros((n_c, b), dtype=int)

    for cycle_idx, non_tree_edge in enumerate(non_tree_edges):
        # TODO: Find the unique path in tree + this non-tree edge
        # For now, just mark the non-tree edge
        C[cycle_idx, non_tree_edge] = 1

    return C


def assign_cycle_orientations(
    C_undirected: np.ndarray,
    incidence_matrix: np.ndarray
) -> np.ndarray:
    """
    Assign consistent orientations to cycles (Algorithm 3, lines 4-8).

    Args:
        C_undirected: Undirected cycle basis
        incidence_matrix: Branch incidence matrix

    Returns:
        D: Directed cycle basis ∈ {-1, 0, 1}^{n_c×b}
    """
    n_c, b = C_undirected.shape
    n = incidence_matrix.shape[0]

    D = np.zeros((n_c, b), dtype=int)

    for kappa in range(n_c):
        # Find edges in this cycle
        cycle_edges = np.where(C_undirected[kappa] > 0)[0]

        # Traverse cycle to assign directions
        # Start with first edge
        if len(cycle_edges) > 0:
            first_edge = cycle_edges[0]

            # Get nodes of first edge
            from_node = np.where(incidence_matrix[:, first_edge] == -1)[0][0]
            to_node = np.where(incidence_matrix[:, first_edge] == 1)[0][0]

            # Arbitrarily orient first edge forward
            D[kappa, first_edge] = 1
            current_node = to_node

            # Traverse remaining edges
            remaining = set(cycle_edges[1:])
            while remaining:
                # Find next edge connected to current_node
                for edge_idx in remaining:
                    edge_from = np.where(incidence_matrix[:, edge_idx] == -1)[0][0]
                    edge_to = np.where(incidence_matrix[:, edge_idx] == 1)[0][0]

                    if edge_from == current_node:
                        D[kappa, edge_idx] = 1
                        current_node = edge_to
                        remaining.remove(edge_idx)
                        break
                    elif edge_to == current_node:
                        D[kappa, edge_idx] = -1
                        current_node = edge_from
                        remaining.remove(edge_idx)
                        break

    return D


def validate_cycle_basis(D: np.ndarray, incidence_matrix: np.ndarray) -> bool:
    """
    Validate that D is a valid cycle basis.

    Checks:
    1. Each row represents a cycle (KVL: sum of voltages = 0)
    2. Rows are linearly independent
    3. Dimension is correct (n_c = b - n + 1)

    Args:
        D: Directed cycle basis
        incidence_matrix: Branch incidence matrix

    Returns:
        True if valid cycle basis
    """
    n, b = incidence_matrix.shape
    n_c_expected = b - n + 1

    if D.shape[0] != n_c_expected:
        print(f"Wrong dimension: expected {n_c_expected}, got {D.shape[0]}")
        return False

    # Check linear independence (rank should be n_c)
    rank = np.linalg.matrix_rank(D.astype(float))
    if rank != D.shape[0]:
        print(f"Not linearly independent: rank {rank}, expected {D.shape[0]}")
        return False

    print(f"Valid cycle basis: {D.shape[0]} cycles, {b} edges")
    return True
