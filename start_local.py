#!/usr/bin/env python3
"""
RubriCheck Local Development Startup Script
==========================================
This script helps you start both the backend API server and frontend development server.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def run_backend():
    """Start the Flask backend server."""
    print("🚀 Starting RubriCheck Backend API Server...")
    backend_dir = Path("rubricheck-backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return None
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is available")
    except ImportError:
        print("❌ Flask not installed. Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start Flask server
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def run_frontend():
    """Start the Vite frontend development server."""
    print("🎨 Starting RubriCheck Frontend Development Server...")
    frontend_dir = Path("rubricheck-frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Check if node_modules exists
    if not Path("node_modules").exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"])
    
    # Check if .env exists, if not copy from example
    if not Path(".env").exists() and Path("env.example").exists():
        print("📝 Creating .env file from example...")
        with open("env.example", "r") as src, open(".env", "w") as dst:
            dst.write(src.read())
    
    # Start Vite development server
    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def main():
    """Main function to start both servers."""
    print("🎯 RubriCheck Local Development Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please install missing dependencies.")
        return
    
    # Check for environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  No .env file found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("\nYou can copy from env.example as a template.")
        
        response = input("\nDo you want to continue without API key? (y/N): ")
        if response.lower() != 'y':
            return
    
    print("\n🚀 Starting RubriCheck servers...")
    print("Backend will run on: http://localhost:8000")
    print("Frontend will run on: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers")
    print("-" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
