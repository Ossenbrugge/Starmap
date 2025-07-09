"""
Setup configuration for Starmap
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version
def get_version():
    """Get version from app_montydb.py"""
    try:
        with open("app_montydb.py", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "0.1.0-alpha"

setup(
    name="starmap",
    version=get_version(),
    author="Starmap Contributors",
    author_email="contact@starmap.dev",
    description="Interactive 3D stellar cartography for science fiction world-building",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/starmap/starmap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
            "mypy>=0.991",
            "coverage>=7.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "coverage>=7.0.0",
            "psutil>=5.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "starmap=app_montydb:main",
            "starmap-migrate=database.migrate:main",
            "starmap-test=tests.run_tests:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.csv",
            "*.json",
            "*.html",
            "*.css",
            "*.js",
            "*.md",
            "*.txt",
            "*.sh",
            "templates/*",
            "static/*",
            "static/css/*",
            "static/js/*",
            "tests/*",
            "database/*",
            "managers/*",
            "models/*",
            "controllers/*",
            "views/*",
        ],
    },
    keywords="astronomy, visualization, science-fiction, starmap, cartography, 3d, flask, montydb",
    project_urls={
        "Documentation": "https://github.com/starmap/starmap/blob/main/README.md",
        "Source": "https://github.com/starmap/starmap",
        "Tracker": "https://github.com/starmap/starmap/issues",
        "Changelog": "https://github.com/starmap/starmap/releases",
    },
)