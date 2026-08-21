@echo off
REM Quick API Test Script for Windows
REM Tests all major endpoints of the Theophysics Backend

echo ========================================
echo THEOPHYSICS BACKEND API TESTS
echo ========================================
echo.

REM Check if server is running
echo [1/8] Testing Health Endpoint...
curl -s http://localhost:5000/health
echo.
echo.

echo [2/8] Testing Root Endpoint...
curl -s http://localhost:5000/
echo.
echo.

echo [3/8] Testing API Documentation...
curl -s http://localhost:5000/docs
echo.
echo.

echo [4/8] Testing Fruits of Spirit - Get All...
curl -s http://localhost:5000/api/fruits-of-spirit/
echo.
echo.

echo [5/8] Testing Fruits of Spirit - Get Love...
curl -s http://localhost:5000/api/fruits-of-spirit/name/Love
echo.
echo.

echo [6/8] Testing Physics Mappings...
curl -s http://localhost:5000/api/fruits-of-spirit/physics-mapping
echo.
echo.

echo [7/8] Testing Random Fruit...
curl -s http://localhost:5000/api/fruits-of-spirit/random
echo.
echo.

echo [8/8] Testing Definition Status...
curl -s http://localhost:5000/api/definitions/status
echo.
echo.

echo ========================================
echo TESTS COMPLETE
echo ========================================
echo.
echo If you see JSON responses above, the API is working!
echo.
pause
