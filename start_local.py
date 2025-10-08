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
import atexit
from pathlib import Path

# Global variables to track processes
backend_process = None
frontend_process = None
original_cwd = None

def cleanup_processes():
    """Clean up running processes on exit."""
    global backend_process, frontend_process
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except:
            backend_process.kill()
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
        except:
            frontend_process.kill()

def run_backend():
    """Start the Flask backend server."""
    global backend_process, original_cwd
    print("Starting RubriCheck Backend API Server...")
    
    # Use absolute path to avoid directory issues
    backend_dir = Path(original_cwd) / "rubricheck-backend"
    
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        print(f"   Expected: {backend_dir}")
        print(f"   Current directory: {os.getcwd()}")
        return None
    
    print(f"SUCCESS: Backend directory found: {backend_dir}")
    
    # Check if Flask is installed
    try:
        import flask
        print("SUCCESS: Flask is available")
    except ImportError:
        print("WARNING: Flask not installed. Installing requirements...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                  cwd=backend_dir, capture_output=True, text=True, encoding="utf-8")
            if result.returncode == 0:
                print("SUCCESS: Requirements installed successfully")
            else:
                print(f"ERROR: Failed to install requirements: {result.stderr}")
                return None
        except Exception as e:
            print(f"ERROR: Error installing requirements: {e}")
            return None
    
    # Start Flask server
    try:
        print("Starting Flask server...")
        # Set environment to use UTF-8 encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['LANG'] = 'en_US.UTF-8'
        env['LC_ALL'] = 'en_US.UTF-8'
        
        # Start backend process without capturing output to avoid encoding issues
        backend_process = subprocess.Popen([sys.executable, "app.py"], 
                                         cwd=backend_dir,
                                         env=env)
        
        print("Backend server started successfully!")
        print("Backend API available at http://localhost:8000")
        
        # Wait for the process to complete
        backend_process.wait()
    except Exception as e:
        print(f"ERROR: Error starting backend: {e}")
        return None

def run_frontend():
    """Start the Vite frontend development server."""
    global frontend_process, original_cwd
    print("Starting RubriCheck Frontend Development Server...")
    
    # Use absolute path to avoid directory issues
    frontend_dir = Path(original_cwd) / "rubricheck-frontend"
    
    if not frontend_dir.exists():
        print("ERROR: Frontend directory not found!")
        print(f"   Expected: {frontend_dir}")
        print(f"   Current directory: {os.getcwd()}")
        return None
    
    print(f"SUCCESS: Frontend directory found: {frontend_dir}")
    
    # Check if node_modules exists
    node_modules_path = frontend_dir / "node_modules"
    if not node_modules_path.exists():
        print("WARNING: Installing frontend dependencies...")
        try:
            result = subprocess.run(["npm", "install"], 
                                  cwd=frontend_dir, 
                                  shell=True, 
                                  capture_output=True, 
                                  text=True, encoding="utf-8")
            if result.returncode == 0:
                print("SUCCESS: Frontend dependencies installed successfully")
            else:
                print(f"ERROR: Failed to install frontend dependencies: {result.stderr}")
                return None
        except Exception as e:
            print(f"ERROR: Error installing frontend dependencies: {e}")
            return None
    else:
        print("SUCCESS: Frontend dependencies found")
    
    # Check if .env exists, if not copy from example
    env_path = frontend_dir / ".env"
    env_example_path = frontend_dir / "env.example"
    if not env_path.exists() and env_example_path.exists():
        print("Creating .env file from example...")
        try:
            with open(env_example_path, "r", encoding="utf-8") as src, open(env_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print("SUCCESS: .env file created")
        except Exception as e:
            print(f"WARNING: Could not create .env file: {e}")
    
    # Start Vite development server
    try:
        print("Starting Vite development server...")
        # Set environment to use UTF-8 encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['LANG'] = 'en_US.UTF-8'
        env['LC_ALL'] = 'en_US.UTF-8'
        
        # Start frontend process without capturing output to avoid encoding issues
        frontend_process = subprocess.Popen(["npm", "run", "dev"], 
                                          cwd=frontend_dir,
                                          shell=True,
                                          env=env)
        
        print("Frontend server started successfully!")
        print("Check your browser at http://localhost:5173 (or the next available port)")
        print("Press Ctrl+C to stop the servers")
        
        # Wait for the process to complete
        frontend_process.wait()
    except Exception as e:
        print(f"ERROR: Error starting frontend: {e}")
        return None

def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")
    
    # Check Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Python 3.8+ is required")
        return False
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True, encoding="utf-8")
        if result.returncode == 0:
            print(f"Node.js {result.stdout.strip()}")
        else:
            print("Node.js not found. Please install Node.js")
            return False
    except FileNotFoundError:
        print("Node.js not found. Please install Node.js")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True, encoding="utf-8")
        if result.returncode == 0:
            print(f"npm {result.stdout.strip()}")
        else:
            print("npm not found")
            return False
    except FileNotFoundError:
        print("npm not found")
        return False
    
    return True

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\nSTOP: Received interrupt signal. Shutting down servers...")
    cleanup_processes()
    sys.exit(0)

def main():
    """Main function to start both servers."""
    global original_cwd
    
    # Save original working directory
    original_cwd = os.getcwd()
    
    # Register cleanup function
    atexit.register(cleanup_processes)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("RubriCheck Local Development Setup")
    print("=" * 50)
    print(f"Working directory: {original_cwd}")
    
    # Check requirements
    if not check_requirements():
        print("\nERROR: Requirements not met. Please install missing dependencies.")
        return 1
    
    # Check for environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("\nWARNING: No .env file found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("\nYou can copy from env.example as a template.")
        
        response = input("\nDo you want to continue without API key? (y/N): ")
        if response.lower() != 'y':
            print("ERROR: Setup cancelled. Please create .env file and try again.")
            return 1
        else:
            print("WARNING: Continuing without API key - some features may not work.")
    
    print("\nStarting RubriCheck servers...")
    print("Backend will run on: http://localhost:8000")
    print("Frontend will run on: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers")
    print("-" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    print("Waiting for backend to start...")
    time.sleep(3)
    
    # Check if backend started successfully
    if backend_process and backend_process.poll() is None:
        print("SUCCESS: Backend server started successfully")
    else:
        print("ERROR: Backend server failed to start")
        return 1
    
    # Start frontend in main thread
    try:
        print("Starting frontend server...")
        run_frontend()
    except KeyboardInterrupt:
        print("\nSTOP: Shutting down servers...")
        cleanup_processes()
        return 0
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        cleanup_processes()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
