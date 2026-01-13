# Running CANOPI Locally - Quick Start

## ✅ Current Status

Both servers are now running successfully!

- **Backend**: http://localhost:8000 ✅
- **Frontend**: http://localhost:3000 ✅

---

## 🌐 Access the Application

**Open in your browser:** http://localhost:3000

You should see:
- 🗺️ Full North American map with Mapbox
- 📍 839 substations (grid nodes)
- ⚡ 868 transmission branches
- 🎨 Complete CANOPI interface

---

## 🚀 How to Start (For Future Reference)

### 1. Start Backend

```bash
cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**You should see:**
```
✓ Gurobi license found at C:\Users\agrab\OneDrive\gurobi.lic
✓ Grid service initialized with 839 nodes and 868 branches
✓ Sample coverage: 839 substations across North America
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (in new terminal)

```bash
cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping\frontend
npm start
```

**You should see:**
```
Compiled successfully!
You can now view canopi-frontend in the browser.
  Local:            http://localhost:3000
```

---

## 🔧 What Was Fixed

### Issue: Mapbox Token Missing
- **Error**: "An API access token is required to use Mapbox GL"
- **Fix**: Created `frontend/.env` with your Mapbox token
- **Result**: Map now loads correctly ✅

### Your Mapbox Token
```
pk.eyJ1IjoiYWdyYWJvd3MiLCJhIjoiY205MXBkaTEyMDNobjJzcHdyNjczOHY1ZiJ9.YUk31iaej90fE7REWALCLQ
```
(Already configured in `.env` - don't commit this file!)

---

## 📊 What's Loaded

### Backend Data
- ✅ **839 grid nodes** (substations, generators, loads)
- ✅ **868 transmission branches** (power lines)
- ✅ **2,174 transmission lines** (GeoJSON)
- ✅ **5 interconnections**: Western, Eastern, Texas, Canadian, Mexican
- ✅ **Gurobi license** detected and configured

### Frontend
- ✅ **Mapbox token** configured
- ✅ **API connection** to backend
- ✅ **All map layers** working
- ✅ **Project management** UI
- ✅ **Optimization** UI (mock data)

---

## 🎯 Using the Application

### View the Grid
1. Open http://localhost:3000
2. Map shows all of North America
3. Zoom in/out to see grid detail
4. Toggle layers in the sidebar

### Add a Project
1. Click **"+ New Project"** button
2. Select project type (Solar/Wind/Storage)
3. Enter details:
   - Name
   - Location (lat/lon or click on map)
   - Capacity (MW)
   - Costs
4. Click **"Create Project"**
5. See project appear on map as a marker

### Run Optimization
1. Add at least one project
2. Click **"Optimization"** panel on right
3. Click **"Run Quick Optimization"**
4. Watch progress bar
5. See results (currently mock data)
6. View cost breakdown, generation schedule, etc.

---

## 🐛 Troubleshooting

### Backend Won't Start

**"uvicorn: command not found"**
```bash
pip install fastapi uvicorn
```

**"ModuleNotFoundError: No module named 'app'"**
```bash
cd backend  # Make sure you're in backend directory
python -m uvicorn app.main:app --reload
```

**"Address already in use"**
```bash
# Kill existing process
taskkill //F //IM python.exe
# Or use different port
python -m uvicorn app.main:app --port 8001 --reload
```

---

### Frontend Won't Start

**"react-scripts: command not found"**
```bash
npm install --legacy-peer-deps
```

**"Port 3000 already in use"**
```bash
# Kill existing process
taskkill //F //IM node.exe
# Or set different port
set PORT=3001 && npm start
```

**Map not loading / Mapbox errors**
- Check `frontend/.env` exists
- Verify Mapbox token is set
- Restart frontend: Ctrl+C, then `npm start`

---

### API Errors in Browser

**"Failed to fetch" or "Network Error"**
1. Check backend is running: http://localhost:8000/health
2. Check browser console (F12) for actual error
3. Verify API URL in `.env`: `REACT_APP_API_BASE_URL=http://localhost:8000`

**"404 Not Found" for API calls**
- This was already fixed! ✅
- API paths now use `/api/v1/` prefix
- If you still see 404s, clear browser cache (Ctrl+Shift+R)

---

## 📝 Environment Files

### frontend/.env (Local Development)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=pk.eyJ1IjoiYWdyYWJvd3MiLCJhIjoiY201MXBkaTEyMDNobjJzcHdyNjczOHY1ZiJ9.YUk31iaej90fE7REWALCLQ
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_DARK_MODE=true
REACT_APP_ENABLE_DEBUG=true
```

### frontend/.env.production (Deployed)
```bash
REACT_APP_API_BASE_URL=/api
REACT_APP_MAPBOX_TOKEN=pk.eyJ1IjoiYWdyYWJvd3MiLCJhIjoiY201MXBkaTEyMDNobjJzcHdyNjczOHY1ZiJ9.YUk31iaej90fE7REWALCLQ
REACT_APP_ENVIRONMENT=production
```

**Note**: `.env` is gitignored for security (contains API tokens)

---

## 🔐 Security Note

**Never commit these files:**
- `frontend/.env` (contains API tokens)
- `backend/.env` (contains database passwords)
- `C:\Users\agrab\OneDrive\gurobi.lic` (Gurobi license)

These are automatically ignored by `.gitignore`. ✅

---

## 🎉 Everything Works!

You now have:
- ✅ Backend running with all grid data
- ✅ Frontend with Mapbox maps
- ✅ Full CANOPI interface
- ✅ 839 nodes + 868 branches loaded
- ✅ Gurobi license configured
- ✅ Ready for development!

**Just open:** http://localhost:3000

---

## 📞 Quick Commands Reference

```bash
# Start everything
cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping

# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm start

# Check health
curl http://localhost:8000/health

# View logs
# Backend: Check terminal output
# Frontend: Check terminal + browser console (F12)

# Stop servers
# Press Ctrl+C in each terminal
```

---

**Status**: ✅ Both servers running successfully!

**Last Updated**: January 13, 2026
