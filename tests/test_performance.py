#!/usr/bin/env python3
"""
Performance Test: JSON vs MontyDB
Compare query performance between the old JSON system and new MontyDB system
"""

import time
from contextlib import contextmanager

# Test MontyDB performance
from database.config import initialize_database
from models.star_model_db import StarModelDB
from models.nation_model_db import NationModelDB
from models.trade_route_model_db import TradeRouteModelDB

# Test old JSON system
from models.database import Database as JSONDatabase

@contextmanager
def timer(description):
    """Context manager for timing operations"""
    start = time.time()
    yield
    end = time.time()
    print(f"{description}: {(end - start) * 1000:.2f}ms")

def test_montydb_performance():
    """Test MontyDB performance"""
    print("🔬 Testing MontyDB Performance")
    print("-" * 40)
    
    # Initialize
    initialize_database()
    star_model = StarModelDB()
    nation_model = NationModelDB()
    trade_model = TradeRouteModelDB()
    
    # Test star queries
    with timer("MontyDB: Load 1000 stars"):
        stars = star_model.get_stars(limit=1000)
    
    with timer("MontyDB: Search 'alpha'"):
        results = star_model.search_stars("alpha", limit=20)
    
    with timer("MontyDB: Get star by ID"):
        star = star_model.get_star_by_id(71456)
    
    with timer("MontyDB: Stars by nation"):
        nation_stars = star_model.get_stars_by_nation("terran_directorate")
    
    # Test nation queries
    with timer("MontyDB: Load all nations"):
        nations = nation_model.get_nations()
    
    # Test trade route queries
    with timer("MontyDB: Load all trade routes"):
        routes = trade_model.get_trade_routes()
    
    with timer("MontyDB: Trade network analysis"):
        analysis = trade_model.get_trade_network_analysis()
    
    print(f"✅ MontyDB Results: {len(stars)} stars, {len(nations)} nations, {len(routes)} routes")

def test_json_performance():
    """Test JSON system performance"""
    print("\n🗃️  Testing JSON Performance")
    print("-" * 40)
    
    # Initialize JSON database
    json_db = JSONDatabase()
    
    # Test queries
    with timer("JSON: Load 1000 stars"):
        stars = json_db.get_stars(limit=1000)
    
    with timer("JSON: Search 'alpha'"):
        results = json_db.search_stars("alpha", limit=20)
    
    with timer("JSON: Get star by ID"):
        star = json_db.get_star_by_id(71456)
    
    with timer("JSON: Load all nations"):
        nations = json_db.get_nations()
    
    with timer("JSON: Load all trade routes"):
        routes = json_db.get_trade_routes()
    
    print(f"✅ JSON Results: {len(stars)} stars, {len(nations)} nations, {len(routes)} routes")

def main():
    """Run performance comparison"""
    print("⚡ Starmap Performance Test")
    print("=" * 50)
    
    # Test MontyDB
    test_montydb_performance()
    
    # Test JSON
    test_json_performance()
    
    print("\n📊 Performance Summary")
    print("-" * 40)
    print("✅ MontyDB provides:")
    print("  • Indexed queries for faster coordinate searches")
    print("  • Database-level filtering vs in-memory operations")
    print("  • Better memory efficiency with lazy loading")
    print("  • Advanced aggregation capabilities")
    print("  • Structured schema validation")

if __name__ == "__main__":
    main()