"""
Sample Data Loader for Western Interconnection Grid

Loads CSV files from data_pipelines/sample_data/ and converts them into
CANOPI engine data structures (Network, Node, Branch objects).

Usage:
    from data_pipelines.loaders import load_sample_data

    network, generators, load_profiles, renewable_profiles, costs = load_sample_data()
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import networkx as nx
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from canopi_engine.models.network import Network, Node, Branch
from canopi_engine.models.capacity_decision import InvestmentCosts, CapacityLimits
from canopi_engine.algorithms.operational_subproblem import ScenarioData, OperationalParameters


def get_sample_data_path() -> str:
    """Get the path to the sample data directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'sample_data')


def load_nodes(data_path: str) -> List[Node]:
    """
    Load nodes from nodes.csv

    Returns:
        List of Node objects
    """
    nodes_df = pd.read_csv(os.path.join(data_path, 'nodes.csv'))

    nodes = []
    for _, row in nodes_df.iterrows():
        node = Node(
            id=int(row['id']),
            name=row['name'],
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            voltage_kv=int(row['voltage_kv']),
            is_slack=False  # Will be set later if needed
        )
        nodes.append(node)

    # Set first node as slack bus for power flow
    if nodes:
        nodes[0].is_slack = True

    print(f"Loaded {len(nodes)} nodes")
    return nodes


def load_branches(data_path: str) -> List[Branch]:
    """
    Load branches from branches.csv

    Returns:
        List of Branch objects
    """
    branches_df = pd.read_csv(os.path.join(data_path, 'branches.csv'))

    branches = []
    for _, row in branches_df.iterrows():
        branch = Branch(
            id=int(row['id']),
            from_node=int(row['from_node_id']),
            to_node=int(row['to_node_id']),
            capacity_mw=float(row['capacity_mw']),
            impedance=float(row['impedance']),
            voltage_kv=int(row['voltage_kv']),
            length_km=float(row['length_km']) if pd.notna(row['length_km']) else None
        )
        branches.append(branch)

    print(f"Loaded {len(branches)} branches")
    return branches


def validate_network_connectivity(nodes: List[Node], branches: List[Branch]) -> bool:
    """
    Validate that the network forms a connected graph with no isolated nodes

    Args:
        nodes: List of Node objects
        branches: List of Branch objects

    Returns:
        True if network is connected, False otherwise
    """
    # Create networkx graph
    G = nx.Graph()

    # Add all nodes
    for node in nodes:
        G.add_node(node.id)

    # Add all edges
    for branch in branches:
        G.add_edge(branch.from_node, branch.to_node)

    # Check connectivity
    is_connected = nx.is_connected(G)

    if is_connected:
        print(f"[OK] Network is connected (no isolated nodes)")
    else:
        components = list(nx.connected_components(G))
        print(f"[WARN] Network has {len(components)} disconnected components:")
        for i, comp in enumerate(components):
            print(f"  Component {i+1}: {len(comp)} nodes")

    return is_connected


def load_generators(data_path: str) -> pd.DataFrame:
    """
    Load generator data from generators.csv

    Returns:
        DataFrame with generator information
    """
    generators_df = pd.read_csv(os.path.join(data_path, 'generators.csv'))
    print(f"Loaded {len(generators_df)} generators")

    # Print summary by type
    print("\nGenerator summary by type:")
    for gen_type in generators_df['type'].unique():
        count = len(generators_df[generators_df['type'] == gen_type])
        total_cap = generators_df[generators_df['type'] == gen_type]['capacity_mw'].sum()
        print(f"  {gen_type}: {count} units, {total_cap:.0f} MW")

    return generators_df


def load_load_profiles(data_path: str) -> pd.DataFrame:
    """
    Load hourly load profiles from load_profiles.csv

    Returns:
        DataFrame with timestamp, node_id, load_mw
    """
    load_df = pd.read_csv(os.path.join(data_path, 'load_profiles.csv'))
    load_df['timestamp'] = pd.to_datetime(load_df['timestamp'])

    print(f"\nLoaded {len(load_df)} load records")
    print(f"Time range: {load_df['timestamp'].min()} to {load_df['timestamp'].max()}")
    print(f"Total system load range: {load_df.groupby('timestamp')['load_mw'].sum().min():.0f} - {load_df.groupby('timestamp')['load_mw'].sum().max():.0f} MW")

    return load_df


def load_renewable_profiles(data_path: str) -> pd.DataFrame:
    """
    Load renewable availability profiles from renewable_profiles.csv

    Returns:
        DataFrame with timestamp, generator_id, availability_factor
    """
    # Check if full file exists, otherwise use template
    renewable_path = os.path.join(data_path, 'renewable_profiles.csv')
    if not os.path.exists(renewable_path):
        renewable_path = os.path.join(data_path, 'renewable_profiles_template.csv')
        print("\nUsing renewable profiles template (subset of data)")

    renewable_df = pd.read_csv(renewable_path)
    renewable_df['timestamp'] = pd.to_datetime(renewable_df['timestamp'])

    print(f"\nLoaded {len(renewable_df)} renewable availability records")
    print(f"Solar generators: {sorted(renewable_df[renewable_df['generator_id'].isin([10,11,12,13,31,32,33,45])]['generator_id'].unique())}")
    print(f"Wind generators: {sorted(renewable_df[renewable_df['generator_id'].isin([14,15,16,34,37,38,39])]['generator_id'].unique())}")

    return renewable_df


def load_generator_costs(data_path: str) -> pd.DataFrame:
    """
    Load generator operating costs from generator_costs.csv

    Returns:
        DataFrame with generator_id, fuel costs, VOM costs, total marginal costs
    """
    costs_df = pd.read_csv(os.path.join(data_path, 'generator_costs.csv'))

    print(f"\nLoaded operating costs for {len(costs_df)} generators")
    print(f"Marginal cost range: ${costs_df['total_marginal_cost_per_mwh'].min():.2f} - ${costs_df['total_marginal_cost_per_mwh'].max():.2f} per MWh")

    return costs_df


def create_network(nodes: List[Node], branches: List[Branch]) -> Network:
    """
    Create a Network object from nodes and branches

    Args:
        nodes: List of Node objects
        branches: List of Branch objects

    Returns:
        Network object
    """
    network = Network(nodes=nodes, branches=branches, hvdc_lines=[])

    print(f"\nCreated network: {network}")
    print(f"  Nodes: {network.n}")
    print(f"  Branches: {network.b}")
    print(f"  Branch capacity range: {network.get_branch_capacities().min():.0f} - {network.get_branch_capacities().max():.0f} MW")
    print(f"  Impedance range: {network.get_branch_impedances().min():.4f} - {network.get_branch_impedances().max():.4f} p.u.")

    return network


def load_sample_data(validate_connectivity: bool = True) -> Tuple[Network, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all sample data files and create CANOPI data structures

    Args:
        validate_connectivity: If True, validate that network is connected

    Returns:
        Tuple of (network, generators_df, load_profiles_df, renewable_profiles_df, costs_df)
    """
    print("=" * 70)
    print("Loading Western Interconnection Sample Data")
    print("=" * 70)

    data_path = get_sample_data_path()

    # Load nodes and branches
    nodes = load_nodes(data_path)
    branches = load_branches(data_path)

    # Validate connectivity
    if validate_connectivity:
        print()
        validate_network_connectivity(nodes, branches)

    # Create network object
    network = create_network(nodes, branches)

    # Load generator data
    generators_df = load_generators(data_path)

    # Load time series data
    load_profiles_df = load_load_profiles(data_path)
    renewable_profiles_df = load_renewable_profiles(data_path)
    costs_df = load_generator_costs(data_path)

    print("\n" + "=" * 70)
    print("Sample data loaded successfully!")
    print("=" * 70)

    return network, generators_df, load_profiles_df, renewable_profiles_df, costs_df


def export_to_optimization_format(
    network: Network,
    generators_df: pd.DataFrame,
    load_profiles_df: pd.DataFrame,
    costs_df: pd.DataFrame
) -> Dict:
    """
    Export loaded data in format ready for optimization algorithm

    Args:
        network: Network object
        generators_df: Generator DataFrame
        load_profiles_df: Load profiles DataFrame
        costs_df: Generator costs DataFrame

    Returns:
        Dictionary with optimization problem data
    """
    # Get unique timestamps
    timestamps = sorted(load_profiles_df['timestamp'].unique())
    T = len(timestamps)

    # Existing generators (capacity > 0)
    existing_gens = generators_df[generators_df['capacity_mw'] > 0]
    G_existing = len(existing_gens)

    # Candidate generators (capacity = 0)
    candidate_gens = generators_df[generators_df['capacity_mw'] == 0]
    G_candidate = len(candidate_gens)

    # Create load matrix (T x n)
    load_matrix = np.zeros((T, network.n))
    for t_idx, ts in enumerate(timestamps):
        ts_data = load_profiles_df[load_profiles_df['timestamp'] == ts]
        for _, row in ts_data.iterrows():
            load_matrix[t_idx, int(row['node_id'])] = row['load_mw']

    # Create generator capacity vector
    gen_capacity = existing_gens['capacity_mw'].values

    # Create cost vectors
    gen_costs = costs_df.merge(
        generators_df[['id', 'node_id']],
        left_on='generator_id',
        right_on='id'
    )

    return {
        'network': network,
        'T': T,
        'timestamps': timestamps,
        'G_existing': G_existing,
        'G_candidate': G_candidate,
        'load_matrix': load_matrix,
        'total_system_load': load_matrix.sum(axis=1),
        'gen_capacity': gen_capacity,
        'gen_nodes': existing_gens['node_id'].values,
        'gen_costs': gen_costs['total_marginal_cost_per_mwh'].values,
        'existing_generators': existing_gens,
        'candidate_generators': candidate_gens,
    }


def create_operational_parameters(
    network: Network,
    generators_df: pd.DataFrame
) -> OperationalParameters:
    """
    Create OperationalParameters from loaded data

    Args:
        network: Network object
        generators_df: Generator DataFrame

    Returns:
        OperationalParameters object
    """
    # Get existing generators
    existing_gens = generators_df[generators_df['capacity_mw'] > 0]
    G = len(existing_gens)
    n = network.n

    # Generator capacities and parameters
    w_g = existing_gens['capacity_mw'].values

    # Generator-node incidence matrix
    A_g = np.zeros((n, G))
    for i, node_id in enumerate(existing_gens['node_id'].values):
        A_g[int(node_id), i] = 1.0

    # Generator ramp rates (assume 50% per hour)
    R = w_g * 0.5

    # Emissions factors
    e = existing_gens['carbon_intensity'].values

    # Storage (none for now)
    w_es_p = np.array([])
    w_es_e = np.array([])
    A_es = np.zeros((n, 0))

    # Branch capacities
    w_br = network.get_branch_capacities()

    # Load-node incidence (nodes with load data)
    load_nodes = [0, 3, 12, 13, 18, 22, 23, 46, 51, 53]
    D = len(load_nodes)
    A_d = np.zeros((n, D))
    for i, node_id in enumerate(load_nodes):
        A_d[node_id, i] = 1.0

    params = OperationalParameters(
        w_g=w_g,
        w_es_p=w_es_p,
        w_es_e=w_es_e,
        w_br=w_br,
        R=R,
        e=e,
        eta=0.90,
        gamma_es=0.50,
        gamma_d=0.15,
        eta_c=1.0,
        A_g=A_g,
        A_es=A_es,
        A_d=A_d
    )

    print(f"\nCreated operational parameters:")
    print(f"  Generators: {G}")
    print(f"  Total capacity: {w_g.sum()/1000:.1f} GW")
    print(f"  Load points: {D}")

    return params


def create_scenario_data(
    generators_df: pd.DataFrame,
    load_profiles_df: pd.DataFrame,
    renewable_profiles_df: pd.DataFrame,
    costs_df: pd.DataFrame,
    time_periods: int = 24
) -> ScenarioData:
    """
    Create ScenarioData from loaded profiles

    Args:
        generators_df: Generator DataFrame
        load_profiles_df: Load profiles DataFrame
        renewable_profiles_df: Renewable profiles DataFrame
        costs_df: Generator costs DataFrame
        time_periods: Number of time periods

    Returns:
        ScenarioData object
    """
    existing_gens = generators_df[generators_df['capacity_mw'] > 0]
    G = len(existing_gens)

    # Get timestamps
    timestamps = sorted(load_profiles_df['timestamp'].unique())[:time_periods]
    T = len(timestamps)

    # Generator costs (T x G)
    c_g = np.zeros((T, G))
    for i, gen_id in enumerate(existing_gens['id'].values):
        if gen_id in costs_df['generator_id'].values:
            cost = costs_df[costs_df['generator_id'] == gen_id]['total_marginal_cost_per_mwh'].values[0]
            c_g[:, i] = cost
        else:
            # Default cost based on type
            gen_type = existing_gens.iloc[i]['type']
            if gen_type == 'nuclear':
                c_g[:, i] = 12.0
            elif gen_type == 'coal':
                c_g[:, i] = 30.0
            elif gen_type == 'gas':
                c_g[:, i] = 50.0
            elif gen_type in ['solar', 'wind', 'hydro']:
                c_g[:, i] = 0.0
            else:
                c_g[:, i] = 40.0

    # Availability factors (T x G)
    a_g = np.ones((T, G))

    # Apply renewable availability
    for i, gen_id in enumerate(existing_gens['id'].values):
        gen_type = existing_gens.iloc[i]['type']

        if gen_type in ['solar', 'wind']:
            # Use renewable profiles if available
            gen_profiles = renewable_profiles_df[renewable_profiles_df['generator_id'] == gen_id]
            if len(gen_profiles) > 0:
                for t, ts in enumerate(timestamps):
                    ts_data = gen_profiles[gen_profiles['timestamp'] == ts]
                    if len(ts_data) > 0:
                        a_g[t, i] = ts_data.iloc[0]['availability_factor']
                    else:
                        # Use default profile
                        hour = t % 24
                        if gen_type == 'solar':
                            if 6 <= hour <= 18:
                                a_g[t, i] = 0.3 + 0.7 * np.sin(np.pi * (hour - 6) / 12)
                            else:
                                a_g[t, i] = 0.0
                        else:  # wind
                            a_g[t, i] = 0.3 + 0.4 * np.sin(2 * np.pi * hour / 24)
            else:
                # Default profiles
                for t in range(T):
                    hour = t % 24
                    if gen_type == 'solar':
                        if 6 <= hour <= 18:
                            a_g[t, i] = 0.3 + 0.7 * np.sin(np.pi * (hour - 6) / 12)
                        else:
                            a_g[t, i] = 0.0
                    else:  # wind
                        a_g[t, i] = 0.3 + 0.4 * np.sin(2 * np.pi * hour / 24)

    # Load demand (T x D)
    load_nodes = [0, 3, 12, 13, 18, 22, 23, 46, 51, 53]
    D = len(load_nodes)
    p_d = np.zeros((T, D))

    for t, ts in enumerate(timestamps):
        ts_data = load_profiles_df[load_profiles_df['timestamp'] == ts]
        for i, node_id in enumerate(load_nodes):
            node_data = ts_data[ts_data['node_id'] == node_id]
            if len(node_data) > 0:
                p_d[t, i] = node_data.iloc[0]['load_mw']
            else:
                # Default load profile
                hour = t % 24
                base_load = 1000.0 * (i + 1) / D  # Scale by node importance
                if 0 <= hour < 6:
                    p_d[t, i] = base_load * 0.7
                elif 6 <= hour < 12:
                    p_d[t, i] = base_load * 0.9
                elif 12 <= hour < 18:
                    p_d[t, i] = base_load * 1.0
                else:
                    p_d[t, i] = base_load * 0.85

    scenario = ScenarioData(
        c_g=c_g,
        a_g=a_g,
        p_d=p_d,
        c_sh=10000.0,
        c_vio=2000.0
    )

    print(f"\nCreated scenario data:")
    print(f"  Time periods: {T}")
    print(f"  Total demand: {p_d.sum()/1000:.1f} GWh")
    print(f"  Demand range: {p_d.sum(axis=1).min():.0f} - {p_d.sum(axis=1).max():.0f} MW")

    return scenario


def create_investment_costs(
    network: Network,
    generators_df: pd.DataFrame
) -> InvestmentCosts:
    """
    Create InvestmentCosts from loaded data

    Args:
        network: Network object
        generators_df: Generator DataFrame

    Returns:
        InvestmentCosts object
    """
    existing_gens = generators_df[generators_df['capacity_mw'] > 0]

    # Annualization factor (30 years, 5% discount rate)
    crf = 0.0651

    # Generator costs
    c_g = existing_gens['capex_per_mw'].values * crf

    # Storage costs (none for now)
    c_es_p = np.array([])
    c_es_e = np.array([])

    # Transmission costs ($/MW per year)
    c_br_per_mw_km = 1500.0
    c_br = np.array([
        c_br_per_mw_km * (branch.length_km or 100.0)
        for branch in network.branches
    ]) * crf

    # Emissions penalty
    c_em = np.array([100.0])

    costs = InvestmentCosts(
        c_g=c_g,
        c_es_p=c_es_p,
        c_es_e=c_es_e,
        c_br=c_br,
        c_em=c_em
    )

    print(f"\nCreated investment costs:")
    print(f"  Avg gen: ${c_g.mean()/1e6:.2f}M/MW/yr")
    print(f"  Avg trans: ${c_br.mean()/1e6:.2f}M/MW/yr")

    return costs


def create_capacity_limits(
    network: Network,
    generators_df: pd.DataFrame
) -> CapacityLimits:
    """
    Create CapacityLimits from loaded data

    Args:
        network: Network object
        generators_df: Generator DataFrame

    Returns:
        CapacityLimits object
    """
    existing_gens = generators_df[generators_df['capacity_mw'] > 0]

    # Can expand generation by 2x
    x_g_max = existing_gens['capacity_mw'].values * 2.0

    # Storage limits (none for now)
    x_es_p_max = np.array([])
    x_es_e_max = np.array([])

    # Can expand transmission by 2x
    x_br_max = network.get_branch_capacities() * 2.0

    # Emissions limit (1 billion tons)
    x_em_max = 1e9

    limits = CapacityLimits(
        x_g_max=x_g_max,
        x_es_p_max=x_es_p_max,
        x_es_e_max=x_es_e_max,
        x_br_max=x_br_max,
        x_em_max=x_em_max
    )

    print(f"\nCreated capacity limits:")
    print(f"  Max gen expansion: {x_g_max.sum()/1000:.1f} GW")
    print(f"  Max trans expansion: {x_br_max.sum()/1000:.1f} GW")

    return limits


def load_complete_optimization_data(time_periods: int = 24) -> Dict:
    """
    Load all data structures needed for CANOPI optimization

    Args:
        time_periods: Number of time periods to simulate

    Returns:
        Dictionary with all optimization data
    """
    print("=" * 70)
    print("Loading Complete Optimization Data for CANOPI")
    print("=" * 70)

    # Load base data
    network, generators_df, load_profiles_df, renewable_profiles_df, costs_df = load_sample_data(
        validate_connectivity=True
    )

    # Create CANOPI data structures
    params = create_operational_parameters(network, generators_df)
    scenario = create_scenario_data(
        generators_df, load_profiles_df, renewable_profiles_df, costs_df, time_periods
    )
    investment_costs = create_investment_costs(network, generators_df)
    capacity_limits = create_capacity_limits(network, generators_df)

    print("\n" + "=" * 70)
    print("Complete Optimization Data Loaded Successfully!")
    print("=" * 70)

    return {
        'network': network,
        'params': params,
        'scenarios': [scenario],
        'investment_costs': investment_costs,
        'capacity_limits': capacity_limits,
        'time_periods': time_periods
    }


if __name__ == '__main__':
    # Test loading
    data = load_complete_optimization_data(time_periods=24)

    print(f"\nValidation:")
    print(f"  Network: {data['network']}")
    print(f"  Generators: {len(data['params'].w_g)}")
    print(f"  Scenarios: {len(data['scenarios'])}")
    print(f"  Time periods: {data['time_periods']}")
