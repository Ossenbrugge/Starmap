#!/usr/bin/env python3
"""
Starmap Application - Main Flask Web Application
Interactive 3D starmap for science fiction novels
"""

import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template, jsonify, request, send_file
import json
from datetime import datetime
import tempfile
from jinja2 import Template

# Try to import weasyprint, disable PDF export if not available
try:
    import weasyprint
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    print("WeasyPrint not available - PDF export disabled")
    PDF_EXPORT_AVAILABLE = False

app = Flask(__name__)

class StarmapApp:
    def __init__(self):
        self.stars_data = None
        self.load_star_data()
        
    def load_star_data(self):
        """Load star data from CSV file"""
        try:
            if os.path.exists("stars_output.csv"):
                self.stars_data = pd.read_csv("stars_output.csv")
                print(f"Loaded {len(self.stars_data)} stars from CSV")
                
                # Add sample planetary systems
                self.add_sample_planets()
            else:
                print("stars_output.csv not found!")
                self.stars_data = pd.DataFrame()
        except Exception as e:
            print(f"Error loading star data: {e}")
            self.stars_data = pd.DataFrame()
    
    def add_sample_planets(self):
        """Add sample planetary data"""
        # Sample planetary systems
        planet_systems = {
            0: [  # Sol
                {"name": "Mercury", "type": "Terrestrial", "distance_au": 0.39, "mass_earth": 0.055},
                {"name": "Venus", "type": "Terrestrial", "distance_au": 0.72, "mass_earth": 0.815},
                {"name": "Earth", "type": "Terrestrial", "distance_au": 1.0, "mass_earth": 1.0},
                {"name": "Mars", "type": "Terrestrial", "distance_au": 1.52, "mass_earth": 0.107}
            ],
            16496: [  # Epsilon Eridani
                {"name": "Epsilon Eridani b", "type": "Gas Giant", "distance_au": 3.4, "mass_earth": 317}
            ],
            70666: [  # Proxima Centauri
                {"name": "Proxima Centauri b", "type": "Terrestrial", "distance_au": 0.05, "mass_earth": 1.27},
                {"name": "Proxima Centauri c", "type": "Super-Earth", "distance_au": 1.5, "mass_earth": 6.0}
            ]
        }
        
        # Add planets column
        self.stars_data['planets'] = self.stars_data['id'].map(planet_systems).fillna('').apply(list)

starmap = StarmapApp()

@app.route('/')
def index():
    """Main starmap page"""
    return render_template('starmap.html')

@app.route('/api/stars')
def get_stars():
    """API endpoint to get star data"""
    try:
        # Limit to reasonable number of stars for performance
        stars_subset = starmap.stars_data.head(1000)
        
        # Convert to JSON-serializable format
        stars_json = []
        for _, star in stars_subset.iterrows():
            star_data = {
                'id': int(star['id']),
                'name': str(star.get('proper', '')),
                'x': float(star.get('x', 0)),
                'y': float(star.get('y', 0)), 
                'z': float(star.get('z', 0)),
                'mag': float(star.get('mag', 0)),
                'spect': str(star.get('spect', '')),
                'dist': float(star.get('dist', 0)),
                'planets': star.get('planets', [])
            }
            stars_json.append(star_data)
            
        return jsonify(stars_json)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/star/<int:star_id>')
def get_star_details(star_id):
    """Get detailed information for a specific star"""
    try:
        star = starmap.stars_data[starmap.stars_data['id'] == star_id]
        if star.empty:
            return jsonify({'error': 'Star not found'})
            
        star_data = star.iloc[0]
        details = {
            'id': int(star_data['id']),
            'name': str(star_data.get('proper', f'Star {star_id}')),
            'coordinates': {
                'x': float(star_data.get('x', 0)),
                'y': float(star_data.get('y', 0)),
                'z': float(star_data.get('z', 0))
            },
            'properties': {
                'magnitude': float(star_data.get('mag', 0)),
                'spectral_class': str(star_data.get('spect', '')),
                'distance': float(star_data.get('dist', 0)),
                'constellation': str(star_data.get('con', '')),
                'proper_motion_ra': float(star_data.get('pmra', 0)),
                'proper_motion_dec': float(star_data.get('pmdec', 0))
            },
            'planets': star_data.get('planets', [])
        }
        
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/starmap/plot')
def generate_starmap_plot():
    """Generate interactive 3D starmap plot"""
    try:
        # Get parameters
        mag_limit = float(request.args.get('mag_limit', 6.0))
        star_count = int(request.args.get('count', 500))
        
        # Filter stars
        bright_stars = starmap.stars_data[starmap.stars_data['mag'] <= mag_limit].head(star_count)
        
        # Create 3D scatter plot
        fig = go.Figure(data=[
            go.Scatter3d(
                x=bright_stars['x'],
                y=bright_stars['y'],
                z=bright_stars['z'],
                mode='markers',
                marker=dict(
                    size=3,
                    color=bright_stars['mag'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Magnitude")
                ),
                text=bright_stars.apply(lambda row: 
                    f"Name: {row.get('proper', 'Unknown')}<br>"
                    f"Magnitude: {row.get('mag', 'N/A')}<br>"
                    f"Distance: {row.get('dist', 'N/A')} pc<br>"
                    f"Spectral Class: {row.get('spect', 'N/A')}", axis=1),
                hovertemplate='%{text}<extra></extra>',
                customdata=bright_stars['id']
            )
        ])
        
        fig.update_layout(
            title="Interactive 3D Starmap",
            scene=dict(
                xaxis_title="X (parsecs)",
                yaxis_title="Y (parsecs)",
                zaxis_title="Z (parsecs)",
                bgcolor='black'
            ),
            paper_bgcolor='black',
            font=dict(color='white')
        )
        
        return fig.to_json()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export/pdf')
def export_pdf():
    """Export starmap as PDF"""
    if not PDF_EXPORT_AVAILABLE:
        return jsonify({'error': 'PDF export not available - WeasyPrint not installed'})
    
    try:
        # Create a simple HTML template for PDF
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Starmap Export</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .star-table { width: 100%; border-collapse: collapse; }
                .star-table th, .star-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .star-table th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Starmap Data Export</h1>
            <p>Generated on: {{ date }}</p>
            <h2>Bright Stars (Magnitude ≤ 6.0)</h2>
            <table class="star-table">
                <tr>
                    <th>Name</th>
                    <th>Magnitude</th>
                    <th>Distance (pc)</th>
                    <th>Spectral Class</th>
                    <th>Constellation</th>
                </tr>
                {% for star in stars %}
                <tr>
                    <td>{{ star.name }}</td>
                    <td>{{ star.mag }}</td>
                    <td>{{ star.dist }}</td>
                    <td>{{ star.spect }}</td>
                    <td>{{ star.con }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        
        # Get bright stars
        bright_stars = starmap.stars_data[starmap.stars_data['mag'] <= 6.0].head(100)
        
        # Prepare data for template
        stars_for_template = []
        for _, star in bright_stars.iterrows():
            stars_for_template.append({
                'name': star.get('proper', 'Unknown'),
                'mag': star.get('mag', 'N/A'),
                'dist': star.get('dist', 'N/A'),
                'spect': star.get('spect', 'N/A'),
                'con': star.get('con', 'N/A')
            })
        
        # Render HTML
        template = Template(html_template)
        html_content = template.render(
            stars=stars_for_template,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            weasyprint.HTML(string=html_content).write_pdf(tmp_file.name)
            return send_file(tmp_file.name, as_attachment=True, download_name='starmap_export.pdf')
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)