"""
Test script for sample data loader

Verifies that all data files can be loaded and validates data integrity.

Usage:
    python test_data_loader.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_pipelines.loaders import load_sample_data, validate_network_connectivity


def test_basic_loading():
    """Test that all files can be loaded"""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Data Loading")
    print("=" * 70)

    try:
        network, generators_df, load_profiles_df, renewable_profiles_df, costs_df = load_sample_data()
        print("\n✓ All data files loaded successfully")
        return True
    except Exception as e:
        print(f"\n✗ Error loading data: {e}")
        return False


def test_network_structure(network):
    """Test network structure and properties"""
    print("\n" + "=" * 70)
    print("TEST 2: Network Structure")
    print("=" * 70)

    tests_passed = True

    # Check node count
    if network.n == 55:
        print(f"✓ Node count correct: {network.n}")
    else:
        print(f"✗ Expected 55 nodes, got {network.n}")
        tests_passed = False

    # Check branch count
    if network.b == 90:
        print(f"✓ Branch count correct: {network.b}")
    else:
        print(f"✗ Expected 90 branches, got {network.b}")
        tests_passed = False

    # Check incidence matrix dimensions
    if network.A_br.shape == (55, 90):
        print(f"✓ Incidence matrix dimensions correct: {network.A_br.shape}")
    else:
        print(f"✗ Expected (55, 90), got {network.A_br.shape}")
        tests_passed = False

    # Check branch capacities
    capacities = network.get_branch_capacities()
    if (capacities > 0).all():
        print(f"✓ All branch capacities positive: {capacities.min():.0f} - {capacities.max():.0f} MW")
    else:
        print(f"✗ Some branch capacities are zero or negative")
        tests_passed = False

    # Check impedances
    impedances = network.get_branch_impedances()
    if (impedances > 0).all() and (impedances < 1).all():
        print(f"✓ Impedances in valid range: {impedances.min():.4f} - {impedances.max():.4f} p.u.")
    else:
        print(f"✗ Some impedances out of range")
        tests_passed = False

    return tests_passed


def test_connectivity(network):
    """Test network connectivity"""
    print("\n" + "=" * 70)
    print("TEST 3: Network Connectivity")
    print("=" * 70)

    is_connected = validate_network_connectivity(network.nodes, network.branches)

    if is_connected:
        print("✓ Network is fully connected")
        return True
    else:
        print("✗ Network has disconnected components")
        return False


def test_generators(generators_df):
    """Test generator data"""
    print("\n" + "=" * 70)
    print("TEST 4: Generator Data")
    print("=" * 70)

    tests_passed = True

    # Check generator count
    if len(generators_df) == 41:
        print(f"✓ Generator count correct: {len(generators_df)}")
    else:
        print(f"✗ Expected 41 generators, got {len(generators_df)}")
        tests_passed = False

    # Check existing vs candidate
    existing = generators_df[generators_df['capacity_mw'] > 0]
    candidate = generators_df[generators_df['capacity_mw'] == 0]

    if len(existing) == 30:
        print(f"✓ Existing generators: {len(existing)}")
    else:
        print(f"✗ Expected 30 existing generators, got {len(existing)}")
        tests_passed = False

    if len(candidate) == 11:
        print(f"✓ Candidate generators: {len(candidate)}")
    else:
        print(f"✗ Expected 11 candidate generators, got {len(candidate)}")
        tests_passed = False

    # Check technology types
    expected_types = {'nuclear', 'coal', 'gas', 'hydro', 'solar', 'wind', 'storage'}
    actual_types = set(generators_df['type'].unique())

    if expected_types == actual_types:
        print(f"✓ All technology types present: {sorted(actual_types)}")
    else:
        print(f"✗ Missing types: {expected_types - actual_types}")
        tests_passed = False

    # Check costs are positive
    if (generators_df['capex_per_mw'] > 0).all():
        print(f"✓ All CAPEX values positive")
    else:
        print(f"✗ Some CAPEX values are zero or negative")
        tests_passed = False

    return tests_passed


def test_load_profiles(load_profiles_df):
    """Test load profile data"""
    print("\n" + "=" * 70)
    print("TEST 5: Load Profiles")
    print("=" * 70)

    tests_passed = True

    # Check time range
    timestamps = load_profiles_df['timestamp'].unique()
    if len(timestamps) == 168:
        print(f"✓ Time period correct: {len(timestamps)} hours")
    else:
        print(f"✗ Expected 168 hours, got {len(timestamps)}")
        tests_passed = False

    # Check load centers
    load_nodes = load_profiles_df['node_id'].unique()
    if len(load_nodes) == 10:
        print(f"✓ Load center count correct: {len(load_nodes)}")
    else:
        print(f"✗ Expected 10 load centers, got {len(load_nodes)}")
        tests_passed = False

    # Check load values are positive
    if (load_profiles_df['load_mw'] > 0).all():
        min_load = load_profiles_df.groupby('timestamp')['load_mw'].sum().min()
        max_load = load_profiles_df.groupby('timestamp')['load_mw'].sum().max()
        print(f"✓ All load values positive: {min_load:.0f} - {max_load:.0f} MW system load")
    else:
        print(f"✗ Some load values are zero or negative")
        tests_passed = False

    return tests_passed


def test_renewable_profiles(renewable_profiles_df):
    """Test renewable availability profiles"""
    print("\n" + "=" * 70)
    print("TEST 6: Renewable Profiles")
    print("=" * 70)

    tests_passed = True

    # Check availability factors in valid range
    if (renewable_profiles_df['availability_factor'] >= 0).all() and \
       (renewable_profiles_df['availability_factor'] <= 1).all():
        print(f"✓ Availability factors in valid range [0, 1]")
    else:
        print(f"✗ Some availability factors out of range")
        tests_passed = False

    # Check generator types
    gen_ids = renewable_profiles_df['generator_id'].unique()
    solar_ids = [10, 11, 12, 13, 31, 32, 33, 45]
    wind_ids = [14, 15, 16, 34, 37, 38, 39]

    has_solar = any(g in gen_ids for g in solar_ids)
    has_wind = any(g in gen_ids for g in wind_ids)

    if has_solar and has_wind:
        print(f"✓ Both solar and wind profiles present")
    else:
        print(f"✗ Missing solar or wind profiles")
        tests_passed = False

    return tests_passed


def test_costs(costs_df, generators_df):
    """Test generator cost data"""
    print("\n" + "=" * 70)
    print("TEST 7: Generator Costs")
    print("=" * 70)

    tests_passed = True

    # Check all generators have costs
    if len(costs_df) == len(generators_df):
        print(f"✓ Cost data for all generators: {len(costs_df)}")
    else:
        print(f"✗ Missing cost data for some generators")
        tests_passed = False

    # Check renewable costs are zero
    renewable_types = ['solar', 'wind']
    renewable_costs = costs_df[costs_df['type'].isin(renewable_types)]

    if (renewable_costs['total_marginal_cost_per_mwh'] == 0).all():
        print(f"✓ Renewable marginal costs are zero")
    else:
        print(f"✗ Some renewable marginal costs are non-zero")
        tests_passed = False

    # Check fossil fuel costs are positive
    fossil_types = ['coal', 'gas']
    fossil_costs = costs_df[costs_df['type'].isin(fossil_types)]

    if (fossil_costs['total_marginal_cost_per_mwh'] > 0).all():
        print(f"✓ Fossil fuel marginal costs positive")
    else:
        print(f"✗ Some fossil fuel marginal costs are zero or negative")
        tests_passed = False

    return tests_passed


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("CANOPI SAMPLE DATA VALIDATION TESTS")
    print("=" * 70)

    # Load data
    if not test_basic_loading():
        print("\n✗ FAILED: Cannot load data files")
        return False

    # Reload for testing
    network, generators_df, load_profiles_df, renewable_profiles_df, costs_df = load_sample_data(
        validate_connectivity=False
    )

    # Run tests
    results = {
        'Network Structure': test_network_structure(network),
        'Network Connectivity': test_connectivity(network),
        'Generator Data': test_generators(generators_df),
        'Load Profiles': test_load_profiles(load_profiles_df),
        'Renewable Profiles': test_renewable_profiles(renewable_profiles_df),
        'Generator Costs': test_costs(costs_df, generators_df)
    }

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70 + "\n")

    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
