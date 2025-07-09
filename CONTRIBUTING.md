# Contributing to Starmap

## Welcome Contributors! 🌟

Thank you for your interest in contributing to Starmap! This interactive 3D stellar cartography application is designed for science fiction world-building and astronomical exploration.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Git** for version control
- **Modern web browser** with WebGL support
- **4GB+ RAM** for development

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/starmap.git
   cd starmap
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv starmap_venv
   source starmap_venv/bin/activate  # Linux/Mac
   # or
   starmap_venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r tests/requirements.txt
   ```

4. **Initialize Database**
   ```bash
   chmod +x migrate_to_montydb.sh
   ./migrate_to_montydb.sh
   ```

5. **Run Tests**
   ```bash
   python tests/run_tests.py --quick
   ```

6. **Start Development Server**
   ```bash
   python app_montydb.py
   ```

## 📋 Development Workflow

### Branch Strategy

- **`main`** - Stable alpha releases
- **`develop`** - Integration branch for new features
- **`feature/feature-name`** - Individual feature branches
- **`hotfix/issue-name`** - Critical bug fixes

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow [coding standards](#coding-standards)
   - Write tests for new functionality
   - Update documentation as needed

3. **Run Tests**
   ```bash
   python tests/run_tests.py all --report
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing Requirements

### Running Tests

```bash
# Full test suite
python tests/run_tests.py all

# Specific categories
python tests/run_tests.py database
python tests/run_tests.py api
python tests/run_tests.py integration

# With coverage
python tests/run_tests.py --coverage
```

### Test Coverage Requirements

- **New Features**: 90%+ test coverage required
- **Bug Fixes**: Tests must reproduce and verify fix
- **API Changes**: Full endpoint testing required
- **Database Changes**: Migration and schema tests required

### Performance Requirements

- **API Responses**: < 500ms for standard queries
- **Database Queries**: < 200ms for typical operations
- **Memory Usage**: < 200MB for normal operations
- **Startup Time**: < 10 seconds for full initialization

## 📝 Coding Standards

### Python Style

- **PEP 8** compliance required
- **Type hints** for all public functions
- **Docstrings** for all classes and public methods
- **Maximum line length**: 120 characters

```python
def add_star(self, star_data: Dict[str, Any]) -> int:
    """
    Add a new star to the database.
    
    Args:
        star_data: Dictionary containing star information
        
    Returns:
        Star ID of the newly created star
        
    Raises:
        ValueError: If star data is invalid
    """
```

### Database Operations

- **Always use transactions** for multi-step operations
- **Validate data** before database operations
- **Use schema validation** for all document creation
- **Handle errors gracefully** with proper logging

### API Design

- **RESTful principles** for all endpoints
- **Consistent JSON responses** with metadata
- **Proper HTTP status codes**
- **Input validation** for all parameters
- **Rate limiting** considerations

### Frontend Code

- **ES6+** JavaScript standards
- **Modular design** with clear separation of concerns
- **Error handling** for all API calls
- **Performance optimization** for large datasets

## 🗂️ Project Structure

```
starmap/
├── app_montydb.py          # Main application (MontyDB)
├── app.py                  # Legacy application (CSV/JSON)
├── database/               # Database layer
│   ├── config.py          # Database configuration
│   ├── schema.py          # Document schemas
│   └── migrate.py         # Migration scripts
├── managers/               # Business logic layer
│   ├── data_manager.py    # Unified data interface
│   ├── star_manager.py    # Star CRUD operations
│   └── ...                # Other managers
├── models/                 # Data models
├── controllers/            # Request handlers
├── views/                  # Response formatting
├── templates/              # Data templates and HTML
├── static/                 # Frontend assets
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.1]
- Python: [e.g., 3.9.7]
- Browser: [e.g., Chrome 96.0]
- Starmap Version: [e.g., v0.1.0-alpha]

## Additional Context
Logs, screenshots, or other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Implementation
How might this be implemented?

## Alternatives Considered
Other approaches that were considered

## Additional Context
Mockups, examples, or related issues
```

## 📚 Documentation

### Documentation Standards

- **Clear explanations** for all features
- **Code examples** for API usage
- **Cross-references** between related sections
- **Regular updates** with code changes

### Documentation Types

- **User Documentation**: README, guides, tutorials
- **API Documentation**: Endpoint descriptions and examples
- **Developer Documentation**: Architecture, setup, contributing
- **Code Documentation**: Docstrings and comments

## 🔍 Code Review Process

### Review Checklist

- [ ] **Functionality**: Does the code work as intended?
- [ ] **Tests**: Are there adequate tests with good coverage?
- [ ] **Documentation**: Is documentation updated and clear?
- [ ] **Style**: Does code follow project standards?
- [ ] **Performance**: Are there performance considerations?
- [ ] **Security**: Are there security implications?

### Review Guidelines

- **Be constructive** and respectful in feedback
- **Focus on code**, not the person
- **Provide specific suggestions** for improvements
- **Acknowledge good work** when you see it
- **Ask questions** if something isn't clear

## 🏗️ Architecture Guidelines

### Design Principles

- **Separation of Concerns**: Clear layer boundaries
- **Modular Design**: Loosely coupled components
- **Testability**: Easy to test in isolation
- **Performance**: Efficient data handling
- **Scalability**: Ability to handle growth

### Database Design

- **MontyDB Primary**: Use MontyDB for new features
- **Schema Validation**: All documents must validate
- **Indexing**: Proper indexes for performance
- **Migrations**: Versioned schema changes

### API Design

- **RESTful**: Follow REST principles
- **Versioning**: Consider API versioning for breaking changes
- **Error Handling**: Consistent error responses
- **Documentation**: OpenAPI/Swagger documentation

## 🎯 Contribution Areas

### High Priority

- **Performance Optimization**: Database query optimization
- **New Data Sources**: Additional astronomical catalogs
- **Visualization Features**: Enhanced 3D rendering
- **API Enhancements**: New endpoints and functionality

### Medium Priority

- **User Interface**: UI/UX improvements
- **Data Import/Export**: Additional formats
- **Testing**: Expanded test coverage
- **Documentation**: User guides and tutorials

### Low Priority

- **Code Refactoring**: Internal improvements
- **Build System**: Development tooling
- **Deployment**: Containerization and deployment

## 📖 Resources

### Learning Resources

- **[README.md](README.md)** - Project overview
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation index
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Data operations guide
- **[Tests README](tests/README.md)** - Testing guide

### External Resources

- **[Flask Documentation](https://flask.palletsprojects.com/)**
- **[MontyDB Documentation](https://montydb.readthedocs.io/)**
- **[Plotly.js Documentation](https://plotly.com/javascript/)**
- **[Python Testing](https://docs.python.org/3/library/unittest.html)**

## 🤝 Community

### Communication

- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: All contributions require review

### Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Documentation** for major features

## 📄 License

By contributing to Starmap, you agree that your contributions will be licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.

---

**Thank you for contributing to Starmap! 🌟**

Your contributions help make stellar cartography accessible to science fiction writers and astronomy enthusiasts worldwide.