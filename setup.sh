#!/bin/bash

# AgentHire Setup Script
echo "🚀 Setting up AgentHire..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install root dependencies
echo "📥 Installing root dependencies..."
npm install

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "1. Backend: source .venv/bin/activate && python run.py"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Sandbox (optional): python sandbox/job_portal.py"
echo ""
echo "📖 Check README.md for detailed instructions"