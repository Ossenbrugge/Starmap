/**
 * Starmap V2 - Streamlined JavaScript
 * Clean, efficient 3D starmap with modern features
 */

class StarmapApp {
    constructor() {
        this.currentStars = [];
        this.nations = [];
        this.tradeRoutes = [];
        this.plot = null;
        this.selectedStar = null;
        
        // Configuration
        this.config = {
            maxStars: 1000,
            maxMagnitude: 8.0,
            spectralType: '',
            overlays: {
                nations: false,
                tradeRoutes: false,
                stellarRegions: false,
                galacticDirections: false
            }
        };
        
        this.init();
    }
    
    async init() {
        this.showStatus('Initializing Starmap V2...', 'info');
        this.setupEventListeners();
        await this.loadInitialData();
        this.createStarmap();
        this.showStatus('Ready! Click on stars to explore the universe.', 'success');
    }
    
    setupEventListeners() {
        // Search
        document.getElementById('searchInput').addEventListener('input', this.debounce(() => {
            this.performSearch();
        }, 300));
        
        // Filters
        document.getElementById('magLimit').addEventListener('input', (e) => {
            document.getElementById('magValue').textContent = e.target.value;
        });
        
        // Overlays
        document.getElementById('nationsOverlay').addEventListener('change', (e) => {
            this.config.overlays.nations = e.target.checked;
            this.updateOverlays();
        });
        
        document.getElementById('tradeRoutesOverlay').addEventListener('change', (e) => {
            this.config.overlays.tradeRoutes = e.target.checked;
            this.updateOverlays();
        });
        
        document.getElementById('stellarRegionsOverlay').addEventListener('change', (e) => {
            this.config.overlays.stellarRegions = e.target.checked;
            this.updateOverlays();
        });
        
        document.getElementById('galacticDirectionsOverlay').addEventListener('change', (e) => {
            this.config.overlays.galacticDirections = e.target.checked;
            this.updateOverlays();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hideStarDetails();
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
        });
    }
    
    async loadInitialData() {
        try {
            // Load stats first
            const statsResponse = await fetch('/api/stats');
            const statsData = await statsResponse.json();
            if (statsData.success) {
                this.updateStats(statsData.data);
            }
            
            // Load nations for overlays
            const nationsResponse = await fetch('/api/nations');
            const nationsData = await nationsResponse.json();
            if (nationsData.success) {
                this.nations = nationsData.data;
            }
            
            // Load initial star data
            await this.loadStars();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showStatus('Error loading data. Please refresh the page.', 'danger');
        }
    }
    
    async loadStars() {
        this.showStatus('Loading stars...', 'info');
        
        try {
            const limit = document.getElementById('starLimit').value;
            const magLimit = document.getElementById('magLimit').value;
            const spectralType = document.getElementById('spectralType').value;
            
            const url = `/api/stars?limit=${limit}&mag_limit=${magLimit}&spectral_type=${spectralType}`;
            console.log('Loading stars from:', url);
            
            const response = await fetch(url);
            const data = await response.json();
            
            console.log('Stars API response:', data);
            
            if (data.success) {
                this.currentStars = data.data;
                console.log('Loaded stars:', this.currentStars.length, 'First star:', this.currentStars[0]);
                this.showStatus(`Loaded ${this.currentStars.length} stars`, 'success');
                return true;
            } else {
                throw new Error(data.error || 'Failed to load stars');
            }
        } catch (error) {
            console.error('Error loading stars:', error);
            this.showStatus('Error loading stars: ' + error.message, 'danger');
            return false;
        }
    }
    
    createStarmap() {
        console.log('Creating starmap with', this.currentStars.length, 'stars');
        
        if (!this.currentStars.length) {
            this.showStatus('No star data available', 'warning');
            return;
        }
        
        // Filter out stars with invalid coordinates
        const validStars = this.currentStars.filter(star => 
            star.x != null && star.y != null && star.z != null &&
            !isNaN(star.x) && !isNaN(star.y) && !isNaN(star.z)
        );
        
        console.log('Valid stars after filtering:', validStars.length);
        console.log('Sample valid star:', validStars[0]);
        
        if (!validStars.length) {
            this.showStatus('No stars with valid coordinates', 'warning');
            return;
        }
        
        // Prepare data for Plotly
        const x = validStars.map(star => star.x);
        const y = validStars.map(star => star.y);
        const z = validStars.map(star => star.z);
        const colors = validStars.map(star => this.getStarColor(star));
        const sizes = validStars.map(star => this.getStarSize(star));
        const text = validStars.map(star => this.getStarTooltip(star));
        
        const trace = {
            x: x,
            y: y,
            z: z,
            mode: 'markers',
            type: 'scatter3d',
            name: 'Stars',
            marker: {
                size: sizes,
                color: colors,
                opacity: 0.8,
                line: {
                    color: 'rgba(255, 255, 255, 0.1)',
                    width: 0.5
                }
            },
            text: text,
            hovertemplate: '%{text}<extra></extra>',
            customdata: validStars.map((star, index) => index)
        };
        
        const layout = {
            title: {
                text: 'Interactive 3D Starmap',
                font: { color: '#ffffff', size: 18 }
            },
            scene: {
                xaxis: { 
                    title: 'X (parsecs)', 
                    color: '#ffffff',
                    gridcolor: 'rgba(255, 255, 255, 0.1)',
                    showbackground: false,
                    autorange: true
                },
                yaxis: { 
                    title: 'Y (parsecs)', 
                    color: '#ffffff',
                    gridcolor: 'rgba(255, 255, 255, 0.1)',
                    showbackground: false,
                    autorange: true
                },
                zaxis: { 
                    title: 'Z (parsecs)', 
                    color: '#ffffff',
                    gridcolor: 'rgba(255, 255, 255, 0.1)',
                    showbackground: false,
                    autorange: true
                },
                bgcolor: 'rgba(0, 0, 0, 0)',
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            },
            paper_bgcolor: 'rgba(0, 0, 0, 0)',
            plot_bgcolor: 'rgba(0, 0, 0, 0)',
            font: { color: '#ffffff' },
            margin: { l: 0, r: 0, t: 40, b: 0 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d'],
            displaylogo: false
        };
        
        Plotly.newPlot('starmap', [trace], layout, config).then(() => {
            // Add click event listener
            document.getElementById('starmap').on('plotly_click', (data) => {
                if (data.points && data.points.length > 0) {
                    const pointIndex = data.points[0].customdata;
                    this.selectStar(validStars[pointIndex]);
                }
            });
            
            this.plot = document.getElementById('starmap');
            this.updateOverlays();
            this.showStatus(`Displaying ${validStars.length} stars in 3D space`, 'success');
        }).catch(error => {
            console.error('Error creating starmap:', error);
            this.showStatus('Error creating 3D visualization', 'danger');
        });
    }
    
    getStarColor(star) {
        // Color by nation if nations overlay is active
        if (this.config.overlays.nations && star.nation) {
            return star.nation.color;
        }
        
        // Fictional stars get a special color
        if (star.is_fictional) {
            return '#ff6b6b'; // Bright red for fictional stars
        }
        
        // Stars with exoplanets get a special tint
        if (star.has_planets || star.exoplanet_count > 0) {
            return '#4ecdc4'; // Teal for stars with planets
        }
        
        // Default color by spectral type
        const spectralClass = star.spectral_class || '';
        const spectral = spectralClass.length > 0 ? spectralClass[0].toUpperCase() : 'G';
        const colors = {
            'O': '#9bb0ff', 'B': '#aabfff', 'A': '#cad7ff',
            'F': '#f8f7ff', 'G': '#fff4ea', 'K': '#ffd2a1', 'M': '#ffad51'
        };
        return colors[spectral] || '#fff4ea';
    }
    
    getStarSize(star) {
        // Special handling for Sol
        if (star.name === 'Sol' || star.id === 0) {
            return 15; // Make Sol very prominent
        }
        
        // Special handling for important fictional stars
        if (star.fictional_name === 'Tiefe-Grenze Tor' || star.id === 999999) {
            return 12; // Make Tiefe-Grenze Tor prominent
        }
        
        // Make fictional stars more prominent
        if (star.is_fictional) {
            return 10; // Make fictional stars prominent
        }
        
        // Stars with exoplanets are slightly larger
        if (star.has_planets || star.exoplanet_count > 0) {
            const mag = star.magnitude || 8.0;
            return Math.max(4, Math.min(12, 17 - mag * 2));
        }
        
        // Convert magnitude to size (brighter stars = larger size)
        const mag = star.magnitude || 8.0;
        return Math.max(2, Math.min(12, 15 - mag * 2));
    }
    
    getStarTooltip(star) {
        let tooltip = `<b>${star.fictional_name || star.name || 'Unknown Star'}</b><br>`;
        tooltip += `Magnitude: ${(star.magnitude || 0).toFixed(2)}<br>`;
        tooltip += `Spectral: ${star.spectral_class || 'Unknown'}<br>`;
        tooltip += `Distance: ${(star.distance || 0).toFixed(1)} pc<br>`;
        tooltip += `Constellation: ${star.constellation_full || star.constellation || 'Unknown'}`;
        
        if (star.nation) {
            tooltip += `<br><b>Controlled by: ${star.nation.name}</b>`;
        }
        
        if (star.has_planets) {
            tooltip += `<br>🪐 ${star.exoplanet_count || 0} planet(s)`;
        }
        
        return tooltip;
    }
    
    async selectStar(star) {
        this.selectedStar = star;
        this.showStatus(`Loading details for ${star.fictional_name || star.name}...`, 'info');
        
        try {
            const response = await fetch(`/api/star/${star.id}`);
            const data = await response.json();
            
            if (data.success) {
                this.showStarDetails(data.data);
                this.showStatus(`Selected: ${star.fictional_name || star.name}`, 'success');
            } else {
                throw new Error(data.error || 'Failed to load star details');
            }
        } catch (error) {
            console.error('Error loading star details:', error);
            this.showStatus('Error loading star details', 'danger');
        }
    }
    
    showStarDetails(star) {
        const panel = document.getElementById('starDetails');
        const content = document.getElementById('starDetailsContent');
        
        let html = `
            <h6 class="text-primary">${star.fictional_data?.name || star.name}</h6>
            ${star.fictional_data?.name ? `<p class="small text-muted">${star.name}</p>` : ''}
            
            <div class="row">
                <div class="col-6">
                    <strong>Magnitude:</strong><br>
                    <span class="text-info">${(star.magnitude || 0).toFixed(2)}</span>
                </div>
                <div class="col-6">
                    <strong>Distance:</strong><br>
                    <span class="text-info">${(star.distance || 0).toFixed(1)} pc</span>
                </div>
            </div>
            
            <div class="row mt-2">
                <div class="col-6">
                    <strong>Spectral Class:</strong><br>
                    <span class="text-warning">${star.spectral_class || 'Unknown'}</span>
                </div>
                <div class="col-6">
                    <strong>Constellation:</strong><br>
                    <span class="text-success">${star.constellation_full || star.constellation || 'Unknown'}</span>
                </div>
            </div>
            
            <div class="mt-3">
                <strong>Coordinates:</strong><br>
                <small class="text-muted">
                    RA: ${(star.ra || 0).toFixed(3)}° | Dec: ${(star.dec || 0).toFixed(3)}°<br>
                    XYZ: (${(star.x || 0).toFixed(1)}, ${(star.y || 0).toFixed(1)}, ${(star.z || 0).toFixed(1)})
                </small>
            </div>
        `;
        
        if (star.fictional_data?.description) {
            html += `
                <div class="mt-3 p-2 bg-warning bg-opacity-10 rounded">
                    <small><strong>Fictional Universe:</strong><br>
                    ${star.fictional_data.description}</small>
                </div>
            `;
        }
        
        if (star.nation) {
            html += `
                <div class="mt-3 p-2 rounded" style="background-color: ${star.nation.color}20; border-left: 3px solid ${star.nation.color}">
                    <strong>Political Control:</strong><br>
                    <span style="color: ${star.nation.color}">${star.nation.name}</span><br>
                    <small class="text-muted">Capital: ${star.nation.capital_system}</small>
                </div>
            `;
        }
        
        if (star.habitability?.has_planets) {
            html += `
                <div class="mt-3 p-2 bg-info bg-opacity-10 rounded">
                    <strong>Planetary System:</strong><br>
                    🪐 ${star.habitability.planet_count} confirmed planet(s)
                </div>
            `;
        }
        
        content.innerHTML = html;
        panel.style.display = 'block';
        
        // Add minimap for planetary orbits
        this.createPlanetaryMinimap(star);
    }
    
    async createPlanetaryMinimap(star) {
        try {
            // Load both fictional and real exoplanets to see if this star has any
            const [fictionalResponse, realResponse] = await Promise.all([
                fetch('/api/fictional-exoplanets'),
                fetch('/api/exoplanets')
            ]);
            
            const fictionalData = await fictionalResponse.json();
            const realData = await realResponse.json();
            
            if (!fictionalData.success || !realData.success) return;
            
            // Find planets for this star
            const fictionalPlanets = fictionalData.data.filter(planet => planet.star_id === star.id);
            const realPlanets = realData.data.filter(planet => {
                // Try to match by star name or ID
                return planet.host_star === star.name || 
                       planet.host_star === star.fictional_name ||
                       planet.star_id === star.id;
            });
            
            const starPlanets = [...fictionalPlanets, ...realPlanets];
            
            // Only show minimap if star has planets
            if (starPlanets.length === 0 && !star.has_planets) return;
            
            // Add minimap section to the star details
            const content = document.getElementById('starDetailsContent');
            const minimapHtml = `
                <div class="mt-3 p-2 bg-secondary bg-opacity-10 rounded">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong>System Overview</strong>
                        <small class="text-muted">${starPlanets.length} planet(s)</small>
                    </div>
                    <canvas id="planetaryMinimap" width="250" height="150" style="background: #1a1a1a; border-radius: 4px; width: 100%; height: auto;"></canvas>
                </div>
            `;
            
            content.innerHTML += minimapHtml;
            
            // Draw the minimap
            const canvas = document.getElementById('planetaryMinimap');
            const ctx = canvas.getContext('2d');
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw star at center
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const starRadius = 8;
            
            // Draw star
            ctx.beginPath();
            ctx.arc(centerX, centerY, starRadius, 0, 2 * Math.PI);
            ctx.fillStyle = this.getStarColor(star);
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Draw star label
            ctx.fillStyle = '#ffffff';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(star.fictional_name || star.name, centerX, centerY - starRadius - 5);
            
            if (starPlanets.length > 0) {
                // Sort planets by orbital distance
                const sortedPlanets = starPlanets.sort((a, b) => {
                    const aDistance = a.semi_major_axis || (a.orbital_period ? Math.pow(a.orbital_period / 365.25, 2/3) : 1);
                    const bDistance = b.semi_major_axis || (b.orbital_period ? Math.pow(b.orbital_period / 365.25, 2/3) : 1);
                    return aDistance - bDistance;
                });
                
                // Draw orbital rings and planets
                sortedPlanets.forEach((planet, index) => {
                    const orbitRadius = 20 + (index * 15); // Scale orbit radii
                    
                    // Draw orbital ring
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, orbitRadius, 0, 2 * Math.PI);
                    ctx.strokeStyle = '#444444';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                    
                    // Planet position (simplified - just place at right side of orbit)
                    const planetX = centerX + orbitRadius;
                    const planetY = centerY;
                    
                    // Planet size based on radius
                    const planetRadius = planet.planet_radius_earth 
                        ? Math.max(2, Math.min(5, planet.planet_radius_earth * 1.5))
                        : 3;
                    
                    // Planet color
                    let planetColor = '#4CAF50'; // Default green
                    if (planet.potentially_habitable) {
                        planetColor = '#2196F3'; // Blue for habitable
                    } else if (planet.equilibrium_temperature > 373) {
                        planetColor = '#FF5722'; // Red for hot
                    } else if (planet.equilibrium_temperature < 273) {
                        planetColor = '#9C27B0'; // Purple for cold
                    }
                    
                    // Draw planet
                    ctx.beginPath();
                    ctx.arc(planetX, planetY, planetRadius, 0, 2 * Math.PI);
                    ctx.fillStyle = planetColor;
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                    
                    // Planet label
                    ctx.fillStyle = '#ffffff';
                    ctx.font = '8px Arial';
                    ctx.textAlign = 'left';
                    ctx.fillText(planet.name, planetX + planetRadius + 3, planetY + 2);
                    
                    // Distance label
                    ctx.fillStyle = '#999999';
                    ctx.font = '6px Arial';
                    ctx.textAlign = 'left';
                    const distance = planet.semi_major_axis || 'Unknown';
                    ctx.fillText(distance !== 'Unknown' ? `${distance.toFixed(2)} AU` : 'Unknown AU', planetX + planetRadius + 3, planetY + 10);
                });
            } else {
                // No detailed planet data, just show generic info
                ctx.fillStyle = '#999999';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('No detailed orbital data available', centerX, centerY + 30);
            }
            
        } catch (error) {
            console.error('Error creating planetary minimap:', error);
        }
    }
    
    hideStarDetails() {
        document.getElementById('starDetails').style.display = 'none';
        this.selectedStar = null;
    }
    
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const resultsDiv = document.getElementById('searchResults');
        
        if (!query) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        if (query.length < 2) return;
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();
            
            if (data.success && data.data.length > 0) {
                let html = '';
                data.data.forEach(star => {
                    html += `
                        <div class="search-result-item" onclick="app.selectStarFromSearch(${star.id})">
                            <div class="fw-bold">${star.fictional_name || star.name}</div>
                            <small class="text-muted">${star.constellation_full} | ${star.spectral_class}</small>
                        </div>
                    `;
                });
                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = '<div class="p-2 text-muted">No results found</div>';
            }
        } catch (error) {
            console.error('Search error:', error);
            resultsDiv.innerHTML = '<div class="p-2 text-danger">Search error</div>';
        }
    }
    
    async selectStarFromSearch(starId) {
        const star = this.currentStars.find(s => s.id === starId);
        if (star) {
            this.selectStar(star);
            document.getElementById('searchResults').innerHTML = '';
            document.getElementById('searchInput').value = '';
            
            // Highlight the selected star on the main starmap
            this.highlightStarOnMap(star);
        }
    }
    
    highlightStarOnMap(star) {
        if (!this.plot) return;
        
        // Create a temporary highlight marker
        const highlightTrace = {
            x: [star.x],
            y: [star.y],
            z: [star.z],
            mode: 'markers',
            type: 'scatter3d',
            name: 'Selected Star',
            marker: {
                size: 20,
                color: '#FFD700', // Gold color
                opacity: 0.8,
                symbol: 'circle-open',
                line: {
                    color: '#FFD700',
                    width: 3
                }
            },
            showlegend: false,
            hovertemplate: `<b>Selected: ${star.fictional_name || star.name}</b><extra></extra>`
        };
        
        // Remove any existing highlight
        this.removeHighlight();
        
        // Add the highlight marker
        Plotly.addTraces(this.plot, [highlightTrace]);
        
        // Store reference to highlight for cleanup
        this.highlightTraceIndex = this.plot.data.length - 1;
        
        // Center the view on the selected star (more gently)
        Plotly.relayout(this.plot, {
            'scene.camera': {
                eye: { 
                    x: star.x / 100 + 1.5, 
                    y: star.y / 100 + 1.5, 
                    z: star.z / 100 + 1.5 
                }
            }
        });
        
        // Auto-remove highlight after 5 seconds
        setTimeout(() => {
            this.removeHighlight();
        }, 5000);
    }
    
    removeHighlight() {
        if (this.plot && this.highlightTraceIndex !== undefined) {
            try {
                Plotly.deleteTraces(this.plot, [this.highlightTraceIndex]);
                this.highlightTraceIndex = undefined;
            } catch (error) {
                // Trace might already be removed
            }
        }
    }
    
    async applyFilters() {
        this.showStatus('Applying filters...', 'info');
        
        if (await this.loadStars()) {
            this.createStarmap();
        }
    }
    
    updateOverlays() {
        if (!this.plot) return;
        
        // First clear all overlay traces
        this.hideOverlayTraces();
        
        // Update star colors based on overlay settings
        this.updateStarColors();
        
        // Show active overlays
        if (this.config.overlays.tradeRoutes) {
            this.showTradeRoutes();
        }
        
        if (this.config.overlays.stellarRegions) {
            this.showStellarRegions();
        }
        
        if (this.config.overlays.galacticDirections) {
            this.showGalacticDirections();
        }
        
        // Handle nations overlay with spheres
        if (this.config.overlays.nations) {
            this.showNationSpheres();
        }
        
        // Show fictional exoplanets if they exist
        this.showFictionalExoplanets();
    }
    
    updateStarColors() {
        if (!this.plot || !this.currentStars.length) return;
        
        // Filter valid stars again
        const validStars = this.currentStars.filter(star => 
            star.x != null && star.y != null && star.z != null &&
            !isNaN(star.x) && !isNaN(star.y) && !isNaN(star.z)
        );
        
        const colors = validStars.map(star => this.getStarColor(star));
        
        // Update the plot colors
        Plotly.restyle(this.plot, {
            'marker.color': [colors]
        }, [0]);
    }
    
    async showTradeRoutes() {
        if (!this.plot || this.tradeRoutes.length === 0) {
            try {
                const response = await fetch('/api/trade-routes');
                const data = await response.json();
                if (data.success) {
                    this.tradeRoutes = data.data;
                }
            } catch (error) {
                console.error('Error loading trade routes:', error);
                return;
            }
        }
        
        // Create trade route traces
        const traceUpdates = [];
        
        this.tradeRoutes.forEach(route => {
            const fromStar = this.currentStars.find(s => s.id === route.endpoints.from.star_id);
            const toStar = this.currentStars.find(s => s.id === route.endpoints.to.star_id);
            
            if (fromStar && toStar) {
                // Color code routes by nation/category
                let routeColor = '#00ff88'; // Default green
                let routeWidth = 3;
                
                if (route.category === 'terran_primary_routes') {
                    routeColor = '#1565C0'; // Terran blue
                } else if (route.category === 'felgenland_routes') {
                    routeColor = '#F44336'; // Felgenland red
                } else if (route.category === 'protelani_routes') {
                    routeColor = '#00BCD4'; // Protelani cyan
                } else if (route.category === 'dorsai_routes') {
                    routeColor = '#BDBDBD'; // Dorsai gray
                } else if (route.category === 'pentothian_routes') {
                    routeColor = '#9C27B0'; // Pentothian purple
                }
                
                // Special routes get thicker lines
                if (route.route_type === 'Primary Trade' || route.route_type === 'Military Alliance') {
                    routeWidth = 4;
                }
                
                const trace = {
                    x: [fromStar.x, toStar.x],
                    y: [fromStar.y, toStar.y],
                    z: [fromStar.z, toStar.z],
                    mode: 'lines',
                    type: 'scatter3d',
                    name: route.name,
                    line: {
                        color: routeColor,
                        width: routeWidth
                    },
                    hovertemplate: `<b>${route.name}</b><br>From: ${route.endpoints.from.system}<br>To: ${route.endpoints.to.system}<br>Type: ${route.route_type}<extra></extra>`
                };
                traceUpdates.push(trace);
            }
        });
        
        if (traceUpdates.length > 0) {
            Plotly.addTraces(this.plot, traceUpdates);
        }
    }
    
    async showStellarRegions() {
        if (!this.plot) return;
        
        try {
            const response = await fetch('/api/stellar-regions');
            const data = await response.json();
            if (!data.success) {
                console.error('Error loading stellar regions:', data.error);
                return;
            }
            
            // Create stellar region octants
            const regionTraces = [];
            
            data.data.forEach(region => {
                // Create octant boundaries using mesh3d
                // Stellar regions are already properly centered on Sol (0,0,0)
                // No coordinate transformation needed - use regions as-is
                const x_range = region.x_range; // Use coordinates directly
                const y_range = region.y_range;
                const z_range = region.z_range;
                
                // Define the 8 corners of the octant
                const vertices = [
                    [x_range[0], y_range[0], z_range[0]], // 0
                    [x_range[1], y_range[0], z_range[0]], // 1
                    [x_range[1], y_range[1], z_range[0]], // 2
                    [x_range[0], y_range[1], z_range[0]], // 3
                    [x_range[0], y_range[0], z_range[1]], // 4
                    [x_range[1], y_range[0], z_range[1]], // 5
                    [x_range[1], y_range[1], z_range[1]], // 6
                    [x_range[0], y_range[1], z_range[1]]  // 7
                ];
                
                // Create wireframe edges for the octant
                const edges = [
                    [0, 1], [1, 2], [2, 3], [3, 0], // bottom face
                    [4, 5], [5, 6], [6, 7], [7, 4], // top face
                    [0, 4], [1, 5], [2, 6], [3, 7]  // vertical edges
                ];
                
                // Create lines for each edge
                edges.forEach((edge, index) => {
                    const start = vertices[edge[0]];
                    const end = vertices[edge[1]];
                    
                    const trace = {
                        x: [start[0], end[0], null],
                        y: [start[1], end[1], null],
                        z: [start[2], end[2], null],
                        mode: 'lines',
                        type: 'scatter3d',
                        name: index === 0 ? region.short_name : '', // Only show name for first edge
                        showlegend: index === 0,
                        line: {
                            color: region.color,
                            width: 2
                        },
                        hovertemplate: `<b>${region.name}</b><br>${region.description}<br>Octant ${region.octant_number}<extra></extra>`
                    };
                    regionTraces.push(trace);
                });
                
                // Add center point marker
                const centerTrace = {
                    x: [region.center[0]],
                    y: [region.center[1]],
                    z: [region.center[2]],
                    mode: 'markers+text',
                    type: 'scatter3d',
                    name: `${region.short_name} Center`,
                    showlegend: false,
                    marker: {
                        size: 6,
                        color: region.color,
                        opacity: 0.8,
                        symbol: 'diamond'
                    },
                    text: region.short_name,
                    textposition: 'middle center',
                    textfont: {
                        size: 10,
                        color: region.color
                    },
                    hovertemplate: `<b>${region.name}</b><br>Center: (${region.center[0]}, ${region.center[1]}, ${region.center[2]})<br>Brightest: ${region.brightest_star}<extra></extra>`
                };
                regionTraces.push(centerTrace);
            });
            
            if (regionTraces.length > 0) {
                Plotly.addTraces(this.plot, regionTraces);
            }
        } catch (error) {
            console.error('Error loading stellar regions:', error);
        }
    }
    
    async showGalacticDirections() {
        if (!this.plot) return;
        
        try {
            const response = await fetch('/api/galactic-directions');
            const data = await response.json();
            if (!data.success) {
                console.error('Error loading galactic directions:', data.error);
                return;
            }
            
            // Create directional markers
            const directionTraces = [];
            
            data.data.forEach(direction => {
                const trace = {
                    x: [direction.position[0]],
                    y: [direction.position[1]],
                    z: [direction.position[2]],
                    mode: 'markers+text',
                    type: 'scatter3d',
                    name: direction.name,
                    marker: {
                        size: 12,
                        color: direction.color,
                        opacity: 0.8,
                        symbol: 'diamond',
                        line: {
                            color: '#ffffff',
                            width: 2
                        }
                    },
                    text: direction.name,
                    textposition: 'middle center',
                    textfont: {
                        size: 12,
                        color: '#ffffff'
                    },
                    showlegend: true,
                    hovertemplate: `<b>${direction.name}</b><br>Galactic Direction<extra></extra>`
                };
                directionTraces.push(trace);
            });
            
            if (directionTraces.length > 0) {
                Plotly.addTraces(this.plot, directionTraces);
            }
        } catch (error) {
            console.error('Error loading galactic directions:', error);
        }
    }
    
    async showNationSpheres() {
        if (!this.plot || !this.nations.length) return;
        
        try {
            // Create spheres for each nation's territory
            const sphereTraces = [];
            
            this.nations.forEach(nation => {
                // Find all stars belonging to this nation
                const nationStars = this.currentStars.filter(star => 
                    star.nation && star.nation.id === nation.id
                );
                
                if (nationStars.length === 0) return;
                
                // Calculate the centroid and average distance for the sphere
                let centerX = 0, centerY = 0, centerZ = 0;
                let maxDistance = 0;
                
                nationStars.forEach(star => {
                    centerX += star.x;
                    centerY += star.y;
                    centerZ += star.z;
                });
                
                centerX /= nationStars.length;
                centerY /= nationStars.length;
                centerZ /= nationStars.length;
                
                // Calculate radius as the maximum distance from center to any star
                nationStars.forEach(star => {
                    const distance = Math.sqrt(
                        Math.pow(star.x - centerX, 2) + 
                        Math.pow(star.y - centerY, 2) + 
                        Math.pow(star.z - centerZ, 2)
                    );
                    maxDistance = Math.max(maxDistance, distance);
                });
                
                // Add some padding to the radius
                const radius = Math.max(maxDistance * 1.2, 5);
                
                // Create sphere surface points
                const spherePoints = [];
                const density = 15; // Lower density for better performance
                
                for (let i = 0; i < density; i++) {
                    for (let j = 0; j < density; j++) {
                        const theta = (i / density) * Math.PI;
                        const phi = (j / density) * 2 * Math.PI;
                        
                        const x = centerX + radius * Math.sin(theta) * Math.cos(phi);
                        const y = centerY + radius * Math.sin(theta) * Math.sin(phi);
                        const z = centerZ + radius * Math.cos(theta);
                        
                        spherePoints.push({x, y, z});
                    }
                }
                
                // Create the sphere trace
                const trace = {
                    x: spherePoints.map(p => p.x),
                    y: spherePoints.map(p => p.y),
                    z: spherePoints.map(p => p.z),
                    mode: 'markers',
                    type: 'scatter3d',
                    name: `${nation.name} Territory`,
                    marker: {
                        size: 1,
                        color: nation.color,
                        opacity: 0.1,
                        line: {
                            color: nation.color,
                            width: 0
                        }
                    },
                    showlegend: false,
                    hovertemplate: `<b>${nation.name}</b><br>Territory Boundary<extra></extra>`
                };
                
                sphereTraces.push(trace);
            });
            
            if (sphereTraces.length > 0) {
                Plotly.addTraces(this.plot, sphereTraces);
            }
        } catch (error) {
            console.error('Error loading nation spheres:', error);
        }
    }
    
    async showFictionalExoplanets() {
        if (!this.plot) return;
        
        try {
            // Load both fictional and real exoplanets
            const [fictionalResponse, realResponse] = await Promise.all([
                fetch('/api/fictional-exoplanets'),
                fetch('/api/exoplanets')
            ]);
            
            const fictionalData = await fictionalResponse.json();
            const realData = await realResponse.json();
            
            if (!fictionalData.success || !realData.success) {
                console.error('Error loading exoplanets');
                return;
            }
            
            const fictionalExoplanets = fictionalData.data;
            const realExoplanets = realData.data;
            
            // Create exoplanet traces for both types
            const exoplanetTraces = [];
            
            // Process fictional exoplanets
            if (fictionalExoplanets.length > 0) {
                const fictionalTraces = this.createExoplanetTraces(fictionalExoplanets, 'fictional');
                exoplanetTraces.push(...fictionalTraces);
            }
            
            // Process real exoplanets
            if (realExoplanets.length > 0) {
                const realTraces = this.createExoplanetTraces(realExoplanets, 'real');
                exoplanetTraces.push(...realTraces);
            }
            
            if (exoplanetTraces.length > 0) {
                Plotly.addTraces(this.plot, exoplanetTraces);
                console.log(`Added ${exoplanetTraces.length / 2} exoplanets to the visualization`);
            }
        } catch (error) {
            console.error('Error loading exoplanets:', error);
        }
    }
    
    createExoplanetTraces(exoplanets, type) {
        const traces = [];
        
        // Group exoplanets by their host star
        const exoplanetsByHost = {};
        exoplanets.forEach(planet => {
            let hostId;
            if (type === 'fictional') {
                hostId = planet.star_id;
            } else {
                // For real exoplanets, match by star name
                hostId = this.findStarIdByName(planet.host_star.name);
            }
            
            if (hostId) {
                if (!exoplanetsByHost[hostId]) {
                    exoplanetsByHost[hostId] = [];
                }
                exoplanetsByHost[hostId].push(planet);
            }
        });
        
        Object.keys(exoplanetsByHost).forEach(hostId => {
            const hostStar = this.currentStars.find(star => star.id === parseInt(hostId));
            if (!hostStar) return;
            
            const planets = exoplanetsByHost[hostId];
            
            planets.forEach((planet, index) => {
                // Get orbital distance
                let orbitDistance;
                if (type === 'fictional') {
                    orbitDistance = planet.semi_major_axis || (planet.orbital_period ? Math.pow(planet.orbital_period / 365.25, 2/3) : 1);
                } else {
                    orbitDistance = planet.orbital_properties.semi_major_axis_au || 1;
                }
                
                // Scale orbit radius for visualization - much smaller scale to not interfere with star positions
                // Use logarithmic scaling to handle large orbital distances
                const orbitRadius = 0.1 + (Math.log(orbitDistance + 1) * 0.05); // Much smaller scale
                const orbitPoints = [];
                
                // Create circular orbit points
                for (let i = 0; i < 24; i++) {
                    const angle = (i / 24) * 2 * Math.PI;
                    const x = hostStar.x + orbitRadius * Math.cos(angle);
                    const y = hostStar.y + orbitRadius * Math.sin(angle);
                    const z = hostStar.z + orbitRadius * Math.sin(angle) * 0.1; // Slight z variation
                    
                    orbitPoints.push({x, y, z});
                }
                
                // Determine planet color based on properties
                let planetColor = '#4CAF50'; // Default green
                let planetName, planetRadius, planetMass, planetPeriod, isHabitable;
                
                if (type === 'fictional') {
                    planetName = planet.name;
                    planetRadius = planet.planet_radius_earth;
                    planetMass = planet.planet_mass_earth;
                    planetPeriod = planet.orbital_period;
                    isHabitable = planet.potentially_habitable;
                    
                    if (isHabitable) {
                        planetColor = '#2196F3'; // Blue for habitable
                    } else if (planet.equilibrium_temperature > 373) {
                        planetColor = '#FF5722'; // Red for hot
                    } else if (planet.equilibrium_temperature < 273) {
                        planetColor = '#9C27B0'; // Purple for cold
                    }
                } else {
                    planetName = planet.name;
                    planetRadius = planet.physical_properties.radius_earth;
                    planetMass = planet.physical_properties.mass_earth;
                    planetPeriod = planet.orbital_properties.period_days;
                    isHabitable = planet.habitability.potentially_habitable === 'True';
                    
                    if (isHabitable) {
                        planetColor = '#2196F3'; // Blue for habitable
                    } else if (planet.physical_properties.equilibrium_temperature_k > 373) {
                        planetColor = '#FF5722'; // Red for hot
                    } else if (planet.physical_properties.equilibrium_temperature_k < 273) {
                        planetColor = '#9C27B0'; // Purple for cold
                    } else {
                        planetColor = '#FFC107'; // Yellow for real exoplanets
                    }
                }
                
                // Create orbit trace
                const orbitTrace = {
                    x: orbitPoints.map(p => p.x),
                    y: orbitPoints.map(p => p.y),
                    z: orbitPoints.map(p => p.z),
                    mode: 'lines',
                    type: 'scatter3d',
                    name: `${planetName} Orbit`,
                    line: {
                        color: planetColor,
                        width: 1
                    },
                    showlegend: false,
                    hovertemplate: `<b>${planetName}</b><br>Host: ${hostStar.fictional_name || hostStar.name}<br>Orbital Period: ${planetPeriod ? planetPeriod.toFixed(1) + ' days' : 'Unknown'}<br>Type: ${type}<br>Habitable: ${isHabitable ? 'Yes' : 'No'}<extra></extra>`
                };
                
                // Create planet marker
                const planetTrace = {
                    x: [orbitPoints[0].x], // Position at first orbit point
                    y: [orbitPoints[0].y],
                    z: [orbitPoints[0].z],
                    mode: 'markers',
                    type: 'scatter3d',
                    name: planetName,
                    marker: {
                        size: planetRadius ? Math.max(2, Math.min(6, planetRadius * 2)) : 3,
                        color: planetColor,
                        opacity: 0.8,
                        line: {
                            color: '#ffffff',
                            width: 1
                        }
                    },
                    showlegend: false,
                    hovertemplate: `<b>${planetName}</b><br>Host: ${hostStar.fictional_name || hostStar.name}<br>Radius: ${planetRadius ? planetRadius.toFixed(2) + ' Earth radii' : 'Unknown'}<br>Mass: ${planetMass ? planetMass.toFixed(2) + ' Earth masses' : 'Unknown'}<br>Period: ${planetPeriod ? planetPeriod.toFixed(1) + ' days' : 'Unknown'}<br>Type: ${type}<extra></extra>`
                };
                
                traces.push(orbitTrace);
                traces.push(planetTrace);
            });
        });
        
        return traces;
    }
    
    findStarIdByName(starName) {
        // Try to find star by various name matches
        const star = this.currentStars.find(s => {
            if (s.name === starName || s.fictional_name === starName) return true;
            if (s.catalog_ids && s.catalog_ids.includes(starName)) return true;
            
            // Try partial matches for known systems
            if (starName.includes('Proxima') && s.name.includes('Proxima')) return true;
            if (starName.includes('20 LMi') && s.name.includes('20 LMi')) return true;
            if (starName.includes('Sol') && s.name === 'Sol') return true;
            
            return false;
        });
        
        return star ? star.id : null;
    }
    
    hideTradeRoutes() {
        if (!this.plot) return;
        
        // Remove all trade route traces (keep only the first trace which is stars)
        const currentTraces = this.plot.data.length;
        if (currentTraces > 1) {
            const indicesToRemove = [];
            for (let i = 1; i < currentTraces; i++) {
                indicesToRemove.push(i);
            }
            Plotly.deleteTraces(this.plot, indicesToRemove);
        }
    }
    
    hideOverlayTraces() {
        if (!this.plot) return;
        
        // Remove all overlay traces except the first one (stars)
        const currentTraces = this.plot.data.length;
        if (currentTraces > 1) {
            const indicesToRemove = [];
            for (let i = 1; i < currentTraces; i++) {
                indicesToRemove.push(i);
            }
            Plotly.deleteTraces(this.plot, indicesToRemove);
        }
    }
    
    async showNationsLegend() {
        const modal = new bootstrap.Modal(document.getElementById('nationsModal'));
        const content = document.getElementById('nationsContent');
        
        if (this.nations.length === 0) {
            content.innerHTML = '<p>Loading nations...</p>';
            modal.show();
            return;
        }
        
        let html = '<div class="row">';
        this.nations.forEach(nation => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="nation-item" style="border-left-color: ${nation.color}">
                        <h6 class="fw-bold" style="color: ${nation.color}">${nation.name}</h6>
                        <p class="small mb-2">${nation.description}</p>
                        <div class="small text-muted">
                            <strong>Government:</strong> ${nation.government_type}<br>
                            <strong>Capital:</strong> ${nation.capital_system}<br>
                            <strong>Population:</strong> ${nation.population}
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        content.innerHTML = html;
        modal.show();
    }
    
    resetView() {
        if (this.plot) {
            Plotly.relayout(this.plot, {
                'scene.camera': {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            });
            this.showStatus('View reset', 'info');
        }
    }
    
    exportData() {
        if (!this.currentStars.length) {
            this.showStatus('No data to export', 'warning');
            return;
        }
        
        const csv = this.generateCSV(this.currentStars);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `starmap_data_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showStatus('Data exported successfully', 'success');
    }
    
    generateCSV(stars) {
        const headers = ['id', 'name', 'fictional_name', 'x', 'y', 'z', 'magnitude', 'spectral_class', 'constellation', 'distance'];
        let csv = headers.join(',') + '\n';
        
        stars.forEach(star => {
            const row = headers.map(header => {
                const value = star[header] || '';
                return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
            });
            csv += row.join(',') + '\n';
        });
        
        return csv;
    }
    
    updateStats(stats) {
        const statsDiv = document.getElementById('stats');
        statsDiv.innerHTML = `
            <div class="small">
                ⭐ Stars: ${stats.stars.toLocaleString()}<br>
                🏛️ Nations: ${stats.nations}<br>
                🛣️ Trade Routes: ${stats.trade_routes}<br>
                🪐 Exoplanets: ${stats.exoplanets.toLocaleString()}
            </div>
        `;
    }
    
    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('status');
        statusDiv.className = `alert alert-${type} small mb-3`;
        statusDiv.textContent = message;
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                if (statusDiv.textContent === message) {
                    statusDiv.className = 'alert alert-info small mb-3';
                    statusDiv.textContent = 'Ready';
                }
            }, 3000);
        }
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Global functions for template onclick handlers
function searchStars() {
    app.performSearch();
}

function applyFilters() {
    app.applyFilters();
}

function showNationsLegend() {
    app.showNationsLegend();
}

function resetView() {
    app.resetView();
}

function exportData() {
    app.exportData();
}

function hideStarDetails() {
    app.hideStarDetails();
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new StarmapApp();
});