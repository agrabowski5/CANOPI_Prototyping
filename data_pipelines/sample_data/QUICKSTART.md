# Quick Start Guide: Western Interconnection Sample Data

Get started with the CANOPI sample dataset in 5 minutes.

## Installation

No installation required! The sample data is included in the repository.

**Optional dependencies for visualization:**
```bash
pip install matplotlib pandas numpy networkx
```

## 1. Load the Data (Python)

```python
# Import the loader
from data_pipelines.loaders import load_sample_data

# Load everything
network, generators_df, load_profiles_df, renewable_profiles_df, costs_df = load_sample_data()

# That's it! You now have:
# - network: Network object with 55 nodes and 90 branches
# - generators_df: DataFrame with 41 generators
# - load_profiles_df: 168 hours of load data
# - renewable_profiles_df: Solar and wind availability
# - costs_df: Operating costs for all generators
```

## 2. Explore the Network

```python
# Network properties
print(f"Nodes: {network.n}")           # 55
print(f"Branches: {network.b}")        # 90
print(f"HVDC lines: {network.β}")      # 0

# Node information
for node in network.nodes[:5]:  # First 5 nodes
    print(f"{node.id}: {node.name} ({node.voltage_kv} kV)")

# Branch information
for branch in network.branches[:5]:  # First 5 branches
    print(f"Branch {branch.id}: {branch.from_node} → {branch.to_node}, "
          f"{branch.capacity_mw} MW, {branch.voltage_kv} kV")

# Get capacity and impedance vectors
capacities = network.get_branch_capacities()  # numpy array (90,)
impedances = network.get_branch_impedances()  # numpy array (90,)

# Get incidence matrix
A_br = network.A_br  # numpy array (55, 90)
```

## 3. Analyze Generators

```python
import pandas as pd

# Existing generation by type
existing = generators_df[generators_df['capacity_mw'] > 0]
print(existing.groupby('type')['capacity_mw'].sum())

# Output:
# coal       5110
# gas        8415
# hydro     12183
# nuclear    6177
# solar      1630
# wind        923

# Candidate expansion sites
candidates = generators_df[generators_df['capacity_mw'] == 0]
print(f"Candidate sites: {len(candidates)}")  # 11

# Generator costs
merged = generators_df.merge(costs_df, left_on='id', right_on='generator_id')
print(merged[['name_x', 'type_x', 'capacity_mw', 'total_marginal_cost_per_mwh']])
```

## 4. Work with Load Profiles

```python
import pandas as pd

# Total system load over time
system_load = load_profiles_df.groupby('timestamp')['load_mw'].sum()

print(f"Peak load: {system_load.max():.0f} MW")      # ~39,000 MW
print(f"Minimum load: {system_load.min():.0f} MW")   # ~17,000 MW
print(f"Average load: {system_load.mean():.0f} MW")  # ~27,000 MW

# Load at a specific node (Los Angeles)
la_load = load_profiles_df[load_profiles_df['node_id'] == 0]
print(la_load.head())

# Create load matrix for optimization (time × nodes)
import numpy as np
timestamps = sorted(load_profiles_df['timestamp'].unique())
load_matrix = np.zeros((len(timestamps), network.n))

for t_idx, ts in enumerate(timestamps):
    ts_data = load_profiles_df[load_profiles_df['timestamp'] == ts]
    for _, row in ts_data.iterrows():
        load_matrix[t_idx, int(row['node_id'])] = row['load_mw']

print(f"Load matrix shape: {load_matrix.shape}")  # (168, 55)
```

## 5. Examine Renewable Profiles

```python
# Solar availability
solar_gens = [10, 11, 12, 13]  # Solar generator IDs
solar_data = renewable_profiles_df[renewable_profiles_df['generator_id'].isin(solar_gens)]

# Check diurnal pattern
print("Solar availability by hour:")
solar_data['hour'] = pd.to_datetime(solar_data['timestamp']).dt.hour
print(solar_data.groupby('hour')['availability_factor'].mean())

# Wind availability
wind_gens = [14, 15, 16, 38, 39]  # Wind generator IDs
wind_data = renewable_profiles_df[renewable_profiles_df['generator_id'].isin(wind_gens)]

print(f"\nWind capacity factor: {wind_data['availability_factor'].mean():.2%}")
```

## 6. Visualize the Network

```python
# Method 1: Use built-in visualization script
import os
os.chdir('data_pipelines/sample_data')
exec(open('visualize_network.py').read())

# Method 2: Custom matplotlib visualization
import matplotlib.pyplot as plt

# Plot nodes
fig, ax = plt.subplots(figsize=(12, 10))

for node in network.nodes:
    ax.scatter(node.longitude, node.latitude, s=50, c='blue', alpha=0.6)

for branch in network.branches:
    from_node = network.nodes[branch.from_node]
    to_node = network.nodes[branch.to_node]
    ax.plot([from_node.longitude, to_node.longitude],
            [from_node.latitude, to_node.latitude],
            'gray', linewidth=0.5, alpha=0.3)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Western Interconnection Sample Network')
plt.show()
```

## 7. Export for Optimization

```python
from data_pipelines.loaders.sample_data_loader import export_to_optimization_format

# Export data in optimization-ready format
opt_data = export_to_optimization_format(
    network,
    generators_df,
    load_profiles_df,
    costs_df
)

# Access optimization problem components
T = opt_data['T']                          # 168 time periods
load_matrix = opt_data['load_matrix']      # (168, 55) array
gen_capacity = opt_data['gen_capacity']    # Existing capacity vector
gen_costs = opt_data['gen_costs']          # Marginal cost vector
gen_nodes = opt_data['gen_nodes']          # Generator locations

print(f"Optimization problem size:")
print(f"  Time periods: {T}")
print(f"  Nodes: {network.n}")
print(f"  Existing generators: {opt_data['G_existing']}")
print(f"  Candidate generators: {opt_data['G_candidate']}")
```

## 8. Validate Data Integrity

```python
# Run validation tests
from data_pipelines.loaders import validate_network_connectivity

is_connected = validate_network_connectivity(network.nodes, network.branches)
print(f"Network is connected: {is_connected}")  # True

# Run full test suite
import subprocess
subprocess.run(['python', 'data_pipelines/sample_data/test_data_loader.py'])
```

## 9. Simple Economic Dispatch Example

```python
import numpy as np

# Get first hour load
hour_0_load = load_profiles_df[load_profiles_df['timestamp'] == timestamps[0]]
total_load = hour_0_load['load_mw'].sum()

print(f"Hour 0 total load: {total_load:.0f} MW")

# Get generator costs (sorted by marginal cost)
gen_data = generators_df[generators_df['capacity_mw'] > 0].merge(
    costs_df, left_on='id', right_on='generator_id'
).sort_values('total_marginal_cost_per_mwh')

# Simple merit order dispatch
remaining_load = total_load
dispatch = []

for _, gen in gen_data.iterrows():
    if remaining_load <= 0:
        power = 0
    else:
        power = min(gen['capacity_mw'], remaining_load)

    dispatch.append({
        'name': gen['name_x'],
        'type': gen['type_x'],
        'capacity': gen['capacity_mw'],
        'dispatch': power,
        'cost': gen['total_marginal_cost_per_mwh']
    })
    remaining_load -= power

dispatch_df = pd.DataFrame(dispatch)
print("\nMerit order dispatch:")
print(dispatch_df[dispatch_df['dispatch'] > 0])

total_cost = sum(d['dispatch'] * d['cost'] for d in dispatch)
print(f"\nTotal generation cost: ${total_cost:,.0f}/hour")
```

## 10. Common Patterns

### Get all nodes of a specific type
```python
solar_nodes = [n for n in network.nodes if 'solar' in n.name.lower()]
```

### Find branches connected to a node
```python
node_id = 0
connected_branches = [b for b in network.branches
                     if b.from_node == node_id or b.to_node == node_id]
```

### Calculate total transmission capacity
```python
total_capacity = sum(b.capacity_mw for b in network.branches)
print(f"Total transmission capacity: {total_capacity:,.0f} MW")
```

### Get load duration curve
```python
system_load = load_profiles_df.groupby('timestamp')['load_mw'].sum().sort_values(ascending=False)
plt.plot(range(len(system_load)), system_load.values)
plt.xlabel('Hours')
plt.ylabel('Load (MW)')
plt.title('Load Duration Curve')
plt.grid(True)
plt.show()
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Run [test_data_loader.py](test_data_loader.py) to validate data
- Use [visualize_network.py](visualize_network.py) to create maps
- Explore the CANOPI optimization algorithms in `canopi_engine/`

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review data file formats in the CSV files
- Look at example code in `sample_data_loader.py`
- Open an issue on GitHub

## Data Summary

| Metric | Value |
|--------|-------|
| Network nodes | 55 |
| Transmission lines | 90 |
| Existing generators | 30 |
| Candidate sites | 11 |
| Time periods | 168 hours (1 week) |
| Load centers | 10 |
| Peak system load | ~39 GW |
| Total generation capacity | ~40 GW |
| Voltage levels | 230, 345, 500 kV |

Happy optimizing! 🔌⚡
