# CANOPI Testing Guide

This guide covers all testing approaches for the CANOPI Energy Planning Platform.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Frontend Testing](#frontend-testing)
3. [Backend Testing](#backend-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [CI/CD Testing](#cicd-testing)
7. [Test Coverage](#test-coverage)

---

## Quick Start

### Run All Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# Watch mode (frontend)
npm test -- --watch
```

---

## Frontend Testing

The frontend uses **Jest** and **React Testing Library** for unit and integration tests.

### Test Structure

```
frontend/src/
├── services/
│   ├── __tests__/
│   │   ├── projectsService.test.ts
│   │   ├── gridService.test.ts
│   │   ├── transmissionService.test.ts
│   │   └── optimizationService.test.ts
│   └── ...
├── components/
│   └── __tests__/
│       └── ...
└── ...
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- projectsService.test.ts

# Update snapshots
npm test -- -u
```

### Writing Frontend Tests

Example service test:

```typescript
import { projectsService } from '../projectsService';
import { apiClient } from '../api';

jest.mock('../api');

describe('projectsService', () => {
  it('should fetch projects', async () => {
    const mockData = [{ id: '1', name: 'Test Project' }];
    (apiClient.get as jest.Mock).mockResolvedValue({ data: mockData });

    const projects = await projectsService.getProjects();

    expect(projects).toEqual(mockData);
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/', { params: undefined });
  });
});
```

### Frontend Test Categories

1. **Service Tests** (`services/__tests__/`)
   - API client mocking
   - Request/response transformation
   - Error handling

2. **Component Tests** (`components/__tests__/`)
   - Rendering tests
   - User interaction tests
   - Props validation
   - State management

3. **Integration Tests**
   - Component + service integration
   - Redux store interactions
   - Routing tests

---

## Backend Testing

The backend uses **pytest** with async support for testing FastAPI endpoints.

### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures and configuration
│   ├── test_projects_api.py     # Projects endpoint tests
│   ├── test_grid_api.py         # Grid data endpoint tests
│   ├── test_optimization_api.py # Optimization endpoint tests
│   └── ...
├── pytest.ini                   # Pytest configuration
└── ...
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_projects_api.py

# Run specific test class
pytest tests/test_projects_api.py::TestProjectsAPI

# Run specific test
pytest tests/test_projects_api.py::TestProjectsAPI::test_create_project

# Run with markers
pytest -m "unit"
pytest -m "integration"
pytest -m "api"

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Writing Backend Tests

Example API test:

```python
import pytest
from fastapi.testclient import TestClient

def test_create_project(client: TestClient, sample_project_data):
    """Test creating a new project"""
    response = client.post("/api/v1/projects/", json=sample_project_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert "id" in data
```

### Fixtures Available

Defined in `conftest.py`:

- `client`: FastAPI TestClient with database override
- `db_session`: Fresh database session for each test
- `sample_project_data`: Sample project data
- `sample_grid_node_data`: Sample grid node data
- `sample_optimization_config`: Sample optimization config

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_transform_data():
    """Unit test"""
    pass

@pytest.mark.integration
def test_database_query():
    """Integration test"""
    pass

@pytest.mark.slow
def test_optimization():
    """Slow test"""
    pass
```

Run tests by marker:
```bash
pytest -m "unit and not slow"
```

---

## Integration Testing

### API Integration Tests

The backend includes comprehensive integration tests in `test_integration.py`:

```bash
cd backend
python test_integration.py
```

This tests:
- Project CRUD operations
- Grid topology retrieval
- Optimization job workflow
- WebSocket connections
- Database transactions

### Manual API Testing

Use the interactive API docs:

1. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Open browser to: `http://localhost:8000/api/docs`

3. Test endpoints interactively

### Quick Integration Test

```bash
cd backend
python quick_test.py
```

This verifies:
- Backend is running
- Database is connected
- All endpoints are accessible
- Data can be created and retrieved

---

## End-to-End Testing

### Manual E2E Test Workflow

1. **Start Services**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

2. **Test User Workflow**
   - Navigate to `http://localhost:3000`
   - Create a new project (solar/wind)
   - Drag project on map
   - View grid topology
   - Run optimization
   - View results

3. **Verify API Calls**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Verify all API calls return 200 status
   - Check response payloads

### E2E Test Script

Run the comprehensive end-to-end test:

```bash
cd backend
python test_api.py
```

This tests:
1. Health check
2. Project creation
3. Project listing
4. Grid topology retrieval
5. Optimization workflow
6. Results retrieval

---

## CI/CD Testing

### GitHub Actions Workflow

Tests run automatically on:
- Push to `main` branch
- Pull requests
- Manual workflow dispatch

See `.github/workflows/claude-code.yml` for CI configuration.

### Local CI Simulation

Run the same checks as CI locally:

```bash
# Backend checks
cd backend
pytest --cov=app --cov-report=xml
black --check .
flake8 .
mypy .

# Frontend checks
cd frontend
npm test -- --coverage --watchAll=false
npm run lint
npm run build
```

---

## Test Coverage

### View Coverage Reports

**Frontend:**
```bash
cd frontend
npm test -- --coverage
# Open coverage/lcov-report/index.html
```

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Critical paths covered
- **API Tests**: All endpoints tested
- **E2E Tests**: Main user workflows

### Current Coverage

Check coverage with:
```bash
# Frontend
npm test -- --coverage --watchAll=false

# Backend
pytest --cov=app --cov-report=term-missing
```

---

## Testing Best Practices

### 1. Test Naming

Use descriptive names:
```python
# Good
def test_create_project_with_valid_data():
    pass

# Bad
def test1():
    pass
```

### 2. Test Independence

Each test should be independent:
```python
# Good
def test_feature_a(client):
    response = client.get("/endpoint")
    assert response.status_code == 200

# Bad - depends on test execution order
def test_feature_b():
    # Assumes data from test_feature_a exists
    pass
```

### 3. Use Fixtures

Reuse setup code with fixtures:
```python
@pytest.fixture
def sample_data():
    return {"name": "Test", "value": 123}

def test_with_fixture(sample_data):
    assert sample_data["name"] == "Test"
```

### 4. Mock External Dependencies

Always mock external APIs, databases, etc.:
```typescript
jest.mock('../api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));
```

### 5. Test Error Cases

Don't just test happy paths:
```python
def test_create_project_invalid_data(client):
    response = client.post("/api/v1/projects/", json={})
    assert response.status_code == 422
```

---

## Troubleshooting

### Frontend Tests Failing

**Issue**: "Cannot find module"
```bash
# Clear cache
npm test -- --clearCache
```

**Issue**: Tests timing out
```javascript
// Increase timeout
jest.setTimeout(10000);
```

### Backend Tests Failing

**Issue**: Database connection errors
```bash
# Use in-memory SQLite (default in conftest.py)
# Or set test database URL
export DATABASE_URL="sqlite:///./test.db"
```

**Issue**: Import errors
```bash
# Install in editable mode
pip install -e .
```

### API Tests Failing (404 Errors)

**Issue**: Endpoints returning 404

✅ **FIXED**: The frontend API paths have been updated to include the `/api` prefix:
- `/v1/projects/` → `/api/v1/projects/`
- `/v1/grid/topology` → `/api/v1/grid/topology`
- `/v1/transmission/lines/geojson` → `/api/v1/transmission/lines/geojson`

Verify the backend is running:
```bash
curl http://localhost:8000/health
```

---

## Additional Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Quick Reference

```bash
# Frontend
npm test                    # Run all tests
npm test -- --watch         # Watch mode
npm test -- --coverage      # With coverage

# Backend
pytest                      # Run all tests
pytest -v                   # Verbose
pytest -x                   # Stop on first failure
pytest -m unit              # Run unit tests only
pytest --cov                # With coverage

# Integration
python backend/test_api.py           # Full E2E test
python backend/quick_test.py         # Quick verification
python backend/test_integration.py   # Integration tests
```

---

**Last Updated**: January 2026
