"""
Gurobi LP/MIP Solver Interface
Provides a clean interface to Gurobi for solving optimization problems
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class SolverResult:
    """Results from solving an optimization problem"""
    status: str
    objective_value: Optional[float]
    solution: Optional[Dict[str, np.ndarray]]
    solve_time: float
    iterations: Optional[int] = None
    gap: Optional[float] = None


class GurobiSolver:
    """
    Wrapper for Gurobi optimizer with convenient methods for
    building and solving linear programs
    """

    def __init__(self, name: str = "optimization", **params):
        """
        Initialize Gurobi model

        Args:
            name: Model name
            **params: Gurobi parameters (e.g., TimeLimit=600, MIPGap=0.01)
        """
        self.model = gp.Model(name)
        self.vars = {}
        self.constrs = {}

        # Set parameters
        for param, value in params.items():
            self.model.setParam(param, value)

    def add_continuous_vars(
        self,
        name: str,
        shape: Tuple[int, ...],
        lb: float = 0.0,
        ub: float = GRB.INFINITY
    ) -> np.ndarray:
        """
        Add continuous decision variables

        Args:
            name: Variable name
            shape: Shape of variable array
            lb: Lower bound
            ub: Upper bound

        Returns:
            Array of Gurobi variables
        """
        if len(shape) == 1:
            vars_list = self.model.addVars(
                shape[0],
                lb=lb,
                ub=ub,
                vtype=GRB.CONTINUOUS,
                name=name
            )
            var_array = np.array([vars_list[i] for i in range(shape[0])])
        elif len(shape) == 2:
            vars_list = self.model.addVars(
                shape[0], shape[1],
                lb=lb,
                ub=ub,
                vtype=GRB.CONTINUOUS,
                name=name
            )
            var_array = np.array([[vars_list[i, j] for j in range(shape[1])]
                                  for i in range(shape[0])])
        else:
            raise ValueError("Only 1D and 2D arrays supported")

        self.vars[name] = var_array
        return var_array

    def add_binary_vars(self, name: str, shape: Tuple[int, ...]) -> np.ndarray:
        """Add binary decision variables"""
        if len(shape) == 1:
            vars_list = self.model.addVars(
                shape[0],
                vtype=GRB.BINARY,
                name=name
            )
            var_array = np.array([vars_list[i] for i in range(shape[0])])
        else:
            raise ValueError("Only 1D binary arrays supported for now")

        self.vars[name] = var_array
        return var_array

    def set_objective(self, expr, sense=GRB.MINIMIZE):
        """
        Set objective function

        Args:
            expr: Gurobi linear expression
            sense: GRB.MINIMIZE or GRB.MAXIMIZE
        """
        self.model.setObjective(expr, sense)

    def add_constraint(self, name: str, constraint):
        """
        Add a named constraint

        Args:
            name: Constraint name
            constraint: Gurobi constraint
        """
        self.constrs[name] = constraint

    def add_constraints(self, name_prefix: str, constraints: List):
        """Add multiple constraints with indexed names"""
        for i, constr in enumerate(constraints):
            self.constrs[f"{name_prefix}_{i}"] = constr

    def solve(self, verbose: bool = False) -> SolverResult:
        """
        Solve the optimization problem

        Args:
            verbose: Whether to print solver output

        Returns:
            SolverResult with solution and status
        """
        if not verbose:
            self.model.setParam('OutputFlag', 0)

        self.model.optimize()

        # Extract results
        status_map = {
            GRB.OPTIMAL: "optimal",
            GRB.INFEASIBLE: "infeasible",
            GRB.UNBOUNDED: "unbounded",
            GRB.INF_OR_UNBD: "inf_or_unbd",
            GRB.TIME_LIMIT: "time_limit",
            GRB.ITERATION_LIMIT: "iteration_limit"
        }

        status = status_map.get(self.model.status, "unknown")

        if status == "optimal":
            obj_value = self.model.ObjVal
            solution = self._extract_solution()
            gap = self.model.MIPGap if self.model.IsMIP else 0.0
        else:
            obj_value = None
            solution = None
            gap = None

        return SolverResult(
            status=status,
            objective_value=obj_value,
            solution=solution,
            solve_time=self.model.Runtime,
            iterations=self.model.IterCount,
            gap=gap
        )

    def _extract_solution(self) -> Dict[str, np.ndarray]:
        """Extract solution values for all variables"""
        solution = {}

        for name, var_array in self.vars.items():
            if var_array.ndim == 1:
                solution[name] = np.array([v.X for v in var_array])
            elif var_array.ndim == 2:
                solution[name] = np.array([[v.X for v in row] for row in var_array])

        return solution

    def get_dual_values(self, constraint_names: List[str]) -> Dict[str, float]:
        """
        Get dual values (shadow prices) for constraints

        Args:
            constraint_names: List of constraint names

        Returns:
            Dictionary mapping constraint names to dual values
        """
        duals = {}
        for name in constraint_names:
            if name in self.constrs:
                duals[name] = self.constrs[name].Pi
        return duals

    def warm_start(self, solution: Dict[str, np.ndarray]):
        """
        Warm-start the solver with an initial solution

        Args:
            solution: Dictionary mapping variable names to values
        """
        for name, values in solution.items():
            if name in self.vars:
                var_array = self.vars[name]
                if var_array.ndim == 1:
                    for i, val in enumerate(values):
                        var_array[i].Start = val
                elif var_array.ndim == 2:
                    for i in range(var_array.shape[0]):
                        for j in range(var_array.shape[1]):
                            var_array[i, j].Start = values[i, j]

    def __del__(self):
        """Clean up Gurobi model"""
        try:
            self.model.dispose()
        except:
            pass


def solve_lp(
    c: np.ndarray,
    A_ub: Optional[np.ndarray] = None,
    b_ub: Optional[np.ndarray] = None,
    A_eq: Optional[np.ndarray] = None,
    b_eq: Optional[np.ndarray] = None,
    bounds: Optional[Tuple[float, float]] = None,
    **solver_params
) -> SolverResult:
    """
    Solve a linear program:
        minimize c^T x
        subject to A_ub x <= b_ub
                   A_eq x = b_eq
                   lb <= x <= ub

    Args:
        c: Objective coefficients
        A_ub: Inequality constraint matrix
        b_ub: Inequality constraint RHS
        A_eq: Equality constraint matrix
        b_eq: Equality constraint RHS
        bounds: (lower, upper) bounds on variables
        **solver_params: Gurobi parameters

    Returns:
        SolverResult
    """
    n = len(c)
    lb, ub = bounds if bounds else (0.0, GRB.INFINITY)

    solver = GurobiSolver("lp", **solver_params)

    # Decision variables
    x = solver.add_continuous_vars("x", shape=(n,), lb=lb, ub=ub)

    # Objective
    obj = gp.quicksum(c[i] * x[i] for i in range(n))
    solver.set_objective(obj, GRB.MINIMIZE)

    # Inequality constraints
    if A_ub is not None and b_ub is not None:
        for i in range(A_ub.shape[0]):
            constr = gp.quicksum(A_ub[i, j] * x[j] for j in range(n)) <= b_ub[i]
            solver.add_constraint(f"ineq_{i}", constr)

    # Equality constraints
    if A_eq is not None and b_eq is not None:
        for i in range(A_eq.shape[0]):
            constr = gp.quicksum(A_eq[i, j] * x[j] for j in range(n)) == b_eq[i]
            solver.add_constraint(f"eq_{i}", constr)

    return solver.solve()
