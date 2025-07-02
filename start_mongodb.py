#!/usr/bin/env python3
"""
MongoDB startup script for Starmap application
Creates and starts a local MongoDB instance
"""

import subprocess
import os
import sys
import time
import signal
import atexit
from pathlib import Path

class MongoDBManager:
    def __init__(self, data_dir="./mongodb_data", port=27017):
        self.data_dir = Path(data_dir).absolute()
        self.port = port
        self.process = None
        self.log_file = None
        
    def setup_directories(self):
        """Create necessary directories for MongoDB"""
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "logs").mkdir(exist_ok=True)
        print(f"MongoDB data directory: {self.data_dir}")
        
    def check_mongodb_installed(self):
        """Check if MongoDB is installed"""
        try:
            result = subprocess.run(["mongod", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("MongoDB is installed")
                return True
            else:
                print("MongoDB not found in PATH")
                return False
        except FileNotFoundError:
            print("MongoDB not installed or not in PATH")
            return False
    
    def start_mongodb(self):
        """Start MongoDB server"""
        if not self.check_mongodb_installed():
            print("\nMongoDB Installation Instructions:")
            if sys.platform == "darwin":  # macOS
                print("Install with Homebrew: brew install mongodb-community")
            elif sys.platform.startswith("linux"):
                print("Install with: sudo apt-get install mongodb-org (Ubuntu/Debian)")
                print("Or: sudo yum install mongodb-org (RHEL/CentOS)")
            else:
                print("Download from: https://www.mongodb.com/try/download/community")
            return False
            
        self.setup_directories()
        
        # MongoDB configuration
        log_path = self.data_dir / "logs" / "mongodb.log"
        
        cmd = [
            "mongod",
            "--dbpath", str(self.data_dir),
            "--port", str(self.port),
            "--logpath", str(log_path),
            "--logappend"
        ]
        
        try:
            print(f"Starting MongoDB on port {self.port}...")
            self.process = subprocess.Popen(cmd, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE)
            
            # Wait a bit for MongoDB to start
            time.sleep(3)
            
            # Check if process is still running
            if self.process.poll() is None:
                print(f"MongoDB started successfully (PID: {self.process.pid})")
                print(f"Data directory: {self.data_dir}")
                print(f"Log file: {log_path}")
                
                # Register cleanup function
                atexit.register(self.stop_mongodb)
                
                return True
            else:
                stdout, stderr = self.process.communicate()
                print(f"MongoDB failed to start:")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"Error starting MongoDB: {e}")
            return False
    
    def stop_mongodb(self):
        """Stop MongoDB server"""
        if self.process and self.process.poll() is None:
            print("Stopping MongoDB...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("MongoDB didn't stop gracefully, forcing...")
                self.process.kill()
            print("MongoDB stopped")
    
    def is_running(self):
        """Check if MongoDB is running"""
        try:
            result = subprocess.run(["mongo", "--eval", "db.stats()"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

def main():
    """Main function to start MongoDB"""
    mongo_manager = MongoDBManager()
    
    if mongo_manager.start_mongodb():
        print("\nMongoDB is ready!")
        print("You can now run the Starmap application.")
        print("Press Ctrl+C to stop MongoDB and exit")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            mongo_manager.stop_mongodb()
    else:
        print("Failed to start MongoDB")
        sys.exit(1)

if __name__ == "__main__":
    main()