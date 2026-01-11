#!/usr/bin/env python3
"""
Complete System Startup
Starts backend, frontend, and runs initialization checks
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("📦 Checking requirements...")
    
    # Map package names to their import names
    packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'playwright': 'playwright',
        'qdrant-client': 'qdrant_client',
        'google-generativeai': 'google.generativeai',
        'python-dotenv': 'dotenv'
    }
    
    missing = []
    for package, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - NOT INSTALLED")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    return True

def start_backend():
    """Start backend server"""
    print("\n🚀 Starting Backend Server...")
    
    backend_cmd = [
        sys.executable,
        '-m',
        'uvicorn',
        'backend.main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ]
    
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print("✅ Backend starting on http://0.0.0.0:8000")
    return backend_process

def start_frontend():
    """Start frontend server"""
    print("\n🎨 Starting Frontend Server...")
    
    frontend_dir = Path("frontend/lovable")
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return None
    
    if not (frontend_dir / "package.json").exists():
        print(f"❌ package.json not found in: {frontend_dir}")
        return None
    
    frontend_cmd = ['npm', 'run', 'dev']
    
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print("✅ Frontend starting on http://127.0.0.1:8080")
    return frontend_process

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 LinkedIn Job Automation - System Startup")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Cannot start - missing requirements")
        return
    
    # Start backend
    backend_proc = start_backend()
    time.sleep(3)
    
    # Start frontend
    frontend_proc = start_frontend()
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ SYSTEM READY")
    print("=" * 60)
    print("\n📍 Access Points:")
    print("   Backend API: http://0.0.0.0:8000")
    print("   API Docs: http://0.0.0.0:8000/docs")
    print("   Frontend UI: http://127.0.0.1:8080")
    print("\n📝 Logs:")
    print("   Backend: Terminal output above")
    print("   Frontend: Terminal output above")
    print("\n⚠️  Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Keep running
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
