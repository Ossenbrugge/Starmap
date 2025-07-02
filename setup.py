#!/usr/bin/env python3
"""
Setup script for Starmap application
Creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os

def run_command(command, check=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def setup_environment():
    """Set up virtual environment and install dependencies"""
    
    # Create virtual environment
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    # Install dependencies
    print("Installing dependencies...")
    run_command(f"{pip_path} install --upgrade pip")
    run_command(f"{pip_path} install -r requirements.txt")
    
    print("\nSetup complete!")
    print(f"To activate the environment, run:")
    if os.name == 'nt':
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
        
    print("\nTo run the application:")
    print("  python app.py")

if __name__ == "__main__":
    setup_environment()