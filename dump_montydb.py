#!/usr/bin/env python3
"""
MontyDB Database Dump Script
Exports all collections to JSON files for backup and restart purposes
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add database path to sys.path
sys.path.append('database')
from database.config import initialize_database, get_database, close_database


def dump_collection_to_json(collection, output_file):
    """Dump a MontyDB collection to JSON file"""
    try:
        documents = list(collection.find({}))
        
        # Convert ObjectId and other non-serializable types to strings
        serializable_docs = []
        for doc in documents:
            serializable_doc = convert_to_serializable(doc)
            serializable_docs.append(serializable_doc)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_docs, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exported {len(serializable_docs)} documents from {collection.name} to {output_file}")
        return len(serializable_docs)
        
    except Exception as e:
        print(f"❌ Error dumping {collection.name}: {e}")
        return 0


def convert_to_serializable(obj):
    """Convert MongoDB/MontyDB objects to JSON serializable format"""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    else:
        return obj


def create_dump_directory():
    """Create a timestamped dump directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_dir = Path(f"montydb_dump_{timestamp}")
    dump_dir.mkdir(exist_ok=True)
    return dump_dir


def dump_database():
    """Dump entire MontyDB database to JSON files"""
    print("🗄️  Starting MontyDB database dump...")
    
    # Initialize database connection
    if not initialize_database():
        print("❌ Failed to initialize database!")
        return False
    
    try:
        db = get_database()
        collections = db.list_collection_names()
        
        if not collections:
            print("⚠️  No collections found in database")
            return True
        
        print(f"📊 Found {len(collections)} collections: {collections}")
        
        # Create dump directory
        dump_dir = create_dump_directory()
        print(f"📁 Creating dump in directory: {dump_dir}")
        
        total_documents = 0
        
        # Dump each collection
        for collection_name in collections:
            collection = db[collection_name]
            output_file = dump_dir / f"{collection_name}.json"
            
            doc_count = dump_collection_to_json(collection, output_file)
            total_documents += doc_count
        
        # Create metadata file
        metadata = {
            "dump_timestamp": datetime.now().isoformat(),
            "database_name": "starmap",
            "collections": collections,
            "total_documents": total_documents,
            "dump_directory": str(dump_dir),
            "database_path": "./starmap_db"
        }
        
        metadata_file = dump_dir / "dump_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Dump metadata saved to {metadata_file}")
        print(f"✅ Database dump completed successfully!")
        print(f"📊 Total documents exported: {total_documents}")
        print(f"📁 Dump location: {dump_dir.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database dump failed: {e}")
        return False
    
    finally:
        close_database()


def main():
    """Main entry point"""
    print("=" * 50)
    print("MontyDB Database Dump Utility")
    print("=" * 50)
    
    if dump_database():
        print("🎉 Dump process completed successfully!")
        return 0
    else:
        print("💥 Dump process failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())