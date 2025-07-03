// Starmap JavaScript Functionality

let currentStars = [];
let starmapPlot = null;
let highlightedStarId = null;
let highlightTrace = null;
let distanceMeasurementMode = false;
let selectedStarsForDistance = [];
let distanceTrace = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    updateStarmap(); // Load initial starmap
});

function setupEventListeners() {
    // Range slider updates
    document.getElementById('magLimit').addEventListener('input', function() {
        document.getElementById('magValue').textContent = this.value;
    });
    
    document.getElementById('starCount').addEventListener('input', function() {
        document.getElementById('countValue').textContent = this.value;
    });
    
    // Search on Enter key
    document.getElementById('starSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchStars();
        }
    });
}

function updateStatus(message, isLoading = false) {
    const statusBar = document.getElementById('statusBar');
    if (isLoading) {
        statusBar.innerHTML = `<div class="loading"></div>${message}`;
        statusBar.className = 'alert alert-warning';
    } else {
        statusBar.innerHTML = message;
        statusBar.className = 'alert alert-info';
    }
}

async function updateStarmap() {
    const magLimit = document.getElementById('magLimit').value;
    const starCount = document.getElementById('starCount').value;
    
    updateStatus('Loading starmap...', true);
    
    try {
        // Fetch star data
        const response = await fetch('/api/stars');
        if (!response.ok) throw new Error('Failed to fetch star data');
        
        currentStars = await response.json();
        
        // Filter stars based on parameters
        let filteredStars = currentStars
            .filter(star => star.mag <= parseFloat(magLimit))
            .slice(0, parseInt(starCount));
        
        // Create 3D scatter plot
        const trace = {
            x: filteredStars.map(star => star.x),
            y: filteredStars.map(star => star.y),
            z: filteredStars.map(star => star.z),
            mode: 'markers',
            type: 'scatter3d',
            marker: {
                size: filteredStars.map(star => Math.max(2, 8 - star.mag)), // Brighter stars are bigger
                color: filteredStars.map(star => star.mag),
                colorscale: [
                    [0, '#ffffff'],      // Bright stars - white
                    [0.3, '#ffff99'],    // Yellow
                    [0.6, '#ff9933'],    // Orange
                    [1, '#ff3333']       // Dim stars - red
                ],
                colorbar: {
                    title: 'Magnitude',
                    titleside: 'right'
                },
                opacity: 0.8
            },
            text: filteredStars.map(star => 
                `${star.name}<br>` +
                `${star.designation_type === 'proper' ? 'Common Name' : 'Designation'}: ${star.designation_type}<br>` +
                `Constellation: ${star.constellation_full || star.constellation}<br>` +
                `Magnitude: ${star.mag.toFixed(2)}<br>` +
                `Distance: ${star.dist.toFixed(2)} pc<br>` +
                `Spectral Class: ${star.spect}<br>` +
                `Coordinates: (${star.x.toFixed(2)}, ${star.y.toFixed(2)}, ${star.z.toFixed(2)})`
            ),
            hovertemplate: '%{text}<extra></extra>',
            customdata: filteredStars.map(star => star.id)
        };
        
        const layout = {
            title: {
                text: `3D Starmap - ${filteredStars.length} Stars (Mag ≤ ${magLimit})`,
                font: { color: 'white', size: 16 }
            },
            scene: {
                xaxis: { 
                    title: 'X (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                yaxis: { 
                    title: 'Y (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                zaxis: { 
                    title: 'Z (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                bgcolor: '#000000',
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            },
            paper_bgcolor: '#000000',
            plot_bgcolor: '#000000',
            font: { color: 'white' },
            margin: { l: 0, r: 0, t: 40, b: 0 }
        };
        
        const config = {
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
            responsive: true
        };
        
        // Create the plot
        starmapPlot = await Plotly.newPlot('starmap', [trace], layout, config);
        
        // Add click event listener
        document.getElementById('starmap').on('plotly_click', function(data) {
            console.log('Starmap clicked:', data); // Debug
            if (data.points && data.points.length > 0) {
                const starId = data.points[0].customdata;
                console.log('Star ID:', starId, 'Distance mode:', distanceMeasurementMode); // Debug
                
                if (distanceMeasurementMode) {
                    handleDistanceModeClick(starId);
                } else {
                    selectStar(starId);
                }
            }
        });
        
        updateStatus(`Loaded ${filteredStars.length} stars successfully`);
        
    } catch (error) {
        console.error('Error updating starmap:', error);
        updateStatus(`Error: ${error.message}`, false);
    }
}

async function selectStar(starId) {
    try {
        updateStatus(`Loading details for star ${starId}...`, true);
        
        const response = await fetch(`/api/star/${starId}`);
        if (!response.ok) throw new Error('Failed to fetch star details');
        
        const starData = await response.json();
        
        // Show star details
        showStarDetails(starData);
        
        // Highlight star on map
        highlightStarOnMap(starId, starData);
        
        // Show star in search results
        showStarInSearch(starData);
        
    } catch (error) {
        console.error('Error selecting star:', error);
        updateStatus(`Error loading star details: ${error.message}`);
    }
}

function showStarInSearch(starData) {
    const searchResults = document.getElementById('searchResults');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchInput = document.getElementById('starSearch');
    
    // Update search input with star name
    searchInput.value = starData.name;
    
    // Create search result display for selected star
    let resultsHtml = `<p><strong>Selected Star</strong></p>`;
    resultsHtml += `
        <div class="search-result-item mb-2 p-2 selected-star" style="border: 2px solid #74b9ff; border-radius: 4px; background-color: rgba(116, 185, 255, 0.1);">
            <div class="fw-bold text-info">${starData.name}</div>
            <small class="text-muted">
                ${starData.designation_type} • ${starData.constellation_full || starData.constellation}<br>
                Mag: ${starData.properties.magnitude.toFixed(2)} • Dist: ${starData.properties.distance.toFixed(2)} pc
            </small>
            <div class="mt-1">
                <button class="btn btn-sm btn-outline-light" onclick="clearHighlight()">Clear Selection</button>
            </div>
        </div>
    `;
    
    searchResultsList.innerHTML = resultsHtml;
    searchResults.style.display = 'block';
}

function highlightStarOnMap(starId, starData) {
    if (!starmapPlot) return;
    
    // Remove previous highlight without clearing panels
    if (highlightedStarId) {
        const plotDiv = document.getElementById('starmap');
        if (plotDiv && plotDiv.data) {
            const traces = plotDiv.data;
            const highlightIndex = traces.findIndex(trace => trace.name === 'Selected Star');
            
            if (highlightIndex !== -1) {
                Plotly.deleteTraces('starmap', highlightIndex);
            }
        }
    }
    
    // Store highlighted star ID
    highlightedStarId = starId;
    
    // Create highlight trace
    highlightTrace = {
        x: [starData.coordinates.x],
        y: [starData.coordinates.y],
        z: [starData.coordinates.z],
        mode: 'markers',
        type: 'scatter3d',
        marker: {
            size: 15,
            color: '#ff6b6b',
            symbol: 'circle-open',
            line: {
                color: '#ff6b6b',
                width: 4
            }
        },
        text: [`SELECTED: ${starData.name}`],
        hovertemplate: '%{text}<extra></extra>',
        name: 'Selected Star',
        showlegend: false
    };
    
    // Add highlight trace to the plot
    Plotly.addTraces('starmap', highlightTrace);
}

function clearHighlight() {
    if (!starmapPlot) return;
    
    // Remove highlight trace if it exists
    const plotDiv = document.getElementById('starmap');
    if (plotDiv && plotDiv.data) {
        const traces = plotDiv.data;
        const highlightIndex = traces.findIndex(trace => trace.name === 'Selected Star');
        
        if (highlightIndex !== -1) {
            Plotly.deleteTraces('starmap', highlightIndex);
        }
    }
    
    // Clear state
    highlightedStarId = null;
    highlightTrace = null;
    
    // Clear search results
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('starSearch').value = '';
    
    // Hide star info panels
    document.getElementById('starInfo').style.display = 'none';
    document.getElementById('planetInfo').style.display = 'none';
    
    updateStatus('Selection cleared');
}

function showStarDetails(starData) {
    try {
        updateStatus(`Showing details for ${starData.name}`);
        
        // Show star information panel
        const starInfoPanel = document.getElementById('starInfo');
        const starDetails = document.getElementById('starDetails');
        
        // Display all names and identifiers
        let allNamesHtml = '';
        if (starData.all_names && starData.all_names.length > 1) {
            allNamesHtml = `
                <div class="star-property">
                    <span><strong>Other Names:</strong></span>
                    <span>${starData.all_names.slice(1).join(', ')}</span>
                </div>
            `;
        }
        
        let catalogIdsHtml = '';
        if (starData.catalog_ids && starData.catalog_ids.length > 0) {
            catalogIdsHtml = `
                <div class="star-property">
                    <span><strong>Catalog IDs:</strong></span>
                    <span>${starData.catalog_ids.join(', ')}</span>
                </div>
            `;
        }

        // Build fictional data section if available
        let fictionalDataHtml = '';
        if (starData.fictional_data && starData.fictional_data.name) {
            fictionalDataHtml = `
                <div class="fictional-data-section mb-3 p-2" style="background-color: rgba(255, 193, 7, 0.1); border: 1px solid #ffc107; border-radius: 4px;">
                    <div class="star-property">
                        <span><strong>🌟 Felgenland Union Name:</strong></span>
                        <span class="text-warning fw-bold">${starData.fictional_data.name}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Source:</strong></span>
                        <span class="text-muted small">${starData.fictional_data.source}</span>
                    </div>
                    ${starData.fictional_data.description ? `
                        <div class="star-property">
                            <span><strong>Description:</strong></span>
                            <span class="text-muted small">${starData.fictional_data.description}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        starDetails.innerHTML = `
            <h6 class="text-primary">${starData.name}</h6>
            ${fictionalDataHtml}
            <div class="star-property">
                <span><strong>Type:</strong></span>
                <span class="badge bg-info">${starData.designation_type}</span>
            </div>
            ${allNamesHtml}
            ${catalogIdsHtml}
            <div class="star-property">
                <span><strong>Constellation:</strong></span>
                <span>${starData.constellation_full || starData.constellation}</span>
            </div>
            <div class="star-property">
                <span><strong>Magnitude:</strong></span>
                <span>${starData.properties.magnitude.toFixed(2)}</span>
            </div>
            <div class="star-property">
                <span><strong>Distance:</strong></span>
                <span>${starData.properties.distance.toFixed(2)} pc</span>
            </div>
            <div class="star-property">
                <span><strong>Spectral Class:</strong></span>
                <span>${starData.properties.spectral_class}</span>
            </div>
            <div class="star-property">
                <span><strong>Coordinates:</strong></span>
                <span>(${starData.coordinates.x.toFixed(2)}, ${starData.coordinates.y.toFixed(2)}, ${starData.coordinates.z.toFixed(2)})</span>
            </div>
        `;
        
        starInfoPanel.style.display = 'block';
        
        // Show planetary system if available
        if (starData.planets && starData.planets.length > 0) {
            const planetInfoPanel = document.getElementById('planetInfo');
            const planetDetails = document.getElementById('planetDetails');
            const planetSystemTitle = document.getElementById('planetSystemTitle');
            const systemViewToggle = document.getElementById('systemViewToggle');
            
            // Update title
            planetSystemTitle.textContent = `${starData.name} System (${starData.planets.length} planets)`;
            
            // Show system view button
            systemViewToggle.style.display = 'block';
            systemViewToggle.onclick = () => PlanetarySystem.openSystemView(starData);
            
            let planetsHtml = '';
            starData.planets.forEach(planet => {
                const confirmStatus = planet.confirmed ? 
                    '<span class="badge bg-success">Confirmed</span>' : 
                    '<span class="badge bg-warning">Candidate</span>';
                
                // Build moons section if planet has moons
                let moonsHtml = '';
                if (planet.moons && planet.moons.length > 0) {
                    moonsHtml = `
                        <div class="moons-section mt-2">
                            <div class="text-info small fw-bold">🌙 Moons (${planet.moons.length}):</div>
                            <div class="ms-2">
                    `;
                    
                    planet.moons.forEach(moon => {
                        moonsHtml += `
                            <div class="moon-item mt-1 p-1" style="border-left: 2px solid #17a2b8; padding-left: 8px;">
                                <div class="text-info small fw-bold">${moon.name}</div>
                                <div class="text-muted" style="font-size: 0.75rem;">
                                    <div><strong>Type:</strong> ${moon.type}</div>
                                    <div><strong>Mass:</strong> ${moon.mass_earth}× Earth</div>
                                    <div><strong>Radius:</strong> ${moon.radius_earth}× Earth</div>
                                    <div><strong>Distance:</strong> ${moon.orbital_distance_km.toLocaleString()} km</div>
                                    <div><strong>Period:</strong> ${moon.orbital_period_days} days</div>
                                    ${moon.description ? `<div class="text-muted fst-italic">${moon.description}</div>` : ''}
                                </div>
                            </div>
                        `;
                    });
                    
                    moonsHtml += `
                            </div>
                        </div>
                    `;
                }

                planetsHtml += `
                    <div class="planet-item mb-2">
                        <div class="planet-name d-flex justify-content-between align-items-center">
                            <span class="text-success fw-bold">${planet.name}</span>
                            ${confirmStatus}
                        </div>
                        <div class="planet-details mt-1">
                            <small>
                                <div><strong>Type:</strong> ${planet.type}</div>
                                <div><strong>Distance:</strong> ${planet.distance_au} AU</div>
                                <div><strong>Mass:</strong> ${planet.mass_earth}× Earth</div>
                                <div><strong>Radius:</strong> ${planet.radius_earth}× Earth</div>
                                <div><strong>Orbital Period:</strong> ${planet.orbital_period_days} days</div>
                                <div><strong>Discovery:</strong> ${planet.discovery_year}</div>
                            </small>
                            ${moonsHtml}
                        </div>
                    </div>
                `;
            });
            
            planetDetails.innerHTML = planetsHtml;
            planetInfoPanel.style.display = 'block';
            
            // Store current system data globally for the planetary system viewer
            window.currentSystemData = starData;
        } else {
            document.getElementById('planetInfo').style.display = 'none';
            document.getElementById('systemViewToggle').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error showing star details:', error);
        updateStatus(`Error showing star details: ${error.message}`);
    }
}

function resetView() {
    if (starmapPlot) {
        const update = {
            'scene.camera': {
                eye: { x: 1.5, y: 1.5, z: 1.5 }
            }
        };
        Plotly.relayout('starmap', update);
        updateStatus('View reset to default position');
    }
}

async function searchStars() {
    const searchInput = document.getElementById('starSearch');
    const query = searchInput.value.trim();
    
    if (!query) {
        document.getElementById('searchResults').style.display = 'none';
        return;
    }
    
    try {
        updateStatus(`Searching for "${query}"...`, true);
        
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Search failed');
        
        const searchData = await response.json();
        
        // Display search results
        const searchResults = document.getElementById('searchResults');
        const searchResultsList = document.getElementById('searchResultsList');
        
        if (searchData.results && searchData.results.length > 0) {
            let resultsHtml = `<p><strong>${searchData.count} results for "${searchData.query}"</strong></p>`;
            
            searchData.results.forEach(star => {
                resultsHtml += `
                    <div class="search-result-item mb-2 p-2" style="border: 1px solid #444; border-radius: 4px; cursor: pointer;" 
                         onclick="selectStar(${star.id})">
                        <div class="fw-bold text-info">${star.name}</div>
                        <small class="text-muted">
                            ${star.designation_type} • ${star.constellation}<br>
                            Mag: ${star.magnitude.toFixed(2)} • Dist: ${star.distance.toFixed(2)} pc
                        </small>
                    </div>
                `;
            });
            
            searchResultsList.innerHTML = resultsHtml;
            searchResults.style.display = 'block';
            
            updateStatus(`Found ${searchData.count} stars matching "${query}"`);
        } else {
            searchResultsList.innerHTML = `<p class="text-muted">No stars found matching "${query}"</p>`;
            searchResults.style.display = 'block';
            updateStatus(`No results found for "${query}"`);
        }
        
    } catch (error) {
        console.error('Error searching stars:', error);
        updateStatus(`Search error: ${error.message}`);
    }
}

async function exportCSV() {
    try {
        updateStatus('Generating CSV export...', true);
        
        const response = await fetch('/export/csv');
        if (!response.ok) throw new Error('Failed to generate CSV');
        
        // Download the CSV
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'starmap_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        updateStatus('CSV exported successfully');
        
    } catch (error) {
        console.error('Error exporting CSV:', error);
        updateStatus(`Error exporting CSV: ${error.message}`);
    }
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Global function for template access
function toggleSystemView() {
    if (window.currentSystemData && window.currentSystemData.planets && window.currentSystemData.planets.length > 0) {
        PlanetarySystem.openSystemView(window.currentSystemData);
    } else {
        updateStatus('No planetary system data available');
    }
}

function toggleSystemAnimation() {
    if (window.PlanetarySystem) {
        PlanetarySystem.toggleSystemAnimation();
    }
}

// Spectral type filtering function
async function filterBySpectralType() {
    const spectralSelect = document.getElementById('spectralType');
    const selectedType = spectralSelect.value;
    const searchInput = document.getElementById('starSearch');
    
    if (!selectedType) {
        // If no type selected, reload all stars
        updateStarmap();
        updateStatus('Filter cleared - showing all stars');
        return;
    }
    
    try {
        updateStatus(`Filtering starmap by spectral type ${selectedType}...`, true);
        
        const response = await fetch(`/api/search?spectral=${encodeURIComponent(selectedType)}`);
        if (!response.ok) throw new Error('Spectral type filtering failed');
        
        const searchData = await response.json();
        
        if (searchData.results && searchData.results.length > 0) {
            // Update the starmap to show only filtered stars
            await updateStarmapWithFilteredStars(searchData.results, selectedType);
            
            // Also display search results panel
            const searchResults = document.getElementById('searchResults');
            const searchResultsList = document.getElementById('searchResultsList');
            
            let resultsHtml = `<p><strong>${searchData.count} ${selectedType}-type stars on map</strong></p>`;
            if (searchData.total_matching > searchData.count) {
                resultsHtml += `<p class="text-muted">Showing first ${searchData.count} of ${searchData.total_matching} total matches</p>`;
            }
            
            // Show first few results in the panel
            searchData.results.slice(0, 10).forEach(star => {
                resultsHtml += `
                    <div class="search-result-item mb-2 p-2" style="border: 1px solid #444; border-radius: 4px; cursor: pointer;" 
                         onclick="selectStar(${star.id})">
                        <div class="fw-bold text-info">${star.name}</div>
                        <small class="text-muted">
                            ${star.designation_type} • ${star.constellation}<br>
                            Spectral: ${star.spectral_class} • Mag: ${star.magnitude.toFixed(2)} • Dist: ${star.distance.toFixed(2)} pc
                        </small>
                    </div>
                `;
            });
            
            if (searchData.results.length > 10) {
                resultsHtml += `<p class="text-muted">...and ${searchData.results.length - 10} more on the map</p>`;
            }
            
            resultsHtml += `<div class="mt-2"><button class="btn btn-sm btn-outline-light" onclick="clearSpectralFilter()">Show All Stars</button></div>`;
            
            searchResultsList.innerHTML = resultsHtml;
            searchResults.style.display = 'block';
            searchInput.value = `Spectral filter: ${selectedType}`;
            
            updateStatus(`Starmap filtered to ${searchData.results.length} ${selectedType}-type stars`);
        } else {
            updateStatus(`No ${selectedType}-type stars found`);
        }
        
    } catch (error) {
        console.error('Error filtering by spectral type:', error);
        updateStatus(`Spectral filter error: ${error.message}`);
    }
}

async function updateStarmapWithFilteredStars(filteredStars, spectralType) {
    try {
        // Create 3D scatter plot with filtered stars
        const trace = {
            x: filteredStars.map(star => star.coordinates.x),
            y: filteredStars.map(star => star.coordinates.y),
            z: filteredStars.map(star => star.coordinates.z),
            mode: 'markers',
            type: 'scatter3d',
            marker: {
                size: filteredStars.map(star => Math.max(2, 8 - star.magnitude)), // Brighter stars are bigger
                color: filteredStars.map(star => star.magnitude),
                colorscale: [
                    [0, '#ffffff'],      // Bright stars - white
                    [0.3, '#ffff99'],    // Yellow
                    [0.6, '#ff9933'],    // Orange
                    [1, '#ff3333']       // Dim stars - red
                ],
                colorbar: {
                    title: 'Magnitude',
                    titleside: 'right'
                },
                opacity: 0.8
            },
            text: filteredStars.map(star => 
                `${star.name}<br>` +
                `${star.designation_type === 'proper' ? 'Common Name' : 'Designation'}: ${star.designation_type}<br>` +
                `Constellation: ${star.constellation}<br>` +
                `Magnitude: ${star.magnitude.toFixed(2)}<br>` +
                `Distance: ${star.distance.toFixed(2)} pc<br>` +
                `Spectral Class: ${star.spectral_class}<br>` +
                `Coordinates: (${star.coordinates.x.toFixed(2)}, ${star.coordinates.y.toFixed(2)}, ${star.coordinates.z.toFixed(2)})`
            ),
            hovertemplate: '%{text}<extra></extra>',
            customdata: filteredStars.map(star => star.id)
        };
        
        const layout = {
            title: {
                text: `3D Starmap - ${filteredStars.length} ${spectralType}-type Stars`,
                font: { color: 'white', size: 16 }
            },
            scene: {
                xaxis: { 
                    title: 'X (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                yaxis: { 
                    title: 'Y (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                zaxis: { 
                    title: 'Z (parsecs)', 
                    gridcolor: '#444',
                    zerolinecolor: '#666',
                    backgroundcolor: '#000'
                },
                bgcolor: '#000000',
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            },
            paper_bgcolor: '#000000',
            plot_bgcolor: '#000000',
            font: { color: 'white' },
            margin: { l: 0, r: 0, t: 40, b: 0 }
        };
        
        const config = {
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
            responsive: true
        };
        
        // Update the plot with filtered data
        await Plotly.newPlot('starmap', [trace], layout, config);
        
        // Re-add click event listener
        document.getElementById('starmap').on('plotly_click', function(data) {
            console.log('Starmap clicked:', data); // Debug
            if (data.points && data.points.length > 0) {
                const starId = data.points[0].customdata;
                console.log('Star ID:', starId, 'Distance mode:', distanceMeasurementMode); // Debug
                
                if (distanceMeasurementMode) {
                    handleDistanceModeClick(starId);
                } else {
                    selectStar(starId);
                }
            }
        });
        
        // Update currentStars with filtered data for distance measurements
        currentStars = filteredStars.map(star => ({
            id: star.id,
            name: star.name,
            x: star.coordinates.x,
            y: star.coordinates.y,
            z: star.coordinates.z,
            mag: star.magnitude,
            spect: star.spectral_class,
            dist: star.distance
        }));
        
    } catch (error) {
        console.error('Error updating starmap with filtered stars:', error);
        updateStatus(`Error updating starmap: ${error.message}`);
    }
}

function clearSpectralFilter() {
    // Reset the spectral type dropdown
    document.getElementById('spectralType').value = '';
    
    // Hide search results
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('starSearch').value = '';
    
    // Reload the full starmap
    updateStarmap();
    
    updateStatus('Spectral filter cleared - showing all stars');
}

// Distance measurement functions
function toggleDistanceMeasurement() {
    const toggleButton = document.getElementById('distanceToggle');
    const indicator = document.getElementById('distanceModeIndicator');
    
    if (!distanceMeasurementMode) {
        // Start distance measurement mode
        distanceMeasurementMode = true;
        selectedStarsForDistance = [];
        toggleButton.textContent = '❌ Cancel Distance Mode';
        toggleButton.classList.remove('btn-outline-primary');
        toggleButton.classList.add('btn-outline-warning');
        if (indicator) indicator.style.display = 'block';
        updateStatus('🎯 Distance measurement mode ON - Click two stars to measure distance');
        console.log('Distance measurement mode activated'); // Debug
    } else {
        // Cancel distance measurement mode
        distanceMeasurementMode = false;
        selectedStarsForDistance = [];
        toggleButton.textContent = '📏 Start Distance Mode';
        toggleButton.classList.remove('btn-outline-warning');
        toggleButton.classList.add('btn-outline-primary');
        if (indicator) indicator.style.display = 'none';
        
        // Remove distance visualization
        clearDistanceVisualization();
        clearHighlight(); // Clear any selected stars
        updateStatus('Distance measurement mode OFF');
        console.log('Distance measurement mode deactivated'); // Debug
    }
}

async function measureDistance(starId1, starId2) {
    try {
        updateStatus(`Calculating distance between stars...`, true);
        
        const response = await fetch(`/api/distance?star1=${starId1}&star2=${starId2}`);
        if (!response.ok) throw new Error('Distance calculation failed');
        
        const distanceData = await response.json();
        
        // Display distance results
        const searchResults = document.getElementById('searchResults');
        const searchResultsList = document.getElementById('searchResultsList');
        
        let resultsHtml = `
            <div class="distance-results">
                <h6 class="text-primary mb-3">🚀 Distance Measurement</h6>
                
                <div class="mb-3">
                    <strong>Between:</strong><br>
                    <div class="ms-2">
                        <div class="text-info">${distanceData.star1.name}</div>
                        <small class="text-muted">Distance from Sol: ${distanceData.star1.distance_from_sol_ly.toFixed(2)} ly</small>
                    </div>
                    <div class="ms-2 mt-1">
                        <div class="text-info">${distanceData.star2.name}</div>
                        <small class="text-muted">Distance from Sol: ${distanceData.star2.distance_from_sol_ly.toFixed(2)} ly</small>
                    </div>
                </div>
                
                <div class="distance-results-box p-3" style="background-color: rgba(116, 185, 255, 0.1); border: 1px solid #74b9ff; border-radius: 4px;">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="fw-bold text-success">${distanceData.distance_between.light_years}</div>
                            <small class="text-muted">Light Years</small>
                        </div>
                        <div class="col-6">
                            <div class="fw-bold text-warning">${distanceData.distance_between.parsecs}</div>
                            <small class="text-muted">Parsecs</small>
                        </div>
                    </div>
                    <hr class="my-2">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="small">${distanceData.distance_between.astronomical_units.toLocaleString()}</div>
                            <small class="text-muted">AU</small>
                        </div>
                        <div class="col-6">
                            <div class="small">${distanceData.distance_between.kilometers.toExponential(2)}</div>
                            <small class="text-muted">km</small>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-light" onclick="clearDistanceMeasurement()">Clear Measurement</button>
                    <button class="btn btn-sm btn-outline-primary" onclick="toggleDistanceMeasurement()">New Measurement</button>
                </div>
            </div>
        `;
        
        searchResultsList.innerHTML = resultsHtml;
        searchResults.style.display = 'block';
        
        // Add visualization line between stars
        addDistanceVisualization(distanceData);
        
        updateStatus(`Distance: ${distanceData.distance_between.light_years} ly / ${distanceData.distance_between.parsecs} pc`);
        
    } catch (error) {
        console.error('Error measuring distance:', error);
        updateStatus(`Distance measurement error: ${error.message}`);
    }
}

function addDistanceVisualization(distanceData) {
    if (!starmapPlot) return;
    
    // Remove previous distance line
    clearDistanceVisualization();
    
    // We need to get the actual 3D coordinates from the star data
    // Find the stars in currentStars array to get their coordinates
    const star1 = currentStars.find(s => s.id === distanceData.star1.id);
    const star2 = currentStars.find(s => s.id === distanceData.star2.id);
    
    if (!star1 || !star2) {
        console.log('Could not find star coordinates for visualization');
        return;
    }
    
    // Add line connecting the two stars using their actual 3D coordinates
    distanceTrace = {
        x: [star1.x, star2.x],
        y: [star1.y, star2.y],
        z: [star1.z, star2.z],
        mode: 'lines',
        type: 'scatter3d',
        line: {
            color: '#00ff00',
            width: 6
        },
        name: 'Distance Measurement',
        showlegend: false,
        hoverinfo: 'skip'
    };
    
    Plotly.addTraces('starmap', distanceTrace);
}

function clearDistanceVisualization() {
    if (!starmapPlot || !distanceTrace) return;
    
    const plotDiv = document.getElementById('starmap');
    if (plotDiv && plotDiv.data) {
        const traces = plotDiv.data;
        const distanceIndex = traces.findIndex(trace => trace.name === 'Distance Measurement');
        
        if (distanceIndex !== -1) {
            Plotly.deleteTraces('starmap', distanceIndex);
        }
    }
    
    distanceTrace = null;
}

function clearDistanceMeasurement() {
    selectedStarsForDistance = [];
    clearDistanceVisualization();
    document.getElementById('searchResults').style.display = 'none';
    updateStatus('Distance measurement cleared');
}

function handleDistanceModeClick(starId) {
    console.log('Distance mode click:', starId); // Debug
    
    if (selectedStarsForDistance.includes(starId)) {
        updateStatus('Star already selected for distance measurement');
        return;
    }
    
    selectedStarsForDistance.push(starId);
    console.log('Selected stars for distance:', selectedStarsForDistance); // Debug
    
    // Find star name for better feedback
    const star = currentStars.find(s => s.id === starId);
    const starName = star ? star.name : `Star ${starId}`;
    
    if (selectedStarsForDistance.length === 1) {
        updateStatus(`First star selected: ${starName}. Click another star to measure distance.`);
        
        // Highlight the first selected star
        if (star) {
            highlightStarOnMap(starId, {
                coordinates: { x: star.x, y: star.y, z: star.z },
                name: starName
            });
        }
    } else if (selectedStarsForDistance.length === 2) {
        const star2 = currentStars.find(s => s.id === selectedStarsForDistance[1]);
        const star2Name = star2 ? star2.name : `Star ${selectedStarsForDistance[1]}`;
        
        updateStatus(`Measuring distance between ${starName} and ${star2Name}...`, true);
        
        // Measure distance between the two selected stars
        measureDistance(selectedStarsForDistance[0], selectedStarsForDistance[1]);
        
        // Reset distance mode but don't exit automatically
        selectedStarsForDistance = [];
    }
}