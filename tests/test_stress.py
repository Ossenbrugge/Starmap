"""
Stress tests for performance and robustness under heavy load
"""

import unittest
import os
import sys
import time
import threading
import queue
import random
from unittest.mock import patch, MagicMock

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests import BaseTestCase


class TestDatabaseStress(BaseTestCase):
    """Stress test database operations"""
    
    @patch('database.config.get_database')
    def test_concurrent_database_access(self, mock_db):
        """Test concurrent database access"""
        # Mock database with thread-safe operations
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        mock_collection = MagicMock()
        mock_db_instance.stars = mock_collection
        mock_collection.find.return_value = [{'_id': i} for i in range(100)]
        
        try:
            from managers.star_manager import StarManager
            
            results = queue.Queue()
            error_count = 0
            
            def database_worker():
                try:
                    star_manager = StarManager()
                    for _ in range(50):  # 50 operations per thread
                        stars = star_manager.search_stars(limit=10)
                        results.put(len(stars))
                        time.sleep(0.001)  # Small delay to increase contention
                except Exception as e:
                    results.put(f"ERROR: {str(e)}")
            
            # Create 10 concurrent threads
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=database_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            operation_results = []
            while not results.empty():
                result = results.get()
                if isinstance(result, str) and result.startswith("ERROR"):
                    error_count += 1
                else:
                    operation_results.append(result)
            
            # Verify results
            self.assertEqual(error_count, 0, f"Had {error_count} errors during concurrent access")
            self.assertEqual(len(operation_results), 500)  # 10 threads * 50 operations
            
        except ImportError:
            self.skipTest("StarManager not available")
    
    @patch('database.config.get_database')
    def test_large_query_performance(self, mock_db):
        """Test performance with large query results"""
        # Mock large dataset
        large_dataset = [{'_id': i, 'name': f'Star {i}'} for i in range(10000)]
        
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = large_dataset
        mock_db_instance.stars = mock_collection
        
        try:
            from managers.star_manager import StarManager
            star_manager = StarManager()
            
            # Test large query performance
            start_time = time.time()
            results = star_manager.search_stars(limit=10000)
            end_time = time.time()
            
            query_time_ms = (end_time - start_time) * 1000
            
            self.assertEqual(len(results), 10000)
            self.assertLess(query_time_ms, 5000, f"Large query took {query_time_ms:.2f}ms")
            
        except ImportError:
            self.skipTest("StarManager not available")
    
    @patch('database.config.get_database')
    def test_bulk_insert_stress(self, mock_db):
        """Test bulk insert operations under stress"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        mock_collection = MagicMock()
        mock_collection.insert_many.return_value = MagicMock()
        mock_db_instance.stars = mock_collection
        
        try:
            from managers.star_manager import StarManager
            star_manager = StarManager()
            
            # Create large batch of test data
            batch_size = 1000
            test_stars = [
                {
                    'id': 900000 + i,
                    'x': random.uniform(-100, 100),
                    'y': random.uniform(-100, 100),
                    'z': random.uniform(-100, 100),
                    'mag': random.uniform(0, 15),
                    'spect': random.choice(['O', 'B', 'A', 'F', 'G', 'K', 'M']) + '2V',
                    'name': f'Stress Test Star {i}'
                }
                for i in range(batch_size)
            ]
            
            # Test bulk insert performance
            start_time = time.time()
            result = star_manager.add_star_batch(test_stars)
            end_time = time.time()
            
            insert_time_ms = (end_time - start_time) * 1000
            
            self.assertEqual(len(result), batch_size)
            self.assertLess(insert_time_ms, 10000, f"Bulk insert took {insert_time_ms:.2f}ms")
            
        except ImportError:
            self.skipTest("StarManager not available")


class TestAPIStress(BaseTestCase):
    """Stress test API endpoints"""
    
    def setUp(self):
        super().setUp()
        
        try:
            import app_montydb
            self.app = app_montydb.app
        except ImportError:
            try:
                import app
                self.app = app.app
            except ImportError:
                self.skipTest("Flask app not available")
        
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests"""
        results = queue.Queue()
        
        def api_worker():
            try:
                for _ in range(20):  # 20 requests per thread
                    response = self.client.get('/api/spectral-types')
                    results.put(response.status_code)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                results.put(f"ERROR: {str(e)}")
        
        # Create 5 concurrent threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=api_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Collect results
        status_codes = []
        error_count = 0
        
        while not results.empty():
            result = results.get()
            if isinstance(result, str) and result.startswith("ERROR"):
                error_count += 1
            else:
                status_codes.append(result)
        
        # Verify results
        self.assertEqual(error_count, 0, f"Had {error_count} API errors")
        self.assertEqual(len(status_codes), 100)  # 5 threads * 20 requests
        
        # All requests should succeed
        for status in status_codes:
            self.assertEqual(status, 200)
    
    @patch('controllers.star_controller.StarController')
    def test_large_response_performance(self, mock_controller):
        """Test API performance with large responses"""
        # Mock large dataset response
        large_dataset = [
            {'id': i, 'name': f'Star {i}', 'x': i * 0.1, 'y': i * 0.1, 'z': i * 0.1}
            for i in range(5000)
        ]
        
        mock_instance = MagicMock()
        mock_instance.get_all_stars.return_value = large_dataset
        mock_controller.return_value = mock_instance
        
        # Test large response performance
        start_time = time.time()
        response = self.client.get('/api/stars?count_limit=5000')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time_ms, 15000, f"Large response took {response_time_ms:.2f}ms")
    
    def test_rapid_sequential_requests(self):
        """Test rapid sequential API requests"""
        request_count = 100
        max_total_time_ms = 30000  # 30 seconds max
        
        start_time = time.time()
        
        status_codes = []
        for i in range(request_count):
            response = self.client.get('/api/spectral-types')
            status_codes.append(response.status_code)
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # Verify all requests succeeded
        for status in status_codes:
            self.assertEqual(status, 200)
        
        # Verify performance
        self.assertLess(total_time_ms, max_total_time_ms, 
                       f"Rapid requests took {total_time_ms:.2f}ms")
        
        avg_time_per_request = total_time_ms / request_count
        self.assertLess(avg_time_per_request, 300, 
                       f"Average request time: {avg_time_per_request:.2f}ms")


class TestMemoryStress(BaseTestCase):
    """Stress test memory usage and management"""
    
    @patch('database.config.get_database')
    def test_memory_usage_under_load(self, mock_db):
        """Test memory usage under heavy load"""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory_mb = process.memory_info().rss / 1024 / 1024
        
        try:
            from managers.data_manager import DataManager
            
            # Mock database to return large datasets
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            large_dataset = [{'_id': i, 'data': 'x' * 1000} for i in range(1000)]
            mock_collection = MagicMock()
            mock_collection.find.return_value = large_dataset
            mock_db_instance.stars = mock_collection
            
            dm = DataManager()
            
            # Perform many operations to stress memory
            for i in range(100):
                stats = dm.get_comprehensive_statistics()
                # Force garbage collection periodically
                if i % 20 == 0:
                    gc.collect()
            
            # Check final memory usage
            final_memory_mb = process.memory_info().rss / 1024 / 1024
            memory_increase_mb = final_memory_mb - initial_memory_mb
            
            # Memory increase should be reasonable (less than 500MB)
            self.assertLess(memory_increase_mb, 500, 
                           f"Memory increased by {memory_increase_mb:.2f}MB")
            
        except ImportError:
            self.skipTest("DataManager not available")
        except ImportError:
            self.skipTest("psutil not available for memory testing")
    
    def test_garbage_collection_effectiveness(self):
        """Test that objects are properly garbage collected"""
        import gc
        import weakref
        
        try:
            from managers.data_manager import DataManager
            
            # Create objects and weak references
            managers = []
            weak_refs = []
            
            for _ in range(10):
                dm = DataManager()
                managers.append(dm)
                weak_refs.append(weakref.ref(dm))
            
            # Clear strong references
            managers.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Check if objects were collected
            alive_count = sum(1 for ref in weak_refs if ref() is not None)
            
            # Most objects should be garbage collected
            self.assertLessEqual(alive_count, 2, 
                               f"{alive_count} objects still alive after GC")
            
        except ImportError:
            self.skipTest("DataManager not available")


class TestDataIntegrityStress(BaseTestCase):
    """Test data integrity under stress conditions"""
    
    @patch('database.config.get_database')
    def test_concurrent_data_modifications(self, mock_db):
        """Test data integrity with concurrent modifications"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        mock_collection = MagicMock()
        mock_db_instance.stars = mock_collection
        
        # Mock successful operations
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = MagicMock()
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        try:
            from managers.data_manager import DataManager
            
            results = queue.Queue()
            
            def data_worker(worker_id):
                try:
                    dm = DataManager()
                    for i in range(10):
                        star_id = 900000 + worker_id * 100 + i
                        
                        # Add star
                        star_data = {
                            'id': star_id,
                            'x': i, 'y': i, 'z': i,
                            'mag': 5.0, 'spect': 'G2V'
                        }
                        added_id = dm.add_star(star_data)
                        
                        # Update star
                        update_data = {'fictional_name': f'Worker {worker_id} Star {i}'}
                        updated = dm.update_star(star_id, update_data)
                        
                        # Delete star
                        deleted = dm.delete_star(star_id, force=True)
                        
                        results.put({
                            'worker_id': worker_id,
                            'operation': i,
                            'added': added_id == star_id,
                            'updated': updated,
                            'deleted': deleted
                        })
                        
                except Exception as e:
                    results.put({'error': str(e), 'worker_id': worker_id})
            
            # Create concurrent workers
            threads = []
            for worker_id in range(5):
                thread = threading.Thread(target=data_worker, args=(worker_id,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Analyze results
            operations = []
            errors = []
            
            while not results.empty():
                result = results.get()
                if 'error' in result:
                    errors.append(result)
                else:
                    operations.append(result)
            
            # Verify no errors occurred
            self.assertEqual(len(errors), 0, f"Had {len(errors)} errors: {errors}")
            
            # Verify all operations completed
            self.assertEqual(len(operations), 50)  # 5 workers * 10 operations
            
            # Verify all operations succeeded
            for op in operations:
                self.assertTrue(op['added'], f"Add failed for worker {op['worker_id']}")
                self.assertTrue(op['updated'], f"Update failed for worker {op['worker_id']}")
                self.assertTrue(op['deleted'], f"Delete failed for worker {op['worker_id']}")
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    @patch('database.config.get_database')
    def test_validation_under_stress(self, mock_db):
        """Test data validation under stress conditions"""
        try:
            from managers.data_manager import DataManager
            
            dm = DataManager()
            
            # Test validation with many rapid calls
            validation_count = 1000
            
            start_time = time.time()
            
            for i in range(validation_count):
                # Mix of valid and invalid data
                if i % 2 == 0:
                    # Valid data
                    star_data = {
                        'id': 900000 + i,
                        'x': i * 0.1, 'y': i * 0.1, 'z': i * 0.1,
                        'mag': 5.0, 'spect': 'G2V'
                    }
                else:
                    # Invalid data
                    star_data = {
                        'id': 'invalid',
                        'mag': 50.0,  # Out of range
                        'spect': 'INVALID'
                    }
                
                errors = dm.validate_star_data(star_data)
                
                # Valid data should have no errors
                if i % 2 == 0:
                    self.assertEqual(len(errors), 0, f"Valid data failed validation at iteration {i}")
                else:
                    self.assertGreater(len(errors), 0, f"Invalid data passed validation at iteration {i}")
            
            end_time = time.time()
            validation_time_ms = (end_time - start_time) * 1000
            
            # Validation should be fast
            self.assertLess(validation_time_ms, 10000, 
                           f"Validation took {validation_time_ms:.2f}ms for {validation_count} items")
            
        except ImportError:
            self.skipTest("DataManager not available")


class TestSystemLimits(BaseTestCase):
    """Test system behavior at limits"""
    
    def test_maximum_api_request_size(self):
        """Test API behavior with maximum request sizes"""
        # Test with very large JSON payload
        large_star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V',
            'name': 'Test Star',
            'description': 'x' * 10000  # 10KB description
        }
        
        import json
        response = self.client.post(
            '/api/star/add',
            data=json.dumps(large_star_data),
            content_type='application/json'
        )
        
        # Should handle large requests gracefully
        self.assertIn(response.status_code, [200, 201, 400, 413])
    
    @patch('database.config.get_database')
    def test_maximum_query_results(self, mock_db):
        """Test handling of maximum query result sizes"""
        # Mock extremely large dataset
        huge_dataset = [{'_id': i, 'name': f'Star {i}'} for i in range(50000)]
        
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = huge_dataset
        mock_db_instance.stars = mock_collection
        
        try:
            from managers.star_manager import StarManager
            star_manager = StarManager()
            
            # Test with large limit
            start_time = time.time()
            results = star_manager.search_stars(limit=50000)
            end_time = time.time()
            
            query_time_ms = (end_time - start_time) * 1000
            
            # Should handle large results
            self.assertLessEqual(len(results), 50000)
            self.assertLess(query_time_ms, 30000, f"Large query took {query_time_ms:.2f}ms")
            
        except ImportError:
            self.skipTest("StarManager not available")


if __name__ == '__main__':
    # Run stress tests with higher verbosity
    unittest.main(verbosity=2)