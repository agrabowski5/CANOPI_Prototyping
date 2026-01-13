@echo off
REM CANOPI API Fix Verification Script for Windows
REM This script verifies that the API path fixes are working correctly

echo ==================================
echo CANOPI API Fix Verification
echo ==================================
echo.

REM Check if backend is running
echo 1. Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running
) else (
    echo [ERROR] Backend is not running
    echo    Please start the backend with: cd backend ^&^& uvicorn app.main:app --reload
    exit /b 1
)

echo.

REM Test API endpoints
echo 2. Testing API endpoints...

REM Test projects endpoint
echo    Testing /api/v1/projects/...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/projects/ > temp.txt
set /p response=<temp.txt
if "%response%"=="200" (
    echo    [OK] 200 OK
) else (
    echo    [ERROR] %response%
)

REM Test grid topology endpoint
echo    Testing /api/v1/grid/topology...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/grid/topology > temp.txt
set /p response=<temp.txt
if "%response%"=="200" (
    echo    [OK] 200 OK
) else (
    echo    [ERROR] %response%
)

REM Test transmission lines endpoint
echo    Testing /api/v1/transmission/lines/geojson...
curl -s -o nul -w "%%{http_code}" "http://localhost:8000/api/v1/transmission/lines/geojson?limit=1" > temp.txt
set /p response=<temp.txt
if "%response%"=="200" (
    echo    [OK] 200 OK
) else (
    echo    [ERROR] %response%
)

REM Test optimization endpoint
echo    Testing /api/v1/optimization/jobs...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/optimization/jobs > temp.txt
set /p response=<temp.txt
if "%response%"=="200" (
    echo    [OK] 200 OK
) else (
    echo    [ERROR] %response%
)

del temp.txt >nul 2>&1

echo.

REM Verify old paths return 404 (as expected)
echo 3. Verifying legacy paths are not accessible...

echo    Testing /v1/projects/ (should be 404)...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/v1/projects/ > temp.txt
set /p response=<temp.txt
if "%response%"=="404" (
    echo    [OK] 404 (correct)
) else (
    echo    [WARNING] %response% (unexpected)
)

del temp.txt >nul 2>&1

echo.

REM Summary
echo ==================================
echo Verification Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Start the frontend: cd frontend ^&^& npm start
echo 2. Open http://localhost:3000
echo 3. Check browser console - should see no 404 errors
echo 4. Test creating projects, viewing grid, and running optimization
echo.

pause
