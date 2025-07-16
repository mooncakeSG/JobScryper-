#!/usr/bin/env python3
"""
JobScryper Backend Startup Script
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting JobScryper Backend...")
    
    # Add current directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
    except ImportError:
        print("❌ FastAPI or Uvicorn not found. Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("🌟 Starting server on http://localhost:8000")
    print("📖 API documentation available at http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 