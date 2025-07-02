#!/usr/bin/env python3
"""
Starmap - Interactive 3D Star Viewer
Main launcher script
"""

import subprocess
import sys
import os

def main():
    """Main entry point - launch the Flask web application"""
    print("🌟 Welcome to Starmap - Interactive 3D Star Viewer!")
    print("Starting the web application...")
    
    # Check if we're in a virtual environment
    if not os.path.exists("venv"):
        print("Virtual environment not found. Running setup...")
        subprocess.run([sys.executable, "setup.py"])
        print("Setup complete. Please run 'source venv/bin/activate' then 'python main.py' again")
        return
    
    # Launch the Flask application
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nShutting down Starmap. Goodbye!")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()