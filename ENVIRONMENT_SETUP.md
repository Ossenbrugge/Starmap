# Starmap Environment Setup Guide

## Quick Start

The Starmap application now has a complete virtual environment setup with all dependencies properly configured.

### 🚀 Instant Setup
```bash
# Run the automated setup (recommended)
python setup_environment.py

# Or manually activate existing environment
source starmap_venv/bin/activate
python app.py
```

### 🎯 Interactive Launcher
```bash
# Use the interactive script
./run_starmap.sh
```

## Environment Details

### Virtual Environment
- **Location**: `starmap_venv/`
- **Python Version**: 3.12.10
- **Activation**: `source starmap_venv/bin/activate`
- **Deactivation**: `deactivate`

### Installed Packages
```
flask==3.0.0          # Web framework
pandas==2.2.0         # Data manipulation
plotly==5.17.0        # 3D visualization
numpy==1.26.3         # Numerical computing
requests==2.31.0      # HTTP client
jinja2==3.1.3         # Template engine
pyarrow==15.0.0       # Data serialization
```

### Data Loaded Successfully
- ✅ **24,673 stars** from CSV files
- ✅ **12 planetary systems** with multiple planets
- ✅ **6 fictional nations** with territories and trade routes
- ✅ **32 API endpoints** available

## Available Scripts

### Setup & Testing
- `setup_environment.py` - Complete environment setup and verification
- `test_environment.py` - Quick environment functionality test
- `migrate_to_mvc.py` - MVC migration verification

### Application Launchers
- `run_starmap.sh` - Interactive application launcher
- `activate_venv.sh` - Activate virtual environment with instructions

### Application Files
- `app_mvc.py` - **MVC version** (recommended)
- `app.py` - Original monolithic version

## Usage Instructions

### 1. First Time Setup
```bash
# Run automated setup
python setup_environment.py

# This will:
# - Check Python version compatibility
# - Verify all required files exist
# - Create virtual environment
# - Install all dependencies
# - Test the application
```

### 2. Daily Usage
```bash
# Option A: Use interactive launcher
./run_starmap.sh

# Option B: Manual activation
source starmap_venv/bin/activate
python app.py

# Option C: Quick activation
source activate_venv.sh
python app.py
```

### 3. Access Application
- **URL**: http://localhost:8080
- **Features**: 3D starmap, planetary systems, political overlays
- **API**: RESTful endpoints for all data

## Development Workflow

### Adding New Dependencies
```bash
# Activate environment
source starmap_venv/bin/activate

# Install new package
pip install <package_name>

# Update requirements
pip freeze > requirements.txt
```

### Testing Changes
```bash
# Quick test
python test_environment.py

# Full migration test
python migrate_to_mvc.py

# Manual testing
python app.py
# Visit http://localhost:8080
```

### Virtual Environment Management
```bash
# Create new environment (if needed)
python -m venv starmap_venv

# Activate environment
source starmap_venv/bin/activate  # Linux/Mac
starmap_venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt

# Deactivate
deactivate

# Remove environment (if needed)
rm -rf starmap_venv
```

## API Endpoints

### Core Data Endpoints
- `GET /` - Main starmap interface
- `GET /api/stars` - Star data with filtering
- `GET /api/star/<id>` - Individual star details
- `GET /api/search` - Search stars by name/type
- `GET /api/distance` - Calculate distances between stars

### Planetary Systems
- `GET /api/systems` - All planetary systems
- `GET /api/planets/habitable` - Habitable zone planets
- `GET /api/planets/confirmed` - Confirmed exoplanets
- `POST /api/planet/add` - Add new planet

### Political Data
- `GET /api/nations` - Fictional nations
- `GET /api/nation/<id>` - Nation details
- `GET /api/trade-routes` - Trade route data

### Extended Features
- `GET /api/stars/brightest` - Brightest stars
- `GET /api/stars/nearest` - Nearest stars
- `GET /api/map/bounds` - Map boundaries
- `GET /api/spectral-types` - Available spectral classifications

## Troubleshooting

### Common Issues

**Virtual environment not found**
```bash
python setup_environment.py  # Recreates everything
```

**Import errors**
```bash
source starmap_venv/bin/activate
pip install -r requirements.txt
```

**Permission errors on scripts**
```bash
chmod +x *.sh
chmod +x *.py
```

**Port 8080 already in use**
```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or modify port in app_mvc.py
app.run(host='0.0.0.0', port=8081, debug=True)
```

### Verification Commands
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test imports
python -c "import flask, pandas, plotly, numpy; print('All packages OK')"

# Test application
python -c "from app import create_app; print('App OK')"
```

### Environment Information
```bash
# Show environment details
which python
pip show flask pandas plotly numpy
python -c "import sys; print(sys.path)"
```

## File Structure Overview

```
starmap/
├── starmap_venv/              # Virtual environment
├── models/                    # MVC Data layer
├── views/                     # MVC Presentation layer  
├── controllers/               # MVC Business logic layer
├── static/                    # Frontend assets
├── templates/                 # HTML templates
├── *.py                       # Application files
├── *.sh                       # Shell scripts
├── *.csv                      # Data files
├── *.json                     # Configuration files
└── *.md                       # Documentation
```

## Performance Notes

- **Startup time**: ~3-5 seconds (loading 24K+ stars)
- **Memory usage**: ~200-300 MB
- **API response**: <500ms for most endpoints
- **Frontend**: Smooth 3D visualization with WebGL

## Security Considerations

- Virtual environment isolates dependencies
- No external network requirements (except for package installation)
- Local development server (not production-ready)
- All data files included in repository

## Next Steps

1. **Development**: Use `app.py` (MVC architecture)
2. **Testing**: Run `test_environment.py` before major changes
3. **Deployment**: Consider Docker containerization for production
4. **Features**: Extend using the MVC architecture patterns

---

## Support

If you encounter issues:

1. Run `python setup_environment.py` to reset everything
2. Check `test_environment.py` output for specific errors
3. Verify all required files exist
4. Ensure Python 3.8+ is installed

The environment is now fully configured and ready for development! 🚀