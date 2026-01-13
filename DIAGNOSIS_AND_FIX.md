# CANOPI Map & Optimization Issue - Diagnosis and Fix

## 🔍 Problem

You're experiencing two issues:
1. **Empty map** - No grid topology or transmission lines showing
2. **Optimization not working** - Can't run optimizations

## 🎯 Root Causes

### Issue 1: Empty Map

**What's happening:**
- Frontend loads and calls `/api/v1/grid/topology` and `/api/v1/transmission/lines/geojson`
- Backend endpoints exist and work correctly
- **BUT**: The backend has no data loaded into memory

**Why:**
1. Sample data files exist in `data_pipelines/` directory
2. Backend `InMemoryGridDataService` exists but isn't initialized with data
3. The `startup_event()` in `main.py` has `TODO: Load network topology data` but doesn't actually load it

**Where the data is:**
```
CANOPI_Prototyping/
├── data_pipelines/
│   ├── sample_data/
│   │   ├── nodes.csv (55 substations)
│   │   ├── branches.csv (75 transmission lines)
│   │   └── generators.csv (30 power plants)
│   ├── grid_data/ (JSON files)
│   │   ├── western_interconnection_nodes.json
│   │   ├── western_interconnection_branches.json
│   │   └── [more interconnection files]
│   └── transmission_data/
│       └── [GeoJSON transmission line files]
```

---

### Issue 2: Optimization Not Working

**What's happening:**
- Optimization endpoints exist
- Frontend calls `/api/v1/optimization/quick`
- Backend tries to use CANOPI optimizer
- **BUT**: Falls back to mock data if optimizer fails

**Why:**
1. CANOPI optimizer requires Gurobi solver (commercial license required)
2. If Gurobi not installed or licensed, optimization silently fails
3. Backend returns mock results instead of real optimization

---

## 💡 Solutions

There are **3 levels** of fixes, from quick to comprehensive:

---

## ⚡ Solution 1: Quick Fix (15 minutes)

### Fix the backend to load sample data on startup

**Step 1: Update main.py to load grid data**

Edit `backend/app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("Starting CANOPI Energy Planning Platform API")

    # Initialize grid data service with sample data
    try:
        from app.services.grid_data_memory import get_grid_service
        grid_service = get_grid_service()
        logger.info(f"Grid service initialized with {len(grid_service.nodes)} nodes and {len(grid_service.branches)} branches")

        if len(grid_service.nodes) == 0:
            logger.warning("No grid data loaded - map will be empty")
        else:
            logger.info(f"Sample coverage: {len(grid_service.nodes)} substations across North America")
    except Exception as e:
        logger.error(f"Failed to initialize grid service: {e}")
```

**Step 2: Verify JSON data files exist**

Check these files exist:
```bash
cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping\data_pipelines\grid_data

# Should see:
# western_interconnection_nodes.json
# western_interconnection_branches.json
# eastern_interconnection_nodes.json
# ... etc
```

**Step 3: Restart backend**

```bash
cd backend
uvicorn app.main:app --reload
```

**Check the output** - you should see:
```
INFO:     Starting CANOPI Energy Planning Platform API
INFO:     Grid service initialized with XXX nodes and YYY branches
```

If you see "0 nodes", the JSON files aren't being found.

---

## 🔧 Solution 2: Load Sample CSV Data (30 minutes)

If the JSON files don't exist or are empty, load from CSV:

**Create a data loader script:**

File: `backend/load_sample_data.py`

```python
"""
Load sample grid data from CSV files into the backend
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.grid_data_memory import InMemoryGridDataService
import pandas as pd
import json

def load_csv_to_json():
    """Load CSV files and convert to JSON format"""

    project_root = Path(__file__).parent.parent
    sample_data_dir = project_root / "data_pipelines" / "sample_data"
    grid_data_dir = project_root / "data_pipelines" / "grid_data"

    grid_data_dir.mkdir(parents=True, exist_ok=True)

    # Load nodes
    print("Loading nodes.csv...")
    nodes_df = pd.read_csv(sample_data_dir / "nodes.csv")

    nodes_json = []
    for _, row in nodes_df.iterrows():
        nodes_json.append({
            "id": str(row["node_id"]),
            "name": row["name"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "voltage_kv": float(row["voltage_kv"]),
            "type": row["type"],
            "iso_rto": row.get("iso_rto", "Unknown")
        })

    # Save to JSON
    output_file = grid_data_dir / "sample_nodes.json"
    with open(output_file, 'w') as f:
        json.dump(nodes_json, f, indent=2)
    print(f"Saved {len(nodes_json)} nodes to {output_file}")

    # Load branches
    print("Loading branches.csv...")
    branches_df = pd.read_csv(sample_data_dir / "branches.csv")

    branches_json = []
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

    # Save to JSON
    output_file = grid_data_dir / "sample_branches.json"
    with open(output_file, 'w') as f:
        json.dump(branches_json, f, indent=2)
    print(f"Saved {len(branches_json)} branches to {output_file}")

    print("\n✅ Sample data converted to JSON!")
    print(f"Files created in: {grid_data_dir}")

    return len(nodes_json), len(branches_json)

if __name__ == "__main__":
    nodes_count, branches_count = load_csv_to_json()
    print(f"\nLoaded {nodes_count} nodes and {branches_count} branches")
    print("\nNext steps:")
    print("1. Restart the backend: uvicorn app.main:app --reload")
    print("2. Check logs for 'Grid service initialized with X nodes'")
    print("3. Open frontend and map should show grid topology")
```

**Run the loader:**

```bash
cd backend
python load_sample_data.py
```

**Then update `grid_data_memory.py` to load these files:**

In `backend/app/services/grid_data_memory.py`, modify the `get_grid_service()` function to also check for `sample_nodes.json` and `sample_branches.json`.

---

## 🚀 Solution 3: Full Database Integration (2 hours)

For production-ready setup with PostgreSQL:

**Step 1: Set up database**

```bash
cd backend

# Create database
createdb canopi

# Run migrations
alembic upgrade head
```

**Step 2: Create database models**

File: `backend/app/models/grid.py`

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GridNode(Base):
    __tablename__ = "grid_nodes"

    id = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    voltage_kv = Column(Float)
    type = Column(String)
    iso_rto = Column(String)

class GridBranch(Base):
    __tablename__ = "grid_branches"

    id = Column(String, primary_key=True)
    from_node_id = Column(String, ForeignKey("grid_nodes.id"))
    to_node_id = Column(String, ForeignKey("grid_nodes.id"))
    capacity_mw = Column(Float)
    voltage_kv = Column(Float)
    length_km = Column(Float)
    reactance = Column(Float)
```

**Step 3: Load data into database**

Create migration or seed script to load CSV → PostgreSQL.

---

## 🎯 Recommended Approach

**For immediate results (today):**
- ✅ Use **Solution 1** (Quick Fix)
- Just add grid service initialization to startup event
- Backend should load existing JSON files

**If map still empty:**
- ✅ Use **Solution 2** (Load CSV Data)
- Convert CSV to JSON format
- Restart backend

**For production:**
- ✅ Use **Solution 3** (Database Integration)
- Proper PostgreSQL setup
- Scalable data loading

---

## 🔍 Debugging Steps

### Check if backend is running:

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### Check grid data endpoint:

```bash
curl http://localhost:8000/api/v1/grid/topology
```

Should return JSON with `nodes` and `branches` arrays.

If empty: `{"nodes": [], "branches": []}`
If working: `{"nodes": [{...}, {...}], "branches": [{...}]}`

### Check transmission data:

```bash
curl "http://localhost:8000/api/v1/transmission/lines/geojson?limit=10"
```

Should return GeoJSON FeatureCollection.

### Check backend logs:

Look for these messages:
```
INFO:     Starting CANOPI Energy Planning Platform API
INFO:     Grid service initialized with XXX nodes and YYY branches
```

If you see warnings about missing files, that's the issue.

---

## 🛠️ Optimization Fix

For the optimization issue:

### Option A: Use Mock Data (Quick)

The backend already falls back to mock data, which is fine for testing the UI.

**Current behavior:**
- Frontend calls `/api/v1/optimization/quick`
- Backend tries real CANOPI optimizer
- If it fails (Gurobi not available), returns mock results
- Frontend shows "optimization completed" with fake data

**This is OK for development!** You can test the UI flow even without real optimization.

### Option B: Install Gurobi (For Real Optimization)

**Requirements:**
- Gurobi Optimizer (free academic license or commercial)
- Python gurobipy package

**Steps:**
1. Get Gurobi license: https://www.gurobi.com/downloads/
2. Install: `pip install gurobipy`
3. Set license: `grbgetkey YOUR_LICENSE_KEY`
4. Restart backend

### Option C: Use Open-Source Solver

Replace Gurobi with open-source alternative (HiGHS, GLPK):

```python
# In canopi_engine, replace Gurobi with:
import highspy
# or
from scipy.optimize import linprog
```

This requires modifying the CANOPI optimization code.

---

## ✅ Verification Checklist

After applying fixes:

- [ ] Backend starts without errors
- [ ] Logs show "Grid service initialized with X nodes"
- [ ] `/api/v1/grid/topology` returns non-empty data
- [ ] `/api/v1/transmission/lines/geojson` returns GeoJSON
- [ ] Frontend map shows grid topology (colored dots)
- [ ] Frontend map shows transmission lines
- [ ] Can create a project and see it on map
- [ ] Can click "Run Optimization" button
- [ ] Optimization shows progress/results (even if mock)

---

## 📝 Quick Start Commands

```bash
# 1. Check if backend is running
curl http://localhost:8000/health

# 2. If not running, start it
cd backend
uvicorn app.main:app --reload

# 3. Check grid data
curl http://localhost:8000/api/v1/grid/topology

# 4. If empty, load sample data
cd backend
python load_sample_data.py  # (create this file first)

# 5. Restart backend
# Press Ctrl+C, then:
uvicorn app.main:app --reload

# 6. Start frontend
cd ../frontend
npm start

# 7. Open browser
# http://localhost:3000
```

---

## 🎯 Expected Result

After fixing, you should see:

**Map:**
- 🟢 Green dots = Substations
- 🔵 Blue dots = Generators
- 🔴 Red dots = Load centers
- Gray lines = Transmission lines (500kV, 345kV, etc.)
- Zoom in/out to see more detail

**Optimization:**
- Click "+ New Project" to add solar/wind project
- Click "Optimization" panel
- Click "Run Quick Optimization"
- See progress bar
- See results (cost, generation, etc.)

Even with mock optimization, the UI should work!

---

## 💬 Still Having Issues?

**Common problems:**

1. **"Connection refused" or "Network error"**
   - Backend not running
   - Solution: Start backend with `uvicorn app.main:app --reload`

2. **"404 Not Found" errors**
   - Already fixed! (API paths corrected)
   - If still seeing, clear browser cache

3. **Empty map but no errors**
   - Backend has no data
   - Solution: Load sample data (Solution 2)

4. **Optimization button disabled**
   - Need at least one project
   - Solution: Click "+ New Project" first

5. **Optimization fails immediately**
   - Optimizer not available
   - Solution: Use mock data (already enabled)

---

## 📞 Next Steps

**Right now (5 minutes):**
1. Check if backend is running: `curl http://localhost:8000/health`
2. If not, start it: `cd backend && uvicorn app.main:app --reload`
3. Check what you see in terminal - any errors?
4. Try opening frontend: http://localhost:3000

**Tell me:**
- Is the backend running?
- What do you see in the backend terminal?
- What errors (if any) in the browser console?

I'll help you get this working! 🚀

---

**Last Updated:** January 13, 2026
