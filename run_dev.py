#!/usr/bin/env python3
"""
Development runner for Cinema Action Scene Generator
Starts both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_command_async(command, name):
    """Run a command asynchronously"""
    print(f"Starting {name}...")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

def main():
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Activate virtual environment and run commands
    venv_python = ".venv/bin/python"
    
    # Commands to run
    api_command = f"{venv_python} -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"
    ui_command = f"{venv_python} -m streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"
    
    processes = []
    
    try:
        # Start API server
        api_process = run_command_async(api_command, "FastAPI Backend")
        processes.append(("API", api_process))
        
        # Wait a moment for API to start
        time.sleep(3)
        
        # Start Streamlit UI
        ui_process = run_command_async(ui_command, "Streamlit Frontend")
        processes.append(("UI", ui_process))
        
        print("\n" + "="*60)
        print("🎬 Cinema Action Scene Generator - Development Server")
        print("="*60)
        print("FastAPI Backend:  http://localhost:8000")
        print("API Docs:         http://localhost:8000/docs")
        print("Streamlit UI:     http://localhost:8501")
        print("="*60)
        print("Press Ctrl+C to stop all services")
        print("="*60 + "\n")
        
        # Wait for user interrupt
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"Warning: {name} process has stopped")
        
        except KeyboardInterrupt:
            print("\nShutting down services...")
    
    finally:
        # Clean up processes
        for name, process in processes:
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
        
        print("All services stopped.")

if __name__ == "__main__":
    main()