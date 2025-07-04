# Git Setup and .gitignore Configuration

## Overview

The Starmap project is configured with a comprehensive .gitignore file to ensure that sensitive, temporary, and environment-specific files are never committed to the repository.

## What's Ignored

### 🚫 Virtual Environment Files
```
starmap_venv/          # Project-specific virtual environment
.venv/                 # Standard venv directory
env/                   # Alternative env directory
venv/                  # Common venv name
ENV/                   # Uppercase variant
```

### 🚫 Backup and Temporary Directories
```
backup/                # Contains original app.py and migration tools
*.backup               # Any backup files
*.bak                  # Backup file extensions
temp/                  # Temporary files
tmp/                   # Temporary directories
scratch/               # Development scratch space
migrations/            # Database migration files (if created)
```

### 🚫 Environment Configuration
```
.env.local             # Local environment variables
.env.development       # Development environment config
.env.production        # Production environment config
.env.test              # Test environment config
environment.json       # Environment configuration files
environment_config.py  # Python environment config
```

### 🚫 Runtime and Cache Files
```
starmap.db            # SQLite database files (if created)
starmap.sqlite        # Alternative database naming
cache/                # Cache directories
.cache/               # Hidden cache directories
*.cache               # Cache files
```

### 🚫 Development and Testing
```
test_output/          # Test result files
test_results/         # Test artifacts
debug_output/         # Debug logs and files
profiling/            # Performance profiling data
benchmarks/           # Benchmark results
```

### 🚫 Log Files and Runtime Data
```
setup_log.txt         # Installation logs
migration_log.txt     # Migration process logs
test_log.txt          # Test execution logs
installation_log.txt  # Environment setup logs
*.log                 # All log files
```

### 🚫 IDE and Editor Files
```
.idea/                # IntelliJ/PyCharm files
.vscode/              # Visual Studio Code files
*.sublime-*           # Sublime Text files
.project              # Eclipse project files
.pydevproject         # PyDev project files
```

### 🚫 Python-Specific
```
__pycache__/          # Python cache directories
*.py[cod]             # Compiled Python files
*$py.class            # Python class files
*.so                  # Compiled extensions
.pytest_cache/        # Pytest cache
.mypy_cache/          # MyPy cache
.ruff_cache/          # Ruff linter cache
```

### 🚫 Flask-Specific
```
instance/             # Flask instance folder
.webassets-cache      # Flask-Assets cache
```

## What's Tracked

### ✅ Source Code
```
app.py                # Main MVC application
models/               # Data layer
views/                # Presentation layer
controllers/          # Business logic layer
```

### ✅ Core Application Files
```
star_naming.py        # Core modules
fictional_*.py        # Data processing modules
galactic_directions.py # Coordinate systems
```

### ✅ Data Files
```
stars_output.csv      # Star catalog data
fictional_stars.csv   # Fictional star data
nations_data.json     # Political data
```

### ✅ Frontend Assets
```
static/               # CSS, JavaScript, images
templates/            # HTML templates
```

### ✅ Configuration and Documentation
```
requirements.txt      # Python dependencies
*.md                  # Documentation files
LICENSE               # License file
```

### ✅ Helper Scripts
```
*.sh                  # Shell scripts (activation, runner)
setup_environment.py  # Environment setup
test_environment.py   # Testing utilities
```

## Git Workflow

### Initial Setup
```bash
# Initialize repository (if not already done)
git init

# Add all trackable files
git add .

# Commit the MVC refactor
git commit -m "Implement MVC architecture and cleanup codebase"
```

### Daily Development
```bash
# Check what's changed
git status

# Add specific files
git add app.py models/ controllers/ views/

# Or add all tracked changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin main
```

### Verifying .gitignore
```bash
# Check if specific files/directories are ignored
git check-ignore starmap_venv/    # Should return the path (ignored)
git check-ignore backup/          # Should return the path (ignored)

# List all ignored files in directory
git status --ignored

# Test what would be added
git add --dry-run .
```

## Repository Structure

After applying .gitignore, your repository should contain:

```
starmap/
├── .gitignore                    # ✅ Ignore rules
├── app.py                        # ✅ Main application
├── requirements.txt              # ✅ Dependencies
├── models/                       # ✅ MVC Models
├── views/                        # ✅ MVC Views
├── controllers/                  # ✅ MVC Controllers
├── static/                       # ✅ Frontend assets
├── templates/                    # ✅ HTML templates
├── *.py                          # ✅ Core modules
├── *.csv, *.json                # ✅ Data files
├── *.md                          # ✅ Documentation
├── *.sh                          # ✅ Helper scripts
├── setup_environment.py         # ✅ Setup utilities
├── test_environment.py          # ✅ Testing utilities
├── starmap_venv/                # 🚫 IGNORED - Virtual environment
├── backup/                      # 🚫 IGNORED - Original files
├── __pycache__/                 # 🚫 IGNORED - Python cache
└── *.log                        # 🚫 IGNORED - Log files
```

## Best Practices

### 1. **Never Commit Environment Files**
- Virtual environments should be recreated on each system
- Use `requirements.txt` instead of committing `starmap_venv/`

### 2. **Keep Backups Local**
- Original files in `backup/` are for local reference only
- Don't commit migration tools or old versions

### 3. **Environment Variables**
- Use `.env` files for local configuration
- Never commit sensitive data like API keys
- Document required environment variables in README

### 4. **Development Files**
- Keep IDE settings, cache files, and logs local
- Only commit source code and documentation

### 5. **Regular Cleanup**
```bash
# Clean up untracked files (be careful!)
git clean -fd

# See what would be cleaned first
git clean -fd --dry-run
```

## Common Issues and Solutions

### Issue: Virtual Environment Accidentally Committed
```bash
# Remove from repository but keep locally
git rm -r --cached starmap_venv/
git commit -m "Remove virtual environment from repository"

# Add to .gitignore if not already there
echo "starmap_venv/" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore to exclude virtual environment"
```

### Issue: Cache Files Committed
```bash
# Remove cache directories
git rm -r --cached __pycache__/
git rm --cached *.pyc

# Commit the removal
git commit -m "Remove Python cache files"
```

### Issue: Large Files Accidentally Added
```bash
# Remove large files
git rm --cached large_file.db

# Add to .gitignore
echo "*.db" >> .gitignore
git add .gitignore
git commit -m "Remove database files and update .gitignore"
```

## Sharing the Project

### For Other Developers
```bash
# Clone the repository
git clone <repository-url>
cd starmap

# Set up environment
python setup_environment.py

# Start developing
source starmap_venv/bin/activate
python app.py
```

### For Production Deployment
```bash
# Clone repository
git clone <repository-url>
cd starmap

# Create production environment
python -m venv production_env
source production_env/bin/activate
pip install -r requirements.txt

# Configure production settings
export FLASK_ENV=production

# Run application
python app.py
```

## Security Considerations

The .gitignore configuration helps maintain security by:

- ✅ **Preventing credential leaks** - Environment files are ignored
- ✅ **Excluding sensitive data** - Database files and caches ignored
- ✅ **Avoiding system-specific files** - Virtual environments ignored
- ✅ **Protecting development data** - Backup and temp files ignored

This ensures that only the necessary source code and documentation are shared in the repository, keeping sensitive information secure and reducing repository size.