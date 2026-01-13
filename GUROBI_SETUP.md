# Gurobi Setup for CANOPI

## Current Status

✅ **Gurobi License Found**: `C:\Users\agrab\OneDrive\gurobi.lic`
⚠️ **Gurobi Not Installed**: Python 3.14 is too new, Gurobi doesn't have wheels yet

---

## Solution Options

### Option 1: Use Python 3.11 or 3.12 (Recommended)

Gurobi currently supports Python 3.8-3.13, but 3.14 just came out.

**Quick fix:**

1. **Install Python 3.11 or 3.12:**
   - Download from: https://www.python.org/downloads/
   - Or use: `winget install Python.Python.3.12`

2. **Create virtual environment with 3.12:**
   ```bash
   cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping\backend
   py -3.12 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set environment variable for license:**
   ```bash
   set GRB_LICENSE_FILE=C:\Users\agrab\OneDrive\gurobi.lic
   ```

4. **Test Gurobi:**
   ```bash
   python -c "import gurobipy; print('Gurobi version:', gurobipy.gurobi.version())"
   ```

---

### Option 2: Install Gurobi Manually (If pip fails)

1. **Download Gurobi installer:**
   - Go to: https://www.gurobi.com/downloads/
   - Download Gurobi Optimizer (latest version)
   - Run installer

2. **Install gurobipy after Gurobi install:**
   ```bash
   cd C:\gurobi1100\win64
   python setup.py install
   ```

3. **Set license environment variable:**
   ```bash
   set GRB_LICENSE_FILE=C:\Users\agrab\OneDrive\gurobi.lic
   ```

---

### Option 3: Use Open-Source Solver (Quick Alternative)

For testing without Gurobi, use HiGHS (open-source):

```bash
pip install highspy scipy
```

Then modify `canopi_engine/solvers/` to use HiGHS instead of Gurobi.

---

## Setting Up Environment Variable Permanently

### Windows (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable('GRB_LICENSE_FILE', 'C:\Users\agrab\OneDrive\gurobi.lic', 'User')
```

### Windows (Command Prompt):
```cmd
setx GRB_LICENSE_FILE "C:\Users\agrab\OneDrive\gurobi.lic"
```

### In Python code (temporary):
```python
import os
os.environ['GRB_LICENSE_FILE'] = r'C:\Users\agrab\OneDrive\gurobi.lic'
```

---

## Quick Test Script

Save as `test_gurobi.py`:

```python
import os
import sys

# Set license file
os.environ['GRB_LICENSE_FILE'] = r'C:\Users\agrab\OneDrive\gurobi.lic'

try:
    import gurobipy as gp
    from gurobipy import GRB

    print(f"✓ Gurobi version: {gp.gurobi.version()}")

    # Test creating a simple model
    m = gp.Model("test")
    x = m.addVar(name="x")
    m.setObjective(x, GRB.MAXIMIZE)
    m.addConstr(x <= 10)
    m.optimize()

    print(f"✓ Gurobi license valid!")
    print(f"✓ Optimization result: x = {x.X}")

except ImportError as e:
    print(f"✗ Gurobi not installed: {e}")
    print("\nInstall with: pip install gurobipy")
    sys.exit(1)

except Exception as e:
    print(f"✗ Gurobi error: {e}")
    print("\nCheck license file at: C:\\Users\\agrab\\OneDrive\\gurobi.lic")
    sys.exit(1)
```

Run:
```bash
python test_gurobi.py
```

---

## For CANOPI Backend

### Update backend/.env or set environment:

Create `backend/.env`:
```bash
GRB_LICENSE_FILE=C:\Users\agrab\OneDrive\gurobi.lic
```

Or in `backend/app/main.py`, add to startup:
```python
import os
os.environ['GRB_LICENSE_FILE'] = r'C:\Users\agrab\OneDrive\gurobi.lic'
```

---

## Troubleshooting

### "No module named 'gurobipy'"
- Gurobi not installed for your Python version
- Try: `pip install gurobipy` (requires Python 3.8-3.13)
- Or install from Gurobi website

### "License file not found"
- Check file exists: `ls C:\Users\agrab\OneDrive\gurobi.lic`
- Set environment variable (see above)

### "License expired"
- Check license file date
- Request new license from Gurobi

### "Could not create environment"
- License file corrupted
- Try re-downloading from Gurobi portal

---

## Current Workaround (Without Gurobi)

The backend already has a fallback! If Gurobi fails, it returns **mock optimization results**.

**This means:**
- ✅ You can test the full UI workflow
- ✅ Optimization button works
- ✅ Results are displayed
- ⚠️ Results are mock data (not real optimization)

**For production**, you'll need Gurobi installed and licensed.

---

## Recommended Next Steps

**For immediate testing (TODAY):**
1. ✅ Just start the backend (it will use mock optimization)
2. ✅ Test the full UI
3. ✅ See grid data on map (839 nodes, 868 branches)

**For real optimization (THIS WEEK):**
1. Install Python 3.12 (more compatible than 3.14)
2. Create venv with 3.12
3. Install Gurobi: `pip install gurobipy`
4. Set license env var
5. Restart backend
6. Real optimization will work!

---

## Quick Commands

```bash
# Check if Gurobi is available
python -c "import gurobipy; print('OK')"

# Check license file
cat C:\Users\agrab\OneDrive\gurobi.lic | head -10

# Set license for current session
set GRB_LICENSE_FILE=C:\Users\agrab\OneDrive\gurobi.lic

# Test backend with mock data (no Gurobi needed)
cd backend
uvicorn app.main:app --reload
```

---

**Current Status:**
- ✅ License file exists
- ⚠️ Gurobi not installed (Python 3.14 too new)
- ✅ Backend works with mock optimization
- ✅ All grid data loads correctly (839 nodes, 868 branches)

**Recommendation:**
Start backend now to test everything. Install Gurobi with Python 3.12 when ready for real optimization.

---

**Last Updated:** January 13, 2026
