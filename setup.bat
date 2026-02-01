@echo off
echo 🚀 Setting up AgentHire...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv .venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install Python dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Install frontend dependencies
echo 📥 Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Install root dependencies
echo 📥 Installing root dependencies...
npm install

echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo 1. Backend: .venv\Scripts\activate.bat ^&^& python run.py
echo 2. Frontend: cd frontend ^&^& npm run dev
echo 3. Sandbox (optional): python sandbox/job_portal.py
echo.
echo 📖 Check README.md for detailed instructions
pause