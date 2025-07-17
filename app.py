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