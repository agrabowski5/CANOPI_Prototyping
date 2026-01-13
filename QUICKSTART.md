# CANOPI Integration - Quick Start Guide

Get the CANOPI optimization running in 5 minutes!

## Prerequisites

- Python 3.8+
- Redis (optional, for background tasks)
- Gurobi license (for optimization)

## Option 1: Quick Test (No Redis Required)

Test the integration without Celery/Redis:

```bash
# Navigate to backend
cd backend

# Run quick test
python quick_test.py

# Run full integration test
python test_integration.py
```

**Expected Output:**
```
[Test 1] Loading network data... PASS
[Test 2] Testing optimizer service... PASS
[Test 3] Testing API result format... PASS
[Test 4] Testing worker logic... PASS
[Test 5] Verifying data consistency... PASS

All core tests passed!
```

## Option 2: Full System with API

Run the complete system with FastAPI and Celery:

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A app.workers.optimization_worker worker --loglevel=info
```

**Terminal 3 - FastAPI:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 3: Test API

Open browser: http://localhost:8000/api/docs

Or use curl:
```bash
# Submit optimization
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

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "estimated_time": 360,
  "created_at": "2024-01-09T12:00:00Z"
}
```

**Check Status:**
```bash
curl "http://localhost:8000/api/v1/optimization/status/{job_id}"
```

**Get Results:**
```bash
curl "http://localhost:8000/api/v1/optimization/results/{job_id}"
```

## Option 3: Python Script

```python
# test_optimization.py
from app.services.canopi.optimizer_service import (
    CANOPIOptimizerService,
    OptimizationRequest
)

# Create service
service = CANOPIOptimizerService(time_periods=12)

# Create request
request = OptimizationRequest(
    planning_horizon_start=2024,
    planning_horizon_end=2030,
    carbon_target=0.8,
    budget_limit=50e9,
    contingency_level="n-1",
    temporal_resolution="hourly"
)

# Run optimization
print("Running optimization...")
result = service.run_optimization(
    request=request,
    simplified=True  # Fast mode
)

# Print results
print(f"\nResults:")
print(f"  Total cost: ${result.total_cost/1e9:.2f}B")
print(f"  Generation: {result.capacity_decision.total_generation_gw:.1f} GW")
print(f"  Transmission: {result.capacity_decision.total_transmission_gw:.1f} GW")
print(f"  Time: {result.computation_time:.1f}s")
```

Run it:
```bash
cd backend
python test_optimization.py
```

## Troubleshooting

### Issue: Import errors
```bash
# Add to script:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Issue: Redis not running
```bash
# Check Redis:
redis-cli ping
# Should return: PONG

# If not installed:
# Mac: brew install redis
# Linux: sudo apt-get install redis-server
# Windows: Use WSL or Docker
```

### Issue: Celery worker not starting
```bash
# Check worker status:
celery -A app.workers.optimization_worker inspect active

# Restart worker:
celery -A app.workers.optimization_worker worker --loglevel=debug
```

## What's Next?

1. ✅ Tests passing? Great! You're ready to go.
2. Read `INTEGRATION_README.md` for detailed docs
3. Read `INTEGRATION_SUMMARY.md` for architecture overview
4. Explore the API at http://localhost:8000/api/docs

## File Locations

- **Data Loader:** `data_pipelines/loaders/sample_data_loader.py`
- **Optimizer Service:** `backend/app/services/canopi/optimizer_service.py`
- **Celery Worker:** `backend/app/workers/optimization_worker.py`
- **API Endpoints:** `backend/app/api/v1/optimization.py`
- **Tests:** `backend/test_integration.py`

## Need Help?

- Check test output: `python test_integration.py`
- Review logs: Celery worker terminal
- Check API docs: http://localhost:8000/api/docs
- Read full docs: `INTEGRATION_README.md`

---

**Status:** ✅ Ready to use!
**Estimated Setup Time:** 5-10 minutes
**First Optimization Run:** < 1 minute (simplified mode)
