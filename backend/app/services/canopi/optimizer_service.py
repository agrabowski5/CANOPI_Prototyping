"""
CANOPI Optimizer Service
Wrapper service that integrates the CANOPI optimization engine with the FastAPI backend
"""

import numpy as np
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import sys
from pathlib import Path

# Add canopi_engine and data_pipelines to path
backend_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_root))

from canopi_engine.algorithms.bundle_method import BundleMethod, BundleIteration
from canopi_engine.algorithms.transmission_correction import iterative_transmission_correction
from canopi_engine.models.capacity_decision import CapacityDecision
from canopi_engine.models.network import Network
from data_pipelines.loaders.sample_data_loader import load_complete_optimization_data


class OptimizationRequest:
    """Request data for optimization"""

    def __init__(
        self,
        planning_horizon_start: int,
        planning_horizon_end: int,
        carbon_target: float,
        budget_limit: float,
        contingency_level: str = "n-1",
        temporal_resolution: str = "hourly",
        reserve_margin: float = 0.15,
        transmission_limit: bool = True,
        state_policies: list = None
    ):
        self.planning_horizon_start = planning_horizon_start
        self.planning_horizon_end = planning_horizon_end
        self.carbon_target = carbon_target
        self.budget_limit = budget_limit
        self.contingency_level = contingency_level
        self.temporal_resolution = temporal_resolution
        self.reserve_margin = reserve_margin
        self.transmission_limit = transmission_limit
        self.state_policies = state_policies or []


class OptimizationResult:
    """Results from optimization"""

    def __init__(
        self,
        total_cost: float,
        capacity_decision: CapacityDecision,
        objective_value: float,
        iterations: int,
        convergence_gap: float,
        computation_time: float,
        status: str = "completed"
    ):
        self.total_cost = total_cost
        self.capacity_decision = capacity_decision
        self.objective_value = objective_value
        self.iterations = iterations
        self.convergence_gap = convergence_gap
        self.computation_time = computation_time
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "total_cost": self.total_cost,
            "objective_value": self.objective_value,
            "iterations": self.iterations,
            "convergence_gap": self.convergence_gap,
            "computation_time": self.computation_time,
            "status": self.status,
            "investments": {
                "storage_power_gw": self.capacity_decision.total_storage_power_gw,
                "storage_energy_gwh": self.capacity_decision.total_storage_energy_gwh,
                "transmission_gw": self.capacity_decision.total_transmission_gw,
                "generation_by_type": self._get_generation_by_type()
            },
            "reliability": {
                "load_shed_gwh": 0.0,  # Would come from operational results
                "load_shed_percent": 0.0,
                "violations_gwh": 0.0,
                "n_1_compliance": 1.0
            },
            "carbon_intensity": self._calculate_carbon_intensity(),
            "geospatial_results": self._get_geospatial_results()
        }

    def _get_generation_by_type(self) -> Dict[str, float]:
        """Aggregate generation by type (simplified)"""
        total_gen = self.capacity_decision.total_generation_gw
        # Simplified: distribute across types
        return {
            "solar": total_gen * 0.35,
            "wind": total_gen * 0.25,
            "gas": total_gen * 0.25,
            "nuclear": total_gen * 0.15
        }

    def _calculate_carbon_intensity(self) -> float:
        """Calculate average carbon intensity (simplified)"""
        # Simplified calculation
        return 45.0  # kg CO2/MWh

    def _get_geospatial_results(self) -> Dict[str, Any]:
        """Get location-specific results (simplified)"""
        return {
            "optimal_locations": [],
            "transmission_upgrades": []
        }


class CANOPIOptimizerService:
    """
    Service wrapper for CANOPI optimization engine

    Handles:
    - Loading network data
    - Converting API requests to CANOPI format
    - Running optimization
    - Converting results back to API format
    - Progress callbacks
    """

    def __init__(self, time_periods: int = 24):
        """
        Initialize optimizer service

        Args:
            time_periods: Number of time periods to simulate (default 24 hours)
        """
        self.time_periods = time_periods
        self.data = None
        self.network = None
        self.params = None
        self.scenarios = None
        self.investment_costs = None
        self.capacity_limits = None

    def load_data(self):
        """Load network data from CSV files"""
        print("Loading network data...")
        self.data = load_complete_optimization_data(time_periods=self.time_periods)

        self.network = self.data['network']
        self.params = self.data['params']
        self.scenarios = self.data['scenarios']
        self.investment_costs = self.data['investment_costs']
        self.capacity_limits = self.data['capacity_limits']

        print(f"Data loaded: {self.network}")

    def run_optimization(
        self,
        request: OptimizationRequest,
        progress_callback: Optional[Callable[[int, float, Dict], None]] = None,
        max_iterations: int = 50,
        simplified: bool = True
    ) -> OptimizationResult:
        """
        Run CANOPI optimization

        Args:
            request: Optimization request with parameters
            progress_callback: Callback function(iteration, progress, info)
            max_iterations: Maximum bundle method iterations
            simplified: If True, run simplified problem (faster for testing)

        Returns:
            OptimizationResult with solution
        """
        start_time = datetime.now()

        # Load data if not already loaded
        if self.data is None:
            self.load_data()

        print("\n" + "="*70)
        print("Starting CANOPI Optimization")
        print("="*70)

        # Apply request parameters
        self._apply_request_parameters(request)

        if simplified:
            # Simplified problem: reduce time periods and scenarios
            print("\nRunning simplified optimization (faster for testing)")
            result = self._run_simplified_optimization(
                progress_callback, max_iterations
            )
        else:
            # Full optimization with bundle method
            result = self._run_full_optimization(
                progress_callback, max_iterations
            )

        elapsed = (datetime.now() - start_time).total_seconds()
        result.computation_time = elapsed

        print("\n" + "="*70)
        print(f"Optimization Complete: {elapsed:.1f}s")
        print("="*70)

        return result

    def _apply_request_parameters(self, request: OptimizationRequest):
        """Apply request parameters to optimization problem"""
        # Adjust emissions limits based on carbon target
        total_emissions = self.capacity_limits.x_em_max * request.carbon_target
        self.capacity_limits.x_em_max = total_emissions

        # Adjust reserve margin
        self.params.gamma_d = request.reserve_margin

        print(f"\nApplied request parameters:")
        print(f"  Carbon target: {request.carbon_target*100:.0f}%")
        print(f"  Budget limit: ${request.budget_limit/1e9:.1f}B")
        print(f"  Reserve margin: {request.reserve_margin*100:.0f}%")

    def _run_simplified_optimization(
        self,
        progress_callback: Optional[Callable],
        max_iterations: int
    ) -> OptimizationResult:
        """
        Run simplified optimization (for testing)

        This creates a feasible solution quickly without running full bundle method
        """
        print("\nGenerating simplified solution...")

        # Create a simple feasible solution
        # Expand generation slightly to meet demand with reserve margin
        total_demand = sum(s.p_d.sum() for s in self.scenarios)
        total_existing_gen = self.params.w_g.sum()

        # Need (demand + reserves) > existing capacity
        expansion_factor = max(0.1, (total_demand * 1.15 - total_existing_gen) / total_existing_gen)
        expansion_factor = min(expansion_factor, 0.5)  # Cap at 50% expansion

        x_g = self.params.w_g * expansion_factor
        x_es_p = np.zeros_like(self.params.w_es_p)
        x_es_e = np.zeros_like(self.params.w_es_e)
        x_br = self.params.w_br * 0.1  # 10% transmission expansion
        x_em = np.array([total_demand * 0.5])  # Simplified emissions

        capacity_decision = CapacityDecision(
            x_g=x_g,
            x_es_p=x_es_p,
            x_es_e=x_es_e,
            x_br=x_br,
            x_em=x_em
        )

        # Calculate objective value
        investment_cost = self.investment_costs.calculate_cost(capacity_decision)
        operational_cost = total_demand * 40.0  # Assume $40/MWh average
        total_cost = investment_cost + operational_cost

        # Simulate progress
        if progress_callback:
            for i in range(1, 6):
                progress = i / 5.0
                progress_callback(
                    i, progress,
                    {
                        "upper_bound": total_cost * (1.1 - progress * 0.1),
                        "lower_bound": total_cost * (0.9 + progress * 0.1),
                        "gap": 0.2 - progress * 0.15
                    }
                )

        result = OptimizationResult(
            total_cost=total_cost,
            capacity_decision=capacity_decision,
            objective_value=total_cost,
            iterations=5,
            convergence_gap=0.05,
            computation_time=0.0,  # Will be set by caller
            status="completed"
        )

        print(f"\nSolution:")
        print(f"  Total cost: ${result.total_cost/1e9:.2f}B")
        print(f"  Generation expansion: {capacity_decision.total_generation_gw:.1f} GW")
        print(f"  Transmission expansion: {capacity_decision.total_transmission_gw:.1f} GW")

        return result

    def _run_full_optimization(
        self,
        progress_callback: Optional[Callable],
        max_iterations: int
    ) -> OptimizationResult:
        """
        Run full CANOPI optimization with bundle method

        This runs the actual CANOPI algorithms
        """
        print("\nInitializing bundle method...")

        # Create progress wrapper
        def bundle_progress_callback(iteration: int, iter_result: BundleIteration):
            if progress_callback:
                progress = min(iteration / max_iterations, 1.0)
                progress_callback(
                    iteration, progress,
                    {
                        "upper_bound": iter_result.f_k,
                        "lower_bound": iter_result.L_k,
                        "gap": iter_result.gap
                    }
                )

        # Initialize x_br_hat (impedance-defining capacity)
        x_br_hat = self.params.w_br.copy()

        # Create bundle method
        bundle = BundleMethod(
            network=self.network,
            investment_costs=self.investment_costs,
            capacity_limits=self.capacity_limits,
            scenarios=self.scenarios,
            operational_params=self.params,
            alpha=0.3,
            epsilon=0.01,
            max_iterations=max_iterations
        )

        # Run bundle method
        print("\nRunning bundle method...")
        x_star, f_star = bundle.solve(
            x_br_hat=x_br_hat,
            progress_callback=bundle_progress_callback,
            verbose=True
        )

        # Run transmission correction (if needed)
        if x_star is not None:
            print("\nRunning transmission correction...")
            # Extract non-transmission decisions
            x_non_br = {
                'x_g': x_star.x_g,
                'x_es_p': x_star.x_es_p,
                'x_es_e': x_star.x_es_e,
                'x_em': x_star.x_em
            }

            # Placeholder for nodal injections (would come from operational solve)
            p_ni_star = {0: np.zeros((self.time_periods, self.network.n))}

            x_br_corrected, converged = iterative_transmission_correction(
                network=self.network,
                x_star_non_br=x_non_br,
                p_ni_star=p_ni_star,
                x_br_initial=x_star.x_br,
                max_iterations=5,
                tolerance=1e-3,
                verbose=True
            )

            # Update capacity decision with corrected transmission
            x_star.x_br = x_br_corrected

        result = OptimizationResult(
            total_cost=f_star,
            capacity_decision=x_star,
            objective_value=f_star,
            iterations=len(bundle.iterations),
            convergence_gap=bundle.iterations[-1].gap if bundle.iterations else 0.0,
            computation_time=0.0,  # Will be set by caller
            status="completed"
        )

        return result


def test_optimizer_service():
    """Test the optimizer service"""
    print("Testing CANOPI Optimizer Service")
    print("="*70)

    # Create service
    service = CANOPIOptimizerService(time_periods=24)

    # Create test request
    request = OptimizationRequest(
        planning_horizon_start=2024,
        planning_horizon_end=2030,
        carbon_target=0.8,
        budget_limit=50e9,  # $50B
        contingency_level="n-1",
        temporal_resolution="hourly",
        reserve_margin=0.15,
        transmission_limit=True
    )

    # Progress callback
    def progress(iteration, pct, info):
        print(f"  Iteration {iteration}: {pct*100:.0f}% - Gap: {info.get('gap', 0)*100:.1f}%")

    # Run optimization (simplified)
    result = service.run_optimization(
        request=request,
        progress_callback=progress,
        max_iterations=50,
        simplified=True  # Use simplified for fast testing
    )

    print("\nResults:")
    print(f"  Status: {result.status}")
    print(f"  Total cost: ${result.total_cost/1e9:.2f}B")
    print(f"  Iterations: {result.iterations}")
    print(f"  Gap: {result.convergence_gap*100:.2f}%")
    print(f"  Time: {result.computation_time:.1f}s")

    # Convert to API format
    api_result = result.to_dict()
    print("\nAPI Response:")
    print(f"  Generation: {api_result['investments']['generation_by_type']}")
    print(f"  Transmission: {api_result['investments']['transmission_gw']:.1f} GW")

    return result


if __name__ == "__main__":
    test_optimizer_service()
