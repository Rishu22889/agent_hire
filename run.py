#!/usr/bin/env python3
"""
Run script for the Autonomous Job Application Engine.
Starts the backend server and provides instructions for the frontend.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pdfplumber
        import fastapi
        import uvicorn
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting backend server...")
    
    try:
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.app:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running at http://localhost:8000")
                print("📚 API documentation available at http://localhost:8000/docs")
                return process
            else:
                print("❌ Backend server started but not responding correctly")
                return None
        except requests.exceptions.RequestException:
            print("❌ Backend server failed to start or is not responding")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def check_frontend():
    """Check if frontend dependencies are available."""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ Frontend package.json not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  Frontend dependencies not installed")
        print("Please run: cd frontend && npm install")
        return False
    
    print("✅ Frontend is ready")
    return True

def main():
    """Main function to run the system."""
    print("🤖 Autonomous Job Application Engine")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Check frontend
    frontend_ready = check_frontend()
    
    print("\n" + "=" * 50)
    print("🎉 SYSTEM STATUS")
    print("=" * 50)
    print("✅ Backend: Running at http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    if frontend_ready:
        print("✅ Frontend: Ready to start")
        print("\n📋 TO START FRONTEND:")
        print("   cd frontend")
        print("   npm run dev")
        print("   Then visit: http://localhost:3000")
    else:
        print("⚠️  Frontend: Needs setup")
        print("\n📋 TO SETUP FRONTEND:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run dev")
    
    print("\n🔧 TESTING THE API:")
    print("   curl http://localhost:8000/")
    print("   curl http://localhost:8000/docs")
    
    print("\n📝 WORKFLOW:")
    print("   1. Upload resume (PDF/Word/Text)")
    print("   2. Review extracted text")
    print("   3. Generate & edit profile")
    print("   4. Validate profile")
    print("   5. Set application policy")
    print("   6. Run autonomous autopilot")
    print("   7. Monitor dashboard")
    
    print("\n⚠️  SAFETY FEATURES:")
    print("   • pdfplumber-only PDF processing")
    print("   • AI suggestions are always drafts")
    print("   • User must verify all information")
    print("   • Strict schema validation")
    print("   • No data invention or guessing")
    
    print(f"\n🔄 Backend PID: {backend_process.pid}")
    print("Press Ctrl+C to stop the backend server")
    
    try:
        # Keep the script running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Backend server stopped")

if __name__ == "__main__":
    main()