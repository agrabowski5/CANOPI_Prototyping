# Getting Started with CANOPI

This guide will help you get the CANOPI Energy Planning Platform up and running in minutes.

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Docker Desktop** (for databases)
- **Gurobi** (optional, for full optimization - trial license available)
- **Mapbox account** (free tier available)

## Quick Start (5 minutes)

### 1. Start Databases

```bash
# Start PostgreSQL, Redis, and TimescaleDB
docker-compose up -d

# Verify they're running
docker-compose ps
```

You should see 3 services running: `canopi_postgres`, `canopi_redis`, `canopi_timescaledb`.

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your Mapbox API key
notepad .env  # Windows
# nano .env  # Linux/Mac
```

**In `.env`, set:**
```
MAPBOX_API_KEY=your_mapbox_token_here
```

Get a free Mapbox token at: https://account.mapbox.com/access-tokens/

### 3. Start Backend Server

```bash
# Still in backend/ directory
python -m app.main
```

The backend should start on http://localhost:8000

**Test it:**
- Open http://localhost:8000/api/docs
- You'll see the interactive API documentation (Swagger UI)
- Try the `GET /api/v1/health` endpoint

### 4. Set Up Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend should automatically open at http://localhost:3000

## What You Should See

### Backend (http://localhost:8000/api/docs)
- Interactive API documentation
- Three main API groups:
  - **Projects**: Create/manage energy projects
  - **Optimization**: Run CANOPI optimization
  - **Grid**: Access network topology and congestion data

### Frontend (http://localhost:3000)
- Interactive map centered on Western US
- Left sidebar: Project list and controls
- Right sidebar: Results dashboard
- Click on map to add projects
- "Run Optimization" button (returns mock results for now)

## Testing the System

### 1. Test Backend APIs

Visit http://localhost:8000/api/docs and try:

**Create a Solar Project:**
```json
POST /api/v1/projects/

{
  "name": "California Solar Farm",
  "type": "solar",
  "capacity_mw": 500,
  "location": {
    "lat": 35.37,
    "lon": -119.02
  },
  "parameters": {
    "capex": 500000000,
    "opex": 5000000,
    "availability_factor": 0.28
  },
  "status": "proposed"
}
```

**Run Mock Optimization:**
```json
POST /api/v1/optimization/run

{
  "parameters": {
    "planning_horizon": {
      "start": 2024,
      "end": 2035
    },
    "carbon_target": 0.80,
    "budget_limit": 50000000000,
    "contingency_level": "n-1",
    "temporal_resolution": "hourly"
  },
  "constraints": {
    "reserve_margin": 0.15,
    "transmission_limit": true,
    "state_policies": []
  }
}
```

This returns a `job_id`. Use it to check status:

```
GET /api/v1/optimization/status/{job_id}
GET /api/v1/optimization/results/{job_id}
```

### 2. Test Frontend

1. **Add a project:**
   - Click anywhere on the map
   - A marker should appear
   - (Full UI implementation may still be in progress)

2. **View sample network:**
   - The map should show the Western Interconnection region
   - Sample transmission lines and nodes

## Sample Data

The system includes realistic sample data in `data_pipelines/sample_data/`:

- **nodes.csv**: 50 substations across Western US
- **branches.csv**: 75 transmission lines
- **generators.csv**: 30 existing power plants
- **load_profiles.csv**: Weekly hourly load data
- **renewable_profiles.csv**: Solar/wind availability

## Running the CANOPI Optimization

The full CANOPI optimization algorithm is implemented in `canopi_engine/algorithms/`. To run it:

```python
from canopi_engine import Network
from canopi_engine.algorithms import BundleMethod
from data_pipelines.loaders import load_sample_network

# Load sample network
network = load_sample_network()

# Run CANOPI optimization
# (Full integration script coming soon)
```

## Troubleshooting

### Backend won't start
- **Port 8000 already in use**: Kill the process using port 8000
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <process_id> /F

  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

- **Database connection error**: Make sure Docker containers are running
  ```bash
  docker-compose up -d
  docker-compose ps
  ```

### Frontend won't start
- **Port 3000 already in use**: The script will offer port 3001
- **Module not found**: Run `npm install` again

### Gurobi license error
- For development, you can use the free academic license
- Or trial license from https://www.gurobi.com/downloads/
- The system will work without Gurobi for basic testing (mock data)

## Next Steps

1. **Explore the API**: Try creating projects and running optimizations
2. **Customize scenarios**: Edit parameters in the optimization request
3. **Add your own data**: Replace sample data with real network topology
4. **Run full CANOPI**: See `examples/run_optimization.py` (coming soon)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                  │
│  - Map Interface (Mapbox)                           │
│  - Project Management                               │
│  - Results Visualization                            │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP REST API
┌──────────────────▼──────────────────────────────────┐
│                 Backend (FastAPI)                    │
│  - API Endpoints                                     │
│  - Business Logic                                    │
│  - Job Queue (Celery)                               │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              CANOPI Engine (Python)                  │
│  - Bundle Method (Algorithm 1)                       │
│  - Transmission Correction (Algorithm 2)             │
│  - Minimal Cycle Basis (Algorithm 3)                │
│  - Operational Subproblem                           │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         Databases (PostgreSQL, Redis, TimescaleDB)   │
└─────────────────────────────────────────────────────┘
```

## Getting Help

- **API Documentation**: http://localhost:8000/api/docs
- **Project README**: [README.md](README.md)
- **Implementation Plan**: `docs/architecture/implementation-plan.md`

## What's Implemented

✅ Backend API framework
✅ Frontend React structure
✅ CANOPI algorithms (Bundle method, RTEP, Cycle basis)
✅ Sample Western Interconnection data
✅ Docker setup for databases
✅ Project management CRUD
✅ Mock optimization endpoints

🔄 **In Progress:**
- Full CANOPI optimization integration
- Real-time WebSocket updates
- Advanced map visualizations
- Data ingestion pipelines

---

**Ready to build the future of energy planning!** 🌍⚡
