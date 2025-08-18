#!/usr/bin/env python3
"""
Test Runner for Starmap - Felgenland Saga
Provides unified test execution for CI/CD and development
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=False)
        print(f"✅ SUCCESS: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description} (exit code: {e.returncode})")
        return False
    except FileNotFoundError as e:
        print(f"❌ ERROR: Command not found: {e}")
        return False

def run_unit_tests():
    """Run unit tests with pytest"""
    cmd = [
        sys.executable, "-m", "pytest", "tests/",
        "--verbose",
        "--tb=short",
        "--junit-xml=test-results.xml"
    ]
    return run_command(cmd, "Unit Tests")

def run_integration_tests():
    """Run integration tests"""
    cmd = [sys.executable, "tests/test_api_auth.py"]
    return run_command(cmd, "Integration Tests")

def run_performance_tests():
    """Run performance tests"""
    cmd = [sys.executable, "tests/test_performance.py"]
    return run_command(cmd, "Performance Tests")

def run_coverage_tests():
    """Run tests with coverage reporting"""
    cmd = [
        sys.executable, "-m", "pytest", "tests/",
        "--cov=.", 
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=50"  # Set minimum coverage
    ]
    return run_command(cmd, "Tests with Coverage")

def run_linting():
    """Run code linting"""
    commands = [
        ([sys.executable, "-m", "flake8", ".", "--count", "--statistics"], "Flake8 Linting"),
        ([sys.executable, "-m", "black", "--check", "."], "Black Code Formatting Check"),
        ([sys.executable, "-m", "isort", "--check-only", "."], "Import Sorting Check"),
    ]
    
    results = []
    for cmd, desc in commands:
        results.append(run_command(cmd, desc))
    
    return all(results)

def run_security_tests():
    """Run security tests"""
    commands = [
        ([sys.executable, "-m", "bandit", "-r", ".", "-f", "json", "-o", "bandit-report.json"], "Bandit Security Check"),
        ([sys.executable, "-m", "safety", "check", "--json"], "Safety Dependency Check"),
    ]
    
    results = []
    for cmd, desc in commands:
        # Don't fail on security warnings, just report them
        try:
            subprocess.run(cmd, cwd=project_root, check=False)
            print(f"✅ COMPLETED: {desc}")
            results.append(True)
        except Exception as e:
            print(f"⚠️  WARNING: {desc} failed: {e}")
            results.append(True)  # Don't fail the build
    
    return all(results)

def run_all_tests():
    """Run all test suites"""
    print("🚀 Running Full Test Suite")
    print("="*60)
    
    tests = [
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("Performance Tests", run_performance_tests),
        ("Code Linting", run_linting),
        ("Security Tests", run_security_tests),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n🧪 Starting: {name}")
        results[name] = test_func()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

def main():
    parser = argparse.ArgumentParser(description="Starmap Test Runner")
    parser.add_argument("test_type", nargs="?", default="all",
                       choices=["all", "unit", "integration", "performance", "coverage", "lint", "security"],
                       help="Type of tests to run")
    parser.add_argument("--report", action="store_true", help="Generate detailed reports")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(project_root)
    os.environ["STARMAP_SECRET_KEY"] = "test-secret-key"
    os.environ["FLASK_ENV"] = "testing"
    
    print(f"🧪 Starmap Test Runner")
    print(f"Project Root: {project_root}")
    print(f"Test Type: {args.test_type}")
    
    # Run requested tests
    if args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "coverage":
        success = run_coverage_tests()
    elif args.test_type == "lint":
        success = run_linting()
    elif args.test_type == "security":
        success = run_security_tests()
    else:
        print(f"Unknown test type: {args.test_type}")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())