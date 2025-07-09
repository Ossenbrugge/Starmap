"""
Base model for MontyDB operations
"""

from abc import ABC, abstractmethod
from datetime import datetime
import sys
import os

# Add database path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from config import get_collection


class BaseModelDB(ABC):
    """Base model class for MontyDB operations"""
    
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = get_collection(collection_name)
        self._cache = {}
        self._initialize_collection()
    
    @abstractmethod
    def _initialize_collection(self):
        """Initialize collection - must be implemented by subclasses"""
        pass
    
    def get_all(self, limit=None, skip=0, sort=None):
        """Get all documents from collection"""
        cursor = self.collection.find()
        
        if sort:
            cursor = cursor.sort(sort)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def get_by_id(self, document_id):
        """Get a single document by ID"""
        return self.collection.find_one({'_id': document_id})
    
    def find(self, query, limit=None, skip=0, sort=None):
        """Find documents matching query"""
        cursor = self.collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def find_one(self, query):
        """Find single document matching query"""
        return self.collection.find_one(query)
    
    def insert_one(self, document):
        """Insert a single document"""
        document['metadata.updated_at'] = datetime.utcnow()
        return self.collection.insert_one(document)
    
    def insert_many(self, documents):
        """Insert multiple documents"""
        for doc in documents:
            doc['metadata.updated_at'] = datetime.utcnow()
        return self.collection.insert_many(documents)
    
    def update_one(self, query, update):
        """Update a single document"""
        update.setdefault('$set', {})['metadata.updated_at'] = datetime.utcnow()
        return self.collection.update_one(query, update)
    
    def update_many(self, query, update):
        """Update multiple documents"""
        update.setdefault('$set', {})['metadata.updated_at'] = datetime.utcnow()
        return self.collection.update_many(query, update)
    
    def delete_one(self, query):
        """Delete a single document"""
        return self.collection.delete_one(query)
    
    def delete_many(self, query):
        """Delete multiple documents"""
        return self.collection.delete_many(query)
    
    def count_documents(self, query=None):
        """Count documents matching query"""
        if query is None:
            query = {}
        return self.collection.count_documents(query)
    
    def aggregate(self, pipeline):
        """Run aggregation pipeline"""
        return list(self.collection.aggregate(pipeline))
    
    def create_index(self, keys, **kwargs):
        """Create an index on the collection"""
        return self.collection.create_index(keys, **kwargs)
    
    def search_text(self, query, fields=None):
        """Search text across specified fields"""
        if fields is None:
            fields = ['name']
        
        # Build regex query for text search
        regex_query = {'$regex': query, '$options': 'i'}
        
        # Create OR query for multiple fields
        or_conditions = []
        for field in fields:
            or_conditions.append({field: regex_query})
        
        if len(or_conditions) == 1:
            search_query = or_conditions[0]
        else:
            search_query = {'$or': or_conditions}
        
        return self.find(search_query)
    
    def clear_cache(self):
        """Clear model cache"""
        self._cache.clear()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return {
            'collection': self.collection_name,
            'cache_entries': len(self._cache)
        }