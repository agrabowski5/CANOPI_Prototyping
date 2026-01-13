"""
Quick test to verify basic integration
"""

import sys
from pathlib import Path

backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

print("Quick Integration Test")
print("=" * 50)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from data_pipelines.loaders.sample_data_loader import load_complete_optimization_data
    from app.services.canopi.optimizer_service import CANOPIOptimizerService
    print("   Imports: OK")
except Exception as e:
    print(f"   Imports: FAIL - {e}")
    sys.exit(1)

# Test 2: Load data
print("\n2. Loading network data...")
try:
    data = load_complete_optimization_data(time_periods=4)
    print(f"   Network: {data['network'].n} nodes, {data['network'].b} branches")
    print(f"   Generators: {len(data['params'].w_g)}")
    print(f"   Data loading: OK")
except Exception as e:
    print(f"   Data loading: FAIL - {e}")
    sys.exit(1)

# Test 3: Create service
print("\n3. Creating optimizer service...")
try:
    service = CANOPIOptimizerService(time_periods=4)
    print("   Service creation: OK")
except Exception as e:
    print(f"   Service creation: FAIL - {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("All quick tests passed!")
print("\nRun 'python test_integration.py' for full tests")
print("=" * 50)
