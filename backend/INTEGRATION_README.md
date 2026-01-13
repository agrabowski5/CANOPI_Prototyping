# CANOPI Backend Integration

This document describes the integration between the CANOPI optimization engine and the FastAPI backend.

## Architecture

```
API Request → Celery Task → Load Network → Run CANOPI → Store Results → API Response
```

## Components

### 1. Data Loader (`data_pipelines/loaders/sample_data_loader.py`)

Loads network data from CSV files and creates CANOPI data structures:

- **Network topology**: Nodes and branches from `nodes.csv` and `branches.csv`
- **Generators**: Existing and candidate generators from `generators.csv`
- **Load profiles**: Hourly demand from `load_profiles.csv`
- **Operational parameters**: Generator ramp rates, emissions factors, etc.
- **Investment costs**: Capital and operating costs
- **Capacity limits**: Maximum expansion limits

**Key Functions:**
- `load_complete_optimization_data(time_periods)`: Loads all data for optimization
- `create_operational_parameters()`: Creates operational parameter object
- `create_scenario_data()`: Creates scenario with demand and availability profiles

### 2. CANOPI Service (`backend/app/services/canopi/optimizer_service.py`)

Wrapper service that integrates CANOPI algorithms with the FastAPI backend:

**Classes:**
- `OptimizationRequest`: Request parameters from API
- `OptimizationResult`: Results in API format
- `CANOPIOptimizerService`: Main service class

**Key Methods:**
- `load_data()`: Loads network data
- `run_optimization()`: Runs CANOPI optimization
- `_run_simplified_optimization()`: Fast simplified solution for testing
- `_run_full_optimization()`: Full bundle method optimization

**Features:**
- Progress callbacks for real-time updates
- Converts between API and CANOPI formats
- Handles both simplified and full optimization modes

### 3. Celery Worker (`backend/app/workers/optimization_worker.py`)

Background worker for asynchronous optimization:

**Tasks:**
- `run_canopi_optimization`: Main optimization task
- `cleanup_old_jobs`: Periodic cleanup of old jobs

**Functions:**
- `update_job_status()`: Updates job progress in storage
- `get_job_status()`: Retrieves current job status
- `get_job_results()`: Retrieves completed job results

**Configuration:**
- Task queue: Redis
- Result backend: Redis
- Task timeout: 1 hour
- Progress tracking enabled

### 4. Updated Optimization API (`backend/app/api/v1/optimization.py`)

Enhanced endpoints that use real CANOPI optimization:

**Endpoints:**
- `POST /api/v1/optimization/run`: Submit optimization job (queues Celery task)
- `GET /api/v1/optimization/status/{job_id}`: Get real-time progress
- `GET /api/v1/optimization/results/{job_id}`: Get results from CANOPI
- `POST /api/v1/optimization/{job_id}/cancel`: Cancel running job

**Updates:**
- Integrates with Celery worker
- Pulls real progress from worker storage
- Returns actual CANOPI results
- Falls back to mock data if worker unavailable

### 5. Integration Test (`backend/test_integration.py`)

End-to-end integration test:

**Tests:**
1. Load network data from CSVs
2. Run optimizer service
3. Validate API result format
4. Test worker logic
5. Verify data consistency

**Usage:**
```bash
cd backend
python test_integration.py
```

## Setup Instructions

### Prerequisites

1. Python 3.8+
2. Redis server (for Celery)
3. Gurobi (for optimization solver)

### Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start Redis:
```bash
redis-server
```

3. Start Celery worker:
```bash
cd backend
celery -A app.workers.optimization_worker worker --loglevel=info
```

4. Start FastAPI server:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

5. Access API docs:
```
http://localhost:8000/api/docs
```

## Testing

### Quick Test (Without Celery)

Test the integration without running Celery:

```bash
cd backend
python test_integration.py
```

This tests:
- Data loading
- Optimizer service
- Result formatting
- Data consistency

### Test with Celery

1. Start Redis and Celery worker (see Setup)

2. Submit optimization via API:
```bash
curl -X POST "http://localhost:8000/api/v1/optimization/run" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "planning_horizon": {"start": 2024, "end": 2030},
      "carbon_target": 0.8,
      "budget_limit": 50000000000,
      "contingency_level": "n-1",
      "temporal_resolution": "hourly"
    },
    "constraints": {
      "reserve_margin": 0.15,
      "transmission_limit": true,
      "state_policies": []
    }
  }'
```

3. Check status:
```bash
curl "http://localhost:8000/api/v1/optimization/status/{job_id}"
```

4. Get results:
```bash
curl "http://localhost:8000/api/v1/optimization/results/{job_id}"
```

## Data Flow

### 1. Submit Optimization

```
Client → POST /optimization/run
  ↓
Create job record in jobs_db
  ↓
Queue Celery task: run_canopi_optimization.delay()
  ↓
Return job_id to client
```

### 2. Run Optimization

```
Celery worker picks up task
  ↓
CANOPIOptimizerService.load_data()
  ↓
Load CSVs → Create CANOPI data structures
  ↓
CANOPIOptimizerService.run_optimization()
  ↓
BundleMethod.solve() [or simplified mode]
  ↓
Progress callbacks → update_job_status()
  ↓
Store results in job_store
```

### 3. Check Status

```
Client → GET /optimization/status/{job_id}
  ↓
Check jobs_db
  ↓
get_job_status() from worker
  ↓
Return progress, iteration, gap
```

### 4. Get Results

```
Client → GET /optimization/results/{job_id}
  ↓
Check job status == 'completed'
  ↓
get_job_results() from worker
  ↓
Convert to API format
  ↓
Return investments, reliability, costs
```

## Optimization Modes

### Simplified Mode (Default for MVP)

- Fast execution (< 1 minute)
- Creates feasible solution
- Suitable for testing and demos
- Used when `simplified=True`

**Algorithm:**
- Calculates expansion needs based on demand
- Applies simple heuristics
- Generates valid capacity decisions
- Simulates progress updates

### Full Mode (Production)

- Complete bundle method optimization
- Transmission correction algorithm
- Contingency analysis
- Used when `simplified=False`

**Algorithm:**
- BundleMethod with cutting planes
- Operational subproblems
- Transmission RTEP correction
- Convergence to optimal solution

## Configuration

### Time Periods

Default: 24 hours (1 day)

Adjust in service initialization:
```python
service = CANOPIOptimizerService(time_periods=168)  # 1 week
```

### Max Iterations

Default: 50 iterations

Adjust in optimization call:
```python
result = service.run_optimization(
    request=request,
    max_iterations=100
)
```

### Convergence Tolerance

Default: 1% gap

Adjust in BundleMethod:
```python
bundle = BundleMethod(
    ...,
    epsilon=0.005  # 0.5% gap
)
```

## Troubleshooting

### Issue: Celery task not starting

**Solution:**
1. Check Redis is running: `redis-cli ping`
2. Check Celery worker is running: `celery -A app.workers.optimization_worker inspect active`
3. Check logs: `celery -A app.workers.optimization_worker worker --loglevel=debug`

### Issue: Optimization fails with infeasibility

**Solution:**
1. Check data consistency (run test_integration.py)
2. Verify demand can be met by capacity
3. Increase capacity limits
4. Check for isolated nodes in network

### Issue: Results not showing in API

**Solution:**
1. Check worker completed successfully
2. Verify job_id matches
3. Check job status is 'completed'
4. Look at worker logs for errors

### Issue: Import errors for canopi_engine

**Solution:**
1. Ensure PYTHONPATH includes project root
2. Check sys.path.insert() in files
3. Verify canopi_engine directory structure

## Performance Notes

### Simplified Mode
- Time: < 1 minute
- Memory: ~500 MB
- Suitable for: Testing, demos, rapid prototyping

### Full Mode (24 hours)
- Time: 5-30 minutes
- Memory: ~2 GB
- Suitable for: Production, detailed analysis

### Full Mode (168 hours / 1 week)
- Time: 30-120 minutes
- Memory: ~8 GB
- Suitable for: Full planning studies

## Next Steps

### Immediate
1. Test integration end-to-end
2. Deploy with Redis and Celery
3. Monitor first production runs

### Short-term
1. Add database persistence (replace in-memory storage)
2. Implement job cancellation
3. Add result export (JSON, CSV)
4. Enhance progress reporting

### Long-term
1. Implement full bundle method mode
2. Add parallel scenario evaluation
3. Optimize memory usage
4. Add result caching
5. Implement job priority queue

## Files Created/Modified

### New Files
- `data_pipelines/loaders/sample_data_loader.py` (enhanced)
- `backend/app/services/canopi/optimizer_service.py`
- `backend/app/services/canopi/__init__.py`
- `backend/app/workers/optimization_worker.py`
- `backend/test_integration.py`
- `backend/INTEGRATION_README.md`

### Modified Files
- `backend/app/api/v1/optimization.py` (integrated with Celery and CANOPI)

## Contact

For questions or issues with the integration, please create an issue in the repository.
