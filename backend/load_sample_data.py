"""
Load sample grid data from CSV files into JSON format for the backend

This script converts CSV sample data into JSON files that the backend can load.
Run this once to initialize the grid topology data.
"""
import sys
from pathlib import Path
import json

def load_csv_to_json():
    """Load CSV files and convert to JSON format"""

    project_root = Path(__file__).parent.parent
    sample_data_dir = project_root / "data_pipelines" / "sample_data"
    grid_data_dir = project_root / "data_pipelines" / "grid_data"

    # Check if sample data exists
    if not sample_data_dir.exists():
        print(f"❌ Sample data directory not found: {sample_data_dir}")
        return 0, 0

    nodes_csv = sample_data_dir / "nodes.csv"
    branches_csv = sample_data_dir / "branches.csv"

    if not nodes_csv.exists():
        print(f"❌ nodes.csv not found: {nodes_csv}")
        return 0, 0

    if not branches_csv.exists():
        print(f"❌ branches.csv not found: {branches_csv}")
        return 0, 0

    # Create grid_data directory if it doesn't exist
    grid_data_dir.mkdir(parents=True, exist_ok=True)

    # Try to use pandas, fallback to csv module
    try:
        import pandas as pd
        use_pandas = True
    except ImportError:
        import csv
        use_pandas = False
        print("⚠ pandas not found, using csv module (slower)")

    # Load nodes
    print(f"📊 Loading {nodes_csv}...")
    nodes_json = []

    if use_pandas:
        import pandas as pd
        nodes_df = pd.read_csv(nodes_csv)

        for _, row in nodes_df.iterrows():
            nodes_json.append({
                "id": str(row["node_id"]),
                "name": str(row["name"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "voltage_kv": float(row["voltage_kv"]),
                "type": str(row["type"]),
                "iso_rto": str(row.get("iso_rto", "Unknown"))
            })
    else:
        import csv
        with open(nodes_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nodes_json.append({
                    "id": str(row["node_id"]),
                    "name": str(row["name"]),
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "voltage_kv": float(row["voltage_kv"]),
                    "type": str(row["type"]),
                    "iso_rto": str(row.get("iso_rto", "Unknown"))
                })

    # Save nodes to JSON
    output_file = grid_data_dir / "sample_nodes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(nodes_json, f, indent=2)
    print(f"✅ Saved {len(nodes_json)} nodes to {output_file}")

    # Load branches
    print(f"📊 Loading {branches_csv}...")
    branches_json = []

    if use_pandas:
        branches_df = pd.read_csv(branches_csv)

        for _, row in branches_df.iterrows():
            branches_json.append({
                "id": str(row["branch_id"]),
                "from_node_id": str(row["from_node"]),
                "to_node_id": str(row["to_node"]),
                "capacity_mw": float(row["capacity_mw"]),
                "voltage_kv": float(row["voltage_kv"]),
                "length_km": float(row.get("length_km", 100)),
                "reactance": float(row.get("reactance", 0.01))
            })
    else:
        with open(branches_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                branches_json.append({
                    "id": str(row["branch_id"]),
                    "from_node_id": str(row["from_node"]),
                    "to_node_id": str(row["to_node"]),
                    "capacity_mw": float(row["capacity_mw"]),
                    "voltage_kv": float(row["voltage_kv"]),
                    "length_km": float(row.get("length_km", 100)),
                    "reactance": float(row.get("reactance", 0.01))
                })

    # Save branches to JSON
    output_file = grid_data_dir / "sample_branches.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(branches_json, f, indent=2)
    print(f"✅ Saved {len(branches_json)} branches to {output_file}")

    print("\n" + "="*60)
    print("✅ Sample data converted to JSON successfully!")
    print("="*60)
    print(f"\nFiles created in: {grid_data_dir}")
    print(f"  - sample_nodes.json ({len(nodes_json)} nodes)")
    print(f"  - sample_branches.json ({len(branches_json)} branches)")

    return len(nodes_json), len(branches_json)

if __name__ == "__main__":
    print("="*60)
    print("CANOPI Sample Data Loader")
    print("="*60)
    print()

    try:
        nodes_count, branches_count = load_csv_to_json()

        if nodes_count > 0:
            print("\n" + "="*60)
            print("📍 Next steps:")
            print("="*60)
            print("\n1. Start/restart the backend:")
            print("   cd backend")
            print("   uvicorn app.main:app --reload")
            print("\n2. Check logs - you should see:")
            print("   '✓ Grid service initialized with X nodes and Y branches'")
            print("\n3. Start the frontend:")
            print("   cd frontend")
            print("   npm start")
            print("\n4. Open http://localhost:3000")
            print("   Map should now show grid topology!")
            print("\n" + "="*60)
        else:
            print("\n❌ No data was loaded. Check that CSV files exist:")
            print("   - data_pipelines/sample_data/nodes.csv")
            print("   - data_pipelines/sample_data/branches.csv")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
