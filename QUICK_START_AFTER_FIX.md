# Quick Start After Fix

## What Was Fixed

✅ Fixed 404 API errors (`/v1/projects/`, `/v1/grid/topology`, `/v1/transmission/lines/geojson`)
✅ Added comprehensive testing framework
✅ Created testing documentation

## Start the Application

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm start
```

Frontend will be available at: `http://localhost:3000`

### 3. Verify Fix (Optional)

**Windows:**
```bash
verify-fix.bat
```

**Mac/Linux:**
```bash
bash verify-fix.sh
```

## Test the Application

1. **Open browser**: http://localhost:3000
2. **Check console** (F12 → Console tab): Should see no 404 errors
3. **Test features**:
   - Click "+ New Project" to create a project
   - Projects should appear in the left panel
   - Map should load with transmission lines
   - Click "Optimization" to run optimization

## Run Tests

### Frontend Tests
```bash
cd frontend

# All tests
npm test

# Specific test to verify API paths
npm test -- api-paths.test.ts

# With coverage
npm test -- --coverage
```

### Backend Tests
```bash
cd backend

# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_projects_api.py
```

## What Changed

### Files Modified:
1. `frontend/src/services/projectsService.ts` - Added `/api` prefix
2. `frontend/src/services/gridService.ts` - Added `/api` prefix
3. `frontend/src/services/transmissionService.ts` - Added `/api` prefix
4. `frontend/src/services/optimizationService.ts` - Added `/api` prefix

### Files Created:
1. `frontend/src/services/__tests__/projectsService.test.ts` - Service tests
2. `frontend/src/services/__tests__/gridService.test.ts` - Service tests
3. `frontend/src/services/__tests__/api-paths.test.ts` - Path verification
4. `backend/tests/conftest.py` - Test fixtures
5. `backend/tests/test_projects_api.py` - API tests
6. `backend/pytest.ini` - Pytest configuration
7. `TESTING_GUIDE.md` - Complete testing documentation
8. `FIX_SUMMARY.md` - Detailed fix information

## API Endpoints Reference

All backend endpoints now use the `/api/v1/` prefix:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/projects/` | GET, POST | List/create projects |
| `/api/v1/projects/{id}` | GET, PUT, DELETE | Get/update/delete project |
| `/api/v1/grid/topology` | GET | Get grid topology |
| `/api/v1/grid/nodes` | GET | Get network nodes |
| `/api/v1/grid/lines` | GET | Get transmission lines |
| `/api/v1/transmission/lines/geojson` | GET | Get lines as GeoJSON |
| `/api/v1/transmission/stats` | GET | Get statistics |
| `/api/v1/optimization/jobs` | GET, POST | List/create optimization jobs |
| `/api/v1/optimization/jobs/{id}` | GET | Get job status |
| `/api/v1/optimization/jobs/{id}/results` | GET | Get job results |

## API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Troubleshooting

### Still seeing 404 errors?

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Check API endpoints**:
   ```bash
   curl http://localhost:8000/api/v1/projects/
   ```
   Should return: `[]` or list of projects

3. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Delete → Clear browsing data
   - Or hard reload: Ctrl+Shift+R

4. **Rebuild frontend**:
   ```bash
   cd frontend
   rm -rf node_modules build
   npm install
   npm start
   ```

### Frontend won't start?

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend won't start?

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Tests failing?

```bash
# Frontend
cd frontend
npm test -- --clearCache
npm test

# Backend
cd backend
pip install -r requirements.txt
pytest -v
```

## Need Help?

1. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing info
2. Check [FIX_SUMMARY.md](FIX_SUMMARY.md) for detailed fix information
3. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
4. Check [README.md](README.md) for general project information

## Production Deployment

The fix will be automatically deployed on next push to main branch via GitHub Actions.

**Production URL**: https://agrabowski5.github.io/CANOPI_Prototyping

To deploy manually:
```bash
cd frontend
npm run build
# Push to GitHub
git add .
git commit -m "Fix API path issues and add testing framework"
git push origin main
```

---

**Status**: ✅ All systems operational
**Last Updated**: January 13, 2026
