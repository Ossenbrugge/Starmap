#!/usr/bin/env python3
"""
Starmap - Felgenland Saga
3D Interactive starmap for the Felgenland Saga universe
Features real astronomical data enhanced with fictional political entities and trade networks
"""

from flask import Flask, request, jsonify, render_template
import json
import os
from models.database import Database
from controllers.api_controller import APIController

app = Flask(__name__)
app.secret_key = 'starmap_felgenland_saga_2024'

# Initialize database and controllers
db = Database()
api = APIController(db)

@app.route('/')
def index():
    """Main starmap page"""
    return render_template('starmap.html')

@app.route('/api/stars')
def get_stars():
    """Get star data with optional filtering"""
    limit = request.args.get('limit', 1000, type=int)
    mag_limit = request.args.get('mag_limit', 8.0, type=float)
    spectral_type = request.args.get('spectral_type', '')
    
    return api.get_stars(limit, mag_limit, spectral_type)

@app.route('/api/star/<int:star_id>')
def get_star_details(star_id):
    """Get detailed information for a specific star"""
    return api.get_star_details(star_id)

@app.route('/api/nations')
def get_nations():
    """Get all nations"""
    return api.get_nations()

@app.route('/api/trade-routes')
def get_trade_routes():
    """Get all trade routes"""
    return api.get_trade_routes()

@app.route('/api/search')
def search_stars():
    """Search stars by name"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    return api.search_stars(query, limit)

@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    return api.get_stats()

@app.route('/api/stellar-regions')
def get_stellar_regions():
    """Get stellar regions data"""
    return api.get_stellar_regions()

@app.route('/api/galactic-directions')
def get_galactic_directions():
    """Get galactic directions data"""
    return api.get_galactic_directions()

@app.route('/api/fictional-exoplanets')
def get_fictional_exoplanets():
    """Get fictional exoplanets data"""
    return api.get_fictional_exoplanets()

@app.route('/api/exoplanets')
def get_exoplanets():
    """Get exoplanets data"""
    return api.get_exoplanets()

# Fictional entity management endpoints

@app.route('/api/fictional/stars', methods=['GET'])
def get_fictional_stars():
    """Get all fictional stars"""
    return api.get_fictional_stars()

@app.route('/api/fictional/stars', methods=['POST'])
def add_fictional_star():
    """Add a new fictional star"""
    return api.add_fictional_star()

@app.route('/api/fictional/stars/<int:star_id>', methods=['DELETE'])
def delete_fictional_star(star_id):
    """Delete a fictional star"""
    return api.delete_fictional_star(star_id)

@app.route('/api/fictional/exoplanets', methods=['GET'])
def get_fictional_exoplanets_new():
    """Get all fictional exoplanets"""
    return api.get_fictional_exoplanets()

@app.route('/api/fictional/exoplanets', methods=['POST'])
def add_fictional_exoplanet():
    """Add a new fictional exoplanet"""
    return api.add_fictional_exoplanet()

@app.route('/api/fictional/nations', methods=['GET'])
def get_fictional_nations():
    """Get all fictional nations"""
    return api.get_fictional_nations()

@app.route('/api/fictional/nations', methods=['POST'])
def add_fictional_nation():
    """Add a new fictional nation"""
    return api.add_fictional_nation()

@app.route('/api/fictional/nations/<string:nation_id>', methods=['DELETE'])
def delete_fictional_nation(nation_id):
    """Delete a fictional nation"""
    return api.delete_fictional_nation(nation_id)

@app.route('/api/fictional/trade-routes', methods=['GET'])
def get_fictional_trade_routes():
    """Get all fictional trade routes"""
    return api.get_fictional_trade_routes()

@app.route('/api/fictional/trade-routes', methods=['POST'])
def add_fictional_trade_route():
    """Add a new fictional trade route"""
    return api.add_fictional_trade_route()

@app.route('/api/fictional/trade-routes/<string:route_id>', methods=['DELETE'])
def delete_fictional_trade_route(route_id):
    """Delete a fictional trade route"""
    return api.delete_fictional_trade_route(route_id)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Starmap - Felgenland Saga")
    print(f"📊 Database Stats: {db.get_stats()}")
    print("🌐 Access at: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)