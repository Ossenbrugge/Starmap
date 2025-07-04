import pandas as pd
import os
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Base model class providing common data operations"""
    
    def __init__(self):
        self.data = None
        self.load_data()
    
    @abstractmethod
    def load_data(self):
        """Load data from source - must be implemented by subclasses"""
        pass
    
    def validate_data(self, data):
        """Validate data structure - can be overridden by subclasses"""
        if data is None or (isinstance(data, pd.DataFrame) and data.empty):
            raise ValueError("Data cannot be empty")
        return True
    
    def get_all(self):
        """Get all data"""
        return self.data
    
    def get_by_id(self, record_id):
        """Get a single record by ID"""
        if self.data is None:
            return None
        
        if isinstance(self.data, pd.DataFrame):
            result = self.data[self.data['id'] == record_id]
            return result.iloc[0] if not result.empty else None
        elif isinstance(self.data, dict):
            return self.data.get(record_id)
        
        return None
    
    def filter_data(self, **filters):
        """Filter data based on criteria"""
        if self.data is None or isinstance(self.data, dict):
            return self.data
        
        filtered_data = self.data.copy()
        
        for column, value in filters.items():
            if column in filtered_data.columns:
                if isinstance(value, (list, tuple)):
                    filtered_data = filtered_data[filtered_data[column].isin(value)]
                else:
                    filtered_data = filtered_data[filtered_data[column] == value]
        
        return filtered_data
    
    def search(self, query, search_columns=None):
        """Search data by text query"""
        if self.data is None or not isinstance(self.data, pd.DataFrame):
            return pd.DataFrame()
        
        if search_columns is None:
            search_columns = ['name'] if 'name' in self.data.columns else []
        
        if not search_columns:
            return pd.DataFrame()
        
        results = pd.DataFrame()
        
        for column in search_columns:
            if column in self.data.columns:
                matches = self.data[
                    self.data[column].str.contains(query, case=False, na=False)
                ]
                results = pd.concat([results, matches]).drop_duplicates()
        
        return results
    
    def reload_data(self):
        """Reload data from source"""
        self.load_data()