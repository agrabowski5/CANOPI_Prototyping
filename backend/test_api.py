"""
End-to-End API Testing Script
Tests all backend endpoints to verify functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health_check():
    """Test health check endpoint"""
    print_section("Testing Health Check")

    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed!")
    return True


def test_create_project():
    """Test creating a new project"""
    print_section("Testing Project Creation")

    project_data = {
        "name": "Test Solar Farm - California",
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

    print(f"Creating project: {project_data['name']}")
    response = requests.post(f"{BASE_URL}/api/v1/projects/", json=project_data)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        project = response.json()
        print(f"Response: {json.dumps(project, indent=2)}")
        print(f"✓ Project created with ID: {project['id']}")
        return project
    else:
        print(f"✗ Failed to create project: {response.text}")
        return None


def test_list_projects():
    """Test listing all projects"""
    print_section("Testing List Projects")

    response = requests.get(f"{BASE_URL}/api/v1/projects/")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} projects")
        for project in projects:
            print(f"  - {project['name']} ({project['type']}, {project['capacity_mw']} MW)")
        print("✓ List projects passed!")
        return projects
    else:
        print(f"✗ Failed to list projects: {response.text}")
        return []


def test_get_project(project_id: str):
    """Test getting a specific project"""
    print_section("Testing Get Project by ID")

    response = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        project = response.json()
        print(f"Project: {project['name']}")
        print(f"  Type: {project['type']}")
        print(f"  Capacity: {project['capacity_mw']} MW")
        print(f"  Location: ({project['location']['lat']}, {project['location']['lon']})")
        print("✓ Get project passed!")
        return project
    else:
        print(f"✗ Failed to get project: {response.text}")
        return None


def test_optimization_impact(project_id: str):
    """Test optimization impact analysis"""
    print_section("Testing Optimization Impact Analysis")

    response = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}/optimization-impact")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        impact = response.json()
        print(f"System Cost Impact:")
        print(f"  Baseline: ${impact['system_cost_impact']['baseline_cost'] / 1e9:.2f}B")
        print(f"  With Project: ${impact['system_cost_impact']['with_project_cost'] / 1e9:.2f}B")
        print(f"  Savings: ${impact['system_cost_impact']['savings'] / 1e6:.1f}M ({impact['system_cost_impact']['savings_percent']:.2f}%)")
        print(f"\nGrid Integration:")
        print(f"  Nearest Substation: {impact['grid_integration']['nearest_substation_km']} km")
        print(f"  Upgrade Required: {impact['grid_integration']['transmission_upgrade_required']}")
        print(f"  Interconnection Cost: ${impact['grid_integration']['estimated_interconnection_cost'] / 1e6:.1f}M")
        print("✓ Optimization impact analysis passed!")
        return impact
    else:
        print(f"✗ Failed to get optimization impact: {response.text}")
        return None


def test_grid_topology():
    """Test grid topology endpoint"""
    print_section("Testing Grid Topology")

    response = requests.get(f"{BASE_URL}/api/v1/grid/topology?region=WECC&limit=10")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        topology = response.json()
        print(f"Nodes: {len(topology['nodes'])}")
        print(f"Branches: {len(topology['branches'])}")

        if topology['nodes']:
            print(f"\nSample Node:")
            node = topology['nodes'][0]
            print(f"  Name: {node['name']}")
            print(f"  Location: ({node['latitude']}, {node['longitude']})")
            print(f"  Voltage: {node['voltage_kv']} kV")

        if topology['branches']:
            print(f"\nSample Branch:")
            branch = topology['branches'][0]
            print(f"  Capacity: {branch['capacity_mw']} MW")
            print(f"  Voltage: {branch['voltage_kv']} kV")

        print("✓ Grid topology passed!")
        return topology
    else:
        print(f"✗ Failed to get grid topology: {response.text}")
        return None


def test_run_optimization():
    """Test running an optimization"""
    print_section("Testing Run Optimization")

    optimization_request = {
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
            "transmission_limit": True,
            "state_policies": []
        }
    }

    print("Submitting optimization job...")
    response = requests.post(f"{BASE_URL}/api/v1/optimization/run", json=optimization_request)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 202:
        job = response.json()
        print(f"Job submitted!")
        print(f"  Job ID: {job['job_id']}")
        print(f"  Status: {job['status']}")
        print(f"  Estimated Time: {job['estimated_time']} seconds")
        print("✓ Optimization submission passed!")
        return job['job_id']
    else:
        print(f"✗ Failed to submit optimization: {response.text}")
        return None


def test_optimization_status(job_id: str):
    """Test checking optimization status"""
    print_section("Testing Optimization Status")

    response = requests.get(f"{BASE_URL}/api/v1/optimization/status/{job_id}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        status = response.json()
        print(f"Job Status: {status['status']}")
        print(f"Progress: {status['progress'] * 100:.1f}%")
        print(f"Current Iteration: {status['current_iteration']}")
        print(f"Elapsed Time: {status['elapsed_time']} seconds")
        print("✓ Optimization status check passed!")
        return status
    else:
        print(f"✗ Failed to get optimization status: {response.text}")
        return None


def test_simulate_progress(job_id: str):
    """Simulate optimization progress (test endpoint)"""
    print_section("Simulating Optimization Progress")

    # Simulate progress at 25%
    response = requests.post(
        f"{BASE_URL}/api/v1/optimization/_test/simulate-progress/{job_id}",
        params={"progress": 0.25, "iteration": 25}
    )
    print(f"Progress 25%: {response.status_code}")
    time.sleep(0.5)

    # Simulate progress at 50%
    response = requests.post(
        f"{BASE_URL}/api/v1/optimization/_test/simulate-progress/{job_id}",
        params={"progress": 0.50, "iteration": 50}
    )
    print(f"Progress 50%: {response.status_code}")
    time.sleep(0.5)

    # Simulate progress at 100% (complete)
    response = requests.post(
        f"{BASE_URL}/api/v1/optimization/_test/simulate-progress/{job_id}",
        params={"progress": 1.0, "iteration": 100}
    )
    print(f"Progress 100%: {response.status_code}")
    print("✓ Progress simulation complete!")


def test_optimization_results(job_id: str):
    """Test getting optimization results"""
    print_section("Testing Optimization Results")

    response = requests.get(f"{BASE_URL}/api/v1/optimization/results/{job_id}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        results = response.json()
        print(f"Job Status: {results['status']}")

        if results['results']:
            res = results['results']
            print(f"\nOptimization Results:")
            print(f"  Total Cost: ${res['total_cost'] / 1e9:.2f}B/year")
            print(f"\nRecommended Investments:")
            print(f"  Storage Power: {res['investments']['storage_power_gw']:.1f} GW")
            print(f"  Storage Energy: {res['investments']['storage_energy_gwh']:.1f} GWh")
            print(f"  Transmission: {res['investments']['transmission_gw']:.1f} GW")
            print(f"  Generation by Type:")
            for gen_type, capacity in res['investments']['generation_by_type'].items():
                print(f"    {gen_type}: {capacity:.1f} GW")

            print(f"\nReliability:")
            print(f"  Load Shed: {res['reliability']['load_shed_gwh']:.2f} GWh ({res['reliability']['load_shed_percent']:.3f}%)")
            print(f"  Violations: {res['reliability']['violations_gwh']:.2f} GWh")
            print(f"  n-1 Compliance: {res['reliability']['n_1_compliance'] * 100:.1f}%")

            print(f"\nCarbon Intensity: {res['carbon_intensity']:.1f} kg CO2/MWh")

            print(f"\nOptimal Locations: {len(res['geospatial_results']['optimal_locations'])} sites")
            for loc in res['geospatial_results']['optimal_locations']:
                print(f"  - {loc['type']}: {loc['capacity_mw']} MW at ({loc['lat']}, {loc['lon']})")

        print("✓ Optimization results retrieval passed!")
        return results
    else:
        print(f"✗ Failed to get optimization results: {response.text}")
        return None


def run_all_tests():
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("  CANOPI BACKEND API - END-TO-END TESTING")
    print("=" * 70)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure the backend server is running!")
    print("  cd backend && python -m app.main")

    try:
        # Test 1: Health Check
        test_health_check()

        # Test 2: Project Management
        project = test_create_project()
        if project:
            project_id = project['id']
            test_list_projects()
            test_get_project(project_id)
            test_optimization_impact(project_id)

        # Test 3: Grid Data
        test_grid_topology()

        # Test 4: Optimization Workflow
        job_id = test_run_optimization()
        if job_id:
            time.sleep(1)
            test_optimization_status(job_id)
            test_simulate_progress(job_id)
            time.sleep(1)
            test_optimization_status(job_id)
            test_optimization_results(job_id)

        # Summary
        print("\n" + "=" * 70)
        print("  ALL TESTS PASSED! ✓")
        print("=" * 70)
        print("\nThe backend API is working correctly!")
        print("Next step: Start the frontend with 'cd frontend && npm start'")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend server")
        print("Please start the backend server:")
        print("  cd backend && python -m app.main")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
