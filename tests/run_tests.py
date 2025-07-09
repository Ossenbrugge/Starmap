#!/usr/bin/env python3
"""
Starmap Test Runner
Comprehensive test execution script with various options
"""

import sys
import os
import argparse
import unittest
import time
from io import StringIO

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests import BaseTestCase, TEST_CONFIG


class TestRunner:
    """Enhanced test runner with reporting and options"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_category(self, category, verbosity=2):
        """Run specific test category"""
        print(f"\n{'='*60}")
        print(f"Running {category.upper()} Tests")
        print(f"{'='*60}")
        
        loader = unittest.TestLoader()
        
        if category == 'all':
            suite = loader.discover('tests', pattern='test_*.py')
        else:
            try:
                suite = loader.discover('tests', pattern=f'test_{category}.py')
            except Exception as e:
                print(f"Error loading {category} tests: {e}")
                return False
        
        # Capture output
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity,
            buffer=True
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Store results
        self.results[category] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'time': end_time - start_time,
            'success': result.wasSuccessful(),
            'output': stream.getvalue()
        }
        
        # Print results
        print(stream.getvalue())
        
        return result.wasSuccessful()
    
    def run_performance_tests(self):
        """Run performance-specific tests"""
        print(f"\n{'='*60}")
        print("Running PERFORMANCE Tests")
        print(f"{'='*60}")
        
        # Set performance mode
        os.environ['STARMAP_PERFORMANCE_MODE'] = '1'
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add performance-critical tests
        from tests.test_stress import TestDatabaseStress, TestAPIStress, TestMemoryStress
        from tests.test_integration import TestPerformanceIntegration
        
        suite.addTests(loader.loadTestsFromTestCase(TestDatabaseStress))
        suite.addTests(loader.loadTestsFromTestCase(TestAPIStress))
        suite.addTests(loader.loadTestsFromTestCase(TestMemoryStress))
        suite.addTests(loader.loadTestsFromTestCase(TestPerformanceIntegration))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Clean up environment
        if 'STARMAP_PERFORMANCE_MODE' in os.environ:
            del os.environ['STARMAP_PERFORMANCE_MODE']
        
        return result.wasSuccessful()
    
    def run_quick_tests(self):
        """Run quick smoke tests"""
        print(f"\n{'='*60}")
        print("Running QUICK Smoke Tests")
        print(f"{'='*60}")
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add quick tests (basic functionality)
        try:
            from tests.test_database import TestDatabaseConfig
            from tests.test_models import TestBaseModel
            from tests.test_api import TestAPIEndpoints
            
            # Add just a few key tests
            suite.addTest(TestDatabaseConfig('test_database_initialization'))
            suite.addTest(TestBaseModel('test_base_model_import'))
            suite.addTest(TestAPIEndpoints('test_home_page'))
            
        except ImportError as e:
            print(f"Warning: Could not import some test classes: {e}")
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*60}")
        print("TEST EXECUTION REPORT")
        print(f"{'='*60}")
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        total_time = 0
        
        for category, result in self.results.items():
            total_tests += result['tests_run']
            total_failures += result['failures']
            total_errors += result['errors']
            total_skipped += result['skipped']
            total_time += result['time']
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{category.upper():15} | {status} | "
                  f"Tests: {result['tests_run']:3} | "
                  f"Failures: {result['failures']:2} | "
                  f"Errors: {result['errors']:2} | "
                  f"Time: {result['time']:6.2f}s")
        
        print(f"{'='*60}")
        print(f"{'TOTAL':15} | {'':6} | "
              f"Tests: {total_tests:3} | "
              f"Failures: {total_failures:2} | "
              f"Errors: {total_errors:2} | "
              f"Time: {total_time:6.2f}s")
        
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if total_skipped > 0:
            print(f"⚠️  Skipped Tests: {total_skipped}")
        
        return total_failures == 0 and total_errors == 0
    
    def run_with_coverage(self, category='all'):
        """Run tests with coverage reporting"""
        try:
            import coverage
        except ImportError:
            print("❌ Coverage.py not installed. Install with: pip install coverage")
            return False
        
        print(f"\n{'='*60}")
        print("Running Tests with Coverage")
        print(f"{'='*60}")
        
        # Start coverage
        cov = coverage.Coverage(source=['.'])
        cov.start()
        
        # Run tests
        success = self.run_category(category, verbosity=1)
        
        # Stop coverage and report
        cov.stop()
        cov.save()
        
        print("\n📊 Coverage Report:")
        print("="*40)
        cov.report(show_missing=True)
        
        # Generate HTML report
        try:
            cov.html_report(directory='htmlcov')
            print(f"\n📄 HTML coverage report generated: htmlcov/index.html")
        except Exception as e:
            print(f"⚠️  Could not generate HTML report: {e}")
        
        return success


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Starmap Test Runner')
    
    parser.add_argument('category', nargs='?', default='all',
                       choices=['all', 'database', 'managers', 'models', 'controllers', 
                               'api', 'integration', 'stress', 'performance', 'quick'],
                       help='Test category to run (default: all)')
    
    parser.add_argument('--coverage', action='store_true',
                       help='Run tests with coverage reporting')
    
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    
    parser.add_argument('--quick', action='store_true',
                       help='Run quick smoke tests only')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet output')
    
    parser.add_argument('--report', action='store_true',
                       help='Generate detailed report')
    
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 2
    if args.verbose:
        verbosity = 3
    elif args.quiet:
        verbosity = 0
    
    runner = TestRunner()
    runner.start_time = time.time()
    
    print("🧪 Starmap Test Suite")
    print(f"Configuration: {TEST_CONFIG}")
    
    try:
        if args.quick:
            success = runner.run_quick_tests()
        elif args.performance:
            success = runner.run_performance_tests()
        elif args.coverage:
            success = runner.run_with_coverage(args.category)
        else:
            if args.category == 'all':
                categories = ['database', 'managers', 'models', 'controllers', 'api', 'integration', 'stress']
                success = True
                for category in categories:
                    category_success = runner.run_category(category, verbosity)
                    success = success and category_success
            else:
                success = runner.run_category(args.category, verbosity)
        
        runner.end_time = time.time()
        
        if args.report or args.category == 'all':
            overall_success = runner.generate_report()
            success = success and overall_success
        
        total_time = runner.end_time - runner.start_time
        print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")
        
        if success:
            print("🎉 All tests passed!")
            return 0
        else:
            print("💥 Some tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())