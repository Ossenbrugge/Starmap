#!/usr/bin/env python3
"""
Starmap Environment Setup Script
Ensures all requirements are met for the Starmap application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class StarmapEnvironmentSetup:
    """Setup and verify Starmap application environment"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "starmap_venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.python_executable = sys.executable
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        min_version = (3, 8)
        
        if version >= min_version:
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
            return True
        else:
            print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (requires >= {min_version[0]}.{min_version[1]})")
            return False
    
    def check_required_files(self):
        """Check if all required files exist"""
        print("📁 Checking required files...")
        
        required_files = [
            "requirements.txt",
            "app.py",
            "star_naming.py",
            "fictional_names.py",
            "fictional_nations.py",
            "fictional_planets.py",
            "galactic_directions.py",
            "stars_output.csv",
            "fictional_stars.csv",
            "nations_data.json",
            "templates/starmap.html"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path}")
        
        if missing_files:
            print(f"\n⚠️  Missing files ({len(missing_files)}):")
            for file_path in missing_files:
                print(f"    - {file_path}")
            return False
        
        print(f"✅ All {len(required_files)} required files found")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        print("🏗️  Setting up virtual environment...")
        
        if self.venv_path.exists():
            print("  ✅ Virtual environment already exists")
            return True
        
        try:
            print("  📦 Creating virtual environment...")
            subprocess.run([
                self.python_executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            print("  ✅ Virtual environment created successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def install_requirements(self):
        """Install requirements in virtual environment"""
        print("📦 Installing requirements...")
        
        if not self.requirements_file.exists():
            print("  ❌ requirements.txt not found")
            return False
        
        venv_python = self.get_venv_python()
        
        if not venv_python.exists():
            print("  ❌ Virtual environment Python not found")
            return False
        
        try:
            # Upgrade pip first
            print("  🔧 Upgrading pip...")
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            
            # Install requirements
            print("  📥 Installing packages...")
            result = subprocess.run([
                str(venv_python), "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            print("  ✅ Requirements installed successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install requirements: {e}")
            print(f"  Error output: {e.stderr}")
            return False
    
    def verify_installation(self):
        """Verify that all packages are properly installed"""
        print("🧪 Verifying installation...")
        
        venv_python = self.get_venv_python()
        
        test_imports = [
            "flask",
            "pandas",
            "plotly", 
            "numpy",
            "requests",
            "jinja2"
        ]
        
        test_script = f"""
import sys
try:
    {'; '.join(f'import {pkg}' for pkg in test_imports)}
    print("SUCCESS: All packages imported successfully")
    
    # Test specific versions
    import flask, pandas, plotly, numpy
    print(f"Flask: {{flask.__version__}}")
    print(f"Pandas: {{pandas.__version__}}")
    print(f"Plotly: {{plotly.__version__}}")
    print(f"Numpy: {{numpy.__version__}}")
    
except ImportError as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
        
        try:
            result = subprocess.run([
                str(venv_python), "-c", test_script
            ], check=True, capture_output=True, text=True)
            
            print("  ✅ Package verification successful")
            print("  📊 Installed versions:")
            for line in result.stdout.strip().split('\n')[1:]:  # Skip SUCCESS line
                if ':' in line:
                    print(f"    {line}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Package verification failed: {e}")
            print(f"  Error: {e.stderr}")
            return False
    
    def test_mvc_application(self):
        """Test the MVC application"""
        print("🚀 Testing MVC application...")
        
        venv_python = self.get_venv_python()
        
        test_script = """
try:
    from app import StarmapApplication
    
    # Test application creation
    app = StarmapApplication()
    
    # Test models
    models = app.get_models()
    star_count = len(models['star_model'].data) if models['star_model'].data is not None else 0
    planet_count = len(models['planet_model'].data)
    nation_count = len(models['nation_model'].data)
    
    # Test Flask app
    flask_app = app.get_app()
    route_count = len(flask_app.url_map._rules)
    
    print(f"SUCCESS: MVC application functional")
    print(f"Stars: {star_count}")
    print(f"Planetary systems: {planet_count}")
    print(f"Nations: {nation_count}")
    print(f"API routes: {route_count}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
"""
        
        try:
            result = subprocess.run([
                str(venv_python), "-c", test_script
            ], check=True, capture_output=True, text=True, timeout=30)
            
            print("  ✅ MVC application test successful")
            for line in result.stdout.strip().split('\n')[1:]:  # Skip SUCCESS line
                if ':' in line:
                    print(f"    {line}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"  ❌ MVC application test failed: {e}")
            print(f"  Error: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print("  ❌ MVC application test timed out")
            return False
    
    def generate_activation_instructions(self):
        """Generate instructions for using the environment"""
        print("\n" + "="*60)
        print("🎉 ENVIRONMENT SETUP COMPLETE!")
        print("="*60)
        
        if platform.system() == "Windows":
            activate_cmd = "starmap_venv\\Scripts\\activate"
        else:
            activate_cmd = "source starmap_venv/bin/activate"
        
        print(f"""
📋 USAGE INSTRUCTIONS:

1. Activate the virtual environment:
   {activate_cmd}

2. Run the Starmap application:
   python app.py              # Main application (MVC architecture)

3. Or use the convenience scripts:
   ./run_starmap.sh           # Interactive launcher
   ./activate_venv.sh         # Just activate environment

4. Access the application:
   http://localhost:8080

5. Deactivate when done:
   deactivate

🔧 DEVELOPMENT COMMANDS:
   python test_environment.py # Test environment
   pip freeze > requirements.txt  # Update requirements
   pip install <package>      # Add new packages

📚 DOCUMENTATION:
   - MVC_REFACTORING.md       # Architecture documentation
   - README.md                # General project information
""")
    
    def run_setup(self):
        """Run complete environment setup"""
        print("🌟 Starmap Environment Setup")
        print("="*40)
        
        success = True
        
        # Check Python version
        if not self.check_python_version():
            success = False
        
        # Check required files
        if not self.check_required_files():
            success = False
        
        if not success:
            print("\n❌ Prerequisites not met. Please address the issues above.")
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install requirements
        if not self.install_requirements():
            return False
        
        # Verify installation
        if not self.verify_installation():
            return False
        
        # Test MVC application
        if not self.test_mvc_application():
            return False
        
        # Generate instructions
        self.generate_activation_instructions()
        
        return True


def main():
    """Main setup function"""
    setup = StarmapEnvironmentSetup()
    
    if setup.run_setup():
        print("✅ Setup completed successfully!")
        return 0
    else:
        print("❌ Setup failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())