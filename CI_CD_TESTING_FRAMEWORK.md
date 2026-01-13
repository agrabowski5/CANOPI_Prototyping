# CI/CD Testing Framework

## Overview

This repository now has a **comprehensive automated testing framework** that runs on every push and pull request.

---

## 🎯 What Gets Tested

### On Every Push & Pull Request

The CI workflow (`.github/workflows/ci.yml`) runs:

1. **Frontend Tests**
   - Jest unit tests for all services
   - React component tests
   - API path verification tests
   - Coverage reporting

2. **Frontend Build Verification**
   - TypeScript compilation
   - Production build
   - Build size check

3. **Frontend Linting**
   - ESLint checks
   - TypeScript type checking

4. **Backend Tests**
   - Pytest unit tests
   - API endpoint tests
   - Database integration tests
   - Tested on Python 3.10 and 3.11

5. **Backend Code Quality**
   - Black formatting check
   - Flake8 linting
   - Mypy type checking

6. **Security Scanning**
   - Trivy vulnerability scanner
   - Dependency security checks

7. **API Path Verification** (Critical!)
   - Ensures all API calls use `/api/v1/` prefix
   - Prevents 404 errors in production

8. **Integration Tests**
   - End-to-end API workflow tests
   - Database transaction tests

---

## 📋 Available Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger

**Purpose:** Run all tests and quality checks

**Jobs:**
- `frontend-tests` - Run Jest tests with coverage
- `frontend-lint` - ESLint and TypeScript checks
- `frontend-build` - Build verification
- `backend-tests` - Pytest with coverage (Python 3.10, 3.11)
- `backend-quality` - Black, Flake8, Mypy
- `security-scan` - Trivy vulnerability scanning
- `api-path-verification` - Critical path validation
- `integration-tests` - E2E tests
- `test-summary` - Results summary

**View:** https://github.com/agrabowski5/CANOPI_Prototyping/actions/workflows/ci.yml

---

### 2. Deploy with Tests (`.github/workflows/deploy-with-tests.yml`)

**Triggers:**
- Push to `main` branch
- Manual trigger

**Purpose:** Run tests BEFORE deploying (fail-safe)

**Jobs:**
1. `run-tests` - Run ALL tests first
2. `build-frontend` - Build only if tests pass
3. `deploy-frontend` - Deploy only if build succeeds
4. `deploy-backend` - Deploy backend
5. `verify-deployment` - Check deployed site
6. `notify` - Send SMS notification

**View:** https://github.com/agrabowski5/CANOPI_Prototyping/actions/workflows/deploy-with-tests.yml

---

### 3. Deploy (`.github/workflows/deploy.yml`)

**Current Status:** ⚠️ **Does not run tests** (legacy)

**Recommendation:** Replace with `deploy-with-tests.yml`

---

## 🚀 How to Use

### Run Tests Locally

```bash
# Frontend tests
cd frontend
npm test

# Frontend tests with coverage
npm test -- --coverage

# Backend tests
cd backend
pytest

# Backend tests with coverage
pytest --cov=app --cov-report=html

# API path verification (critical)
cd frontend
npm test -- api-paths.test.ts
```

### Trigger Workflows Manually

1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions
2. Select workflow (CI or Deploy with Tests)
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

### Check Test Results

After pushing code:

1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions
2. Click on the latest workflow run
3. View each job's logs
4. Check test summary at the bottom

---

## ✅ What Happens on Push

```
1. You push code to main
   ↓
2. CI Workflow triggers automatically
   ↓
3. Runs in parallel:
   - Frontend tests
   - Backend tests
   - Linting checks
   - Security scans
   - API path verification
   ↓
4. If ALL tests pass:
   ✅ Green checkmark appears
   ✅ Code is safe to deploy

5. If ANY test fails:
   ❌ Red X appears
   ❌ Workflow fails
   ❌ You get notification
   ❌ Deployment is blocked (if using deploy-with-tests)
```

---

## 🛡️ Deployment Protection

### Current Setup (deploy.yml)
❌ **No test protection** - deploys even if code is broken

### Recommended Setup (deploy-with-tests.yml)
✅ **Tests run first** - deployment blocked if tests fail

### To Enable Protected Deployment:

Option 1: **Rename files**
```bash
cd .github/workflows
mv deploy.yml deploy-old.yml
mv deploy-with-tests.yml deploy.yml
git add .
git commit -m "Enable test protection for deployments"
git push
```

Option 2: **Branch Protection Rules**
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select required checks:
   - `frontend-tests`
   - `backend-tests`
   - `api-path-verification`

---

## 📊 Test Coverage

### View Coverage Reports

**Frontend:**
- Local: `frontend/coverage/lcov-report/index.html`
- CI: Check workflow artifacts

**Backend:**
- Local: `backend/htmlcov/index.html`
- CI: Check workflow artifacts

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Frontend Services | 80%+ | 🆕 New tests |
| Frontend Components | 70%+ | TBD |
| Backend API | 80%+ | 🆕 New tests |
| Backend Core | 90%+ | TBD |

---

## 🔍 Test Categories

### Unit Tests
- Test individual functions/methods
- No external dependencies
- Fast execution
- Run on every commit

### Integration Tests
- Test multiple components together
- Database interactions
- API endpoint workflows
- Run on every push

### E2E Tests (Future)
- Full user workflows
- Browser automation (Cypress/Playwright)
- Run on deploy or nightly

### API Path Verification (Critical!)
- Ensures `/api/v1/` prefix on all calls
- Prevents 404 errors
- **Fail-fast if incorrect**
- Run on every commit

---

## 🚨 Critical Tests

These tests will **block deployment** if they fail:

1. **API Path Verification**
   - File: `frontend/src/services/__tests__/api-paths.test.ts`
   - Purpose: Prevent 404 errors
   - Impact: High - breaks entire app

2. **Frontend Build**
   - Command: `npm run build`
   - Purpose: Ensure code compiles
   - Impact: High - prevents deployment

3. **Backend Core Tests**
   - File: `backend/tests/test_projects_api.py`
   - Purpose: Ensure API works
   - Impact: High - backend failures

---

## 📝 Adding New Tests

### Frontend Test

Create file: `frontend/src/components/__tests__/MyComponent.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Backend Test

Create file: `backend/tests/test_my_feature.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_my_endpoint(client: TestClient):
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
    assert response.json()["success"] == True
```

---

## 🔧 Troubleshooting

### Tests Pass Locally But Fail in CI

**Common causes:**
1. Environment variables missing
2. Different Node/Python versions
3. Race conditions in async tests
4. Timezone differences

**Solutions:**
1. Check workflow logs for exact error
2. Replicate CI environment locally:
   ```bash
   # Use same Node version
   nvm use 20

   # Use same Python version
   pyenv local 3.10
   ```

### Workflow Takes Too Long

**Current times:**
- Frontend tests: ~2 minutes
- Backend tests: ~3 minutes
- Total CI: ~8-10 minutes

**To speed up:**
1. Run jobs in parallel (already done)
2. Cache dependencies (already done)
3. Split tests across multiple runners
4. Run only affected tests

### Tests Flaky (Sometimes Pass, Sometimes Fail)

**Common in:**
- Async/await code
- Database tests
- Network requests

**Solutions:**
1. Add retries for flaky tests
2. Increase timeouts
3. Mock external dependencies
4. Use test fixtures properly

---

## 📈 Continuous Improvement

### Current Status

✅ Frontend unit tests created
✅ Backend unit tests created
✅ API path verification created
✅ CI workflow configured
✅ Deploy with tests workflow created
⏳ Need to enable deploy-with-tests
⏳ Need more component tests
⏳ Need E2E tests

### Roadmap

**Phase 1** (Current)
- [x] Create test framework
- [x] Add service tests
- [x] Add API tests
- [x] Configure CI workflow
- [ ] Enable protected deployments

**Phase 2** (Next)
- [ ] Add component tests
- [ ] Increase coverage to 80%+
- [ ] Add visual regression tests
- [ ] Set up Codecov integration

**Phase 3** (Future)
- [ ] Add E2E tests (Cypress/Playwright)
- [ ] Performance testing
- [ ] Load testing
- [ ] Chaos engineering

---

## 🎓 Best Practices

1. **Write tests before fixing bugs** - Prevent regressions
2. **Test behavior, not implementation** - Tests should survive refactoring
3. **Keep tests simple** - One assertion per test ideally
4. **Use descriptive test names** - `test_create_project_with_invalid_email`
5. **Mock external dependencies** - Keep tests fast and reliable
6. **Run tests locally before pushing** - Faster feedback
7. **Fix broken tests immediately** - Don't let them pile up
8. **Review test coverage regularly** - Identify gaps

---

## 📚 Resources

- [Testing Guide](./TESTING_GUIDE.md) - Detailed testing documentation
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 🔗 Quick Links

- **View CI Runs**: https://github.com/agrabowski5/CANOPI_Prototyping/actions
- **Configure Workflows**: `.github/workflows/`
- **Frontend Tests**: `frontend/src/**/__tests__/`
- **Backend Tests**: `backend/tests/`
- **Test Reports**: Check workflow artifacts

---

**Last Updated**: January 13, 2026
**Framework Status**: ✅ Active and Running
