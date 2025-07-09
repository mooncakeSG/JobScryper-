#!/usr/bin/env python3
"""
Start both JobScryper Frontend and Backend
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting Backend...")
    backend_dir = Path("backend")
    
    # Start backend process
    backend_process = subprocess.Popen(
        [sys.executable, "start.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    return backend_process

def start_frontend():
    """Start the Next.js frontend"""
    print("🎨 Starting Frontend...")
    frontend_dir = Path("job-frontend")
    
    # Start frontend process
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    return frontend_process

def main():
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(5)  # Wait for backend to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("✅ Both services started!")
        print("🔗 Backend: http://localhost:8000")
        print("🎯 Frontend: http://localhost:3000")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
            
        sys.exit(0)

if __name__ == "__main__":
    main() 