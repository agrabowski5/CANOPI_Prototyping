# Western Interconnection Sample Data

Realistic sample data for the Western Interconnection power grid for testing CANOPI optimization algorithms.

## Overview

This dataset represents a simplified but realistic model of the Western Interconnection, covering power transmission and generation across the western United States including California, Nevada, Arizona, Utah, Colorado, Wyoming, Idaho, Oregon, Washington, and Montana.

**Network Size:**
- **55 nodes** (substations and generation sites)
- **90 transmission lines** (230-500 kV)
- **41 generators** (30 existing + 11 candidate expansions)
- **10 load centers** with hourly profiles
- **168 hours** of operational data (1 week)

## Data Files

### 1. `nodes.csv` - Network Nodes

Transmission substations, generation sites, and load centers across the Western US.

**Columns:**
- `id`: Unique node identifier (0-54)
- `name`: Node name (location - facility)
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `voltage_kv`: Voltage level (230, 345, or 500 kV)
- `iso_rto`: Independent System Operator (CAISO or WECC)
- `type`: Node type (substation, nuclear, coal, gas, hydro, solar, wind, load_center, storage)

**Node Types:**
- **Substations (36)**: Major transmission hubs
- **Generation sites (15)**: Existing power plants
- **Load centers (10)**: Major demand centers
- **Candidate sites (11)**: Potential new generation locations

**Major Cities Covered:**
- Los Angeles, San Diego, San Francisco, San Jose
- Sacramento, Fresno, Bakersfield
- Las Vegas, Phoenix, Tucson
- Denver, Salt Lake City, Albuquerque
- Portland, Seattle, Spokane, Boise

### 2. `branches.csv` - Transmission Lines

High-voltage AC transmission lines connecting nodes.

**Columns:**
- `id`: Unique branch identifier (0-89)
- `from_node_id`: Source node ID
- `to_node_id`: Destination node ID
- `capacity_mw`: Thermal capacity limit (MW)
- `impedance`: Line impedance in per-unit (p.u.)
- `voltage_kv`: Operating voltage (230, 345, or 500 kV)
- `length_km`: Approximate line length (km)

**Voltage Levels:**
- **500 kV**: Long-distance bulk transmission (1000-3000 MW capacity)
- **345 kV**: Regional transmission (500-1500 MW capacity)
- **230 kV**: Sub-transmission and distribution (300-1000 MW capacity)

**Network Properties:**
- Fully connected topology (no isolated nodes)
- Realistic impedances proportional to line length
- Based on actual Western Interconnection pathways

### 3. `generators.csv` - Generation Assets

Existing power plants and candidate expansion sites.

**Columns:**
- `id`: Unique generator identifier (0-40)
- `node_id`: Connected node ID
- `name`: Generator name
- `type`: Technology (nuclear, coal, gas, hydro, solar, wind, storage)
- `capacity_mw`: Installed capacity (0 = candidate for expansion)
- `capex_per_mw`: Capital cost ($/MW)
- `opex_per_mw_year`: Annual O&M cost ($/MW/year)
- `carbon_intensity`: CO2 emissions (kg CO2/MWh)

**Existing Generation (30 units, ~40 GW):**
- **Nuclear (2)**: 6,177 MW - Diablo Canyon, Palo Verde
- **Coal (3)**: 5,110 MW - Four Corners, Navajo, Comanche
- **Natural Gas (12)**: 8,415 MW - Combined cycle and peakers
- **Hydro (8)**: 12,183 MW - Bonneville, Grand Coulee, Glen Canyon, etc.
- **Solar (4)**: 1,630 MW - Desert Southwest, Coachella Valley
- **Wind (3)**: 923 MW - Wild Horse, Chokecherry, Elk Grove

**Candidate Expansion (11 units):**
- Solar (4 sites), Wind (3 sites), Gas (2 sites), Hydro (1 site), Battery Storage (2 sites)

**Cost Data (NREL ATB 2024):**
- Nuclear: $6.5M/MW capex, $100k/MW/yr opex
- Coal: $3.8M/MW capex, $95k/MW/yr opex
- Gas CC: $1.1M/MW capex, $25k/MW/yr opex
- Hydro: $4.2M/MW capex, $45k/MW/yr opex
- Solar: $1.35M/MW capex, $18k/MW/yr opex
- Wind: $1.6M/MW capex, $45k/MW/yr opex
- Storage: $1.5M/MW capex, $25k/MW/yr opex

### 4. `load_profiles.csv` - Hourly Load Demand

Realistic hourly electricity demand at 10 major load centers for one week (July 1-7, 2024).

**Columns:**
- `timestamp`: Date and time (hourly intervals)
- `node_id`: Load center node ID
- `load_mw`: Electricity demand (MW)

**Load Centers:**
- Los Angeles (node 0): 3,500-6,900 MW
- San Francisco (node 3): 2,300-4,600 MW
- Phoenix (node 12): 1,760-3,460 MW
- Phoenix West (node 13): 1,500-2,950 MW
- Salt Lake City (node 18): 1,165-2,290 MW
- Portland (node 22): 1,330-2,610 MW
- Seattle (node 23): 1,245-2,445 MW
- Eureka (node 46): 246-530 MW
- Santa Barbara (node 51): 365-785 MW
- Riverside (node 53): 728-1,567 MW

**Load Patterns:**
- Realistic summer daily profiles
- Peak demand: 2-6 PM (afternoon/evening)
- Minimum demand: 3-5 AM (early morning)
- Weekend effect: Slightly lower demand on Sat-Sun
- Total system peak: ~39 GW
- Total system minimum: ~17 GW

### 5. `renewable_profiles_template.csv` - Solar and Wind Availability

Hourly capacity factors for renewable generators (simplified template).

**Columns:**
- `timestamp`: Date and time
- `generator_id`: Renewable generator ID
- `availability_factor`: Available capacity fraction (0.0-1.0)

**Solar Generators (IDs: 10-13, 31-33, 45):**
- Zero availability at night (before 6 AM, after 8 PM)
- Peak availability around noon (~0.95)
- Smooth diurnal curve

**Wind Generators (IDs: 14-16, 34, 37-39):**
- Variable availability (0.05-0.95)
- Higher in afternoon/evening hours
- Site-specific patterns (Wyoming has higher capacity factors)

**Note:** Full renewable profiles can be generated using `generate_renewable_profiles.py`

### 6. `generator_costs.csv` - Operating Costs

Marginal operating costs for each generator.

**Columns:**
- `generator_id`: Generator ID
- `name`: Generator name
- `type`: Technology type
- `fuel_cost_per_mwh`: Fuel cost ($/MWh)
- `vom_cost_per_mwh`: Variable O&M cost ($/MWh)
- `total_marginal_cost_per_mwh`: Total variable cost ($/MWh)

**Typical Marginal Costs:**
- **Solar/Wind**: $0/MWh (zero fuel cost)
- **Hydro**: $2-3/MWh (minimal O&M only)
- **Nuclear**: $10-11/MWh (fuel + O&M)
- **Coal**: $33-34/MWh (fuel + O&M)
- **Gas Combined Cycle**: $43-48/MWh (fuel + O&M)
- **Gas Peakers**: $57-60/MWh (higher fuel costs)
- **Battery Storage**: $1.50/MWh (round-trip efficiency losses)

## Usage

### Loading Data in Python

```python
from data_pipelines.loaders import load_sample_data

# Load all data
network, generators_df, load_profiles_df, renewable_profiles_df, costs_df = load_sample_data()

# Network object contains:
#   - network.nodes: List of Node objects
#   - network.branches: List of Branch objects
#   - network.n: Number of nodes (55)
#   - network.b: Number of branches (90)
#   - network.A_br: Branch incidence matrix

# DataFrames contain:
#   - generators_df: Generator specifications
#   - load_profiles_df: Hourly load data
#   - renewable_profiles_df: Solar/wind availability
#   - costs_df: Operating costs
```

### Data Validation

```python
from data_pipelines.loaders import validate_network_connectivity

# Check network connectivity
nodes, branches = load_nodes(), load_branches()
is_connected = validate_network_connectivity(nodes, branches)
# Returns: True (network is fully connected)
```

### Visualization

```bash
cd data_pipelines/sample_data
python visualize_network.py
```

Generates a geographic map showing:
- Node locations colored by type
- Transmission lines colored by voltage
- Major city labels
- Network statistics

### Export for Optimization

```python
from data_pipelines.loaders.sample_data_loader import export_to_optimization_format

opt_data = export_to_optimization_format(
    network, generators_df, load_profiles_df, costs_df
)

# Returns dictionary with:
#   - network: Network object
#   - T: Number of time periods (168)
#   - load_matrix: (T × n) load array
#   - gen_capacity: Existing generator capacities
#   - gen_costs: Marginal cost vector
#   - And more...
```

## Data Sources and Methodology

### Geographic Accuracy
- Coordinates are based on actual substation and power plant locations
- Network topology reflects real transmission pathways in the Western Interconnection
- Major interstate transmission corridors are represented

### Generation Fleet
- Based on actual facilities in WECC/CAISO regions
- Capacities approximate real installed capacity
- Technology mix reflects current Western grid composition

### Load Profiles
- Derived from CAISO and WECC historical load data
- Summer peak patterns (July)
- Scaled to representative system size

### Costs
- Capital costs from NREL Annual Technology Baseline (ATB) 2024
- Operating costs from EIA and NREL data
- Carbon intensity from EPA eGRID database

### Simplifications
- Reduced network size (55 nodes vs. thousands in real system)
- Simplified DC power flow (no reactive power)
- Single voltage angle representation
- No inter-regional ties (WECC-only)

## Network Statistics

```
Topology:
  Nodes: 55
  Branches: 90
  Average degree: 3.27
  Network diameter: 12 hops

Voltage Levels:
  500 kV: 25 nodes, 46 lines (bulk transmission)
  345 kV: 16 nodes, 24 lines (regional)
  230 kV: 14 nodes, 20 lines (sub-transmission)

Geographic Coverage:
  Latitude range: 32.2°N - 47.9°N
  Longitude range: -124.2°W - -104.6°W
  Coverage area: ~1.2 million km²

Transmission Capacity:
  Total: 131,650 MW
  500 kV lines: 96,550 MW (73%)
  345 kV lines: 26,200 MW (20%)
  230 kV lines: 8,900 MW (7%)

Generation Capacity:
  Total existing: 40,438 MW
  Hydro: 30% (12,183 MW)
  Gas: 21% (8,415 MW)
  Nuclear: 15% (6,177 MW)
  Coal: 13% (5,110 MW)
  Solar: 4% (1,630 MW)
  Wind: 2% (923 MW)

Load Characteristics:
  Peak demand: ~39 GW
  Minimum demand: ~17 GW
  Load factor: 61%
  Number of load centers: 10
```

## Testing Scenarios

This dataset is suitable for testing:

1. **Economic Dispatch**: Unit commitment with realistic costs and constraints
2. **Capacity Expansion**: Optimal siting of new generation and transmission
3. **N-1 Contingency**: Reliability analysis with line outages
4. **Renewable Integration**: High penetration solar/wind scenarios
5. **Energy Storage**: Battery placement and sizing
6. **Carbon Constraints**: Emissions-limited optimization
7. **Multi-period Planning**: Long-term investment decisions

## Files Overview

```
data_pipelines/sample_data/
├── README.md                          # This file
├── nodes.csv                          # 55 nodes
├── branches.csv                       # 90 transmission lines
├── generators.csv                     # 41 generators
├── load_profiles.csv                  # 1,680 load records (168 hrs × 10 nodes)
├── renewable_profiles_template.csv    # Sample renewable availability
├── generator_costs.csv                # Operating costs
├── generate_renewable_profiles.py     # Script to generate full profiles
└── visualize_network.py               # Network visualization tool
```

## Citation

If you use this dataset in research, please cite:

```
Western Interconnection Sample Data for CANOPI Optimization Engine
Generated for capacity expansion and transmission planning research
Based on NREL ATB 2024, WECC topology, and CAISO operational data
```

## License

This sample dataset is provided for research and testing purposes. Cost data is derived from publicly available sources (NREL ATB, EIA). Network topology is representative but simplified.

## Contact

For questions or issues with this dataset, please open an issue in the CANOPI repository.

---

**Last Updated:** January 2026
**Version:** 1.0
**Generated by:** CANOPI Data Pipeline
