// Starmap JavaScript Functionality

let currentStars = [];
let starmapPlot = null;
let highlightedStarId = null;
let highlightTrace = null;
let distanceMeasurementMode = false;
let selectedStarsForDistance = [];
let distanceTrace = null;

// Political overlay variables
let politicalOverlayActive = false;
let tradeRoutesActive = false;
let territoryBordersActive = false;
let nationsData = {};
let selectedNation = null;
let politicalTraces = [];

// Galactic directions variables
let galacticDirectionsActive = false;
let galacticGridActive = false;
let galacticDirectionsData = {};
let galacticDistance = 50;
let galacticTraces = [];

// Stellar regions variables
let stellarRegionsActive = false;
let stellarRegionsData = {};
let stellarRegionsTraces = [];
let selectedRegion = null;

// Helper function to convert hex color to RGB values
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? 
        `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : 
        '128, 128, 128'; // fallback gray
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    initializeStarmap(); // Initialize with server readiness check
});

async function initializeStarmap() {
    updateStatus('Checking server connection...', true);
    
    // Check if server is ready
    let serverReady = false;
    let attempts = 0;
    const maxAttempts = 10;
    
    while (!serverReady && attempts < maxAttempts) {
        try {
            const response = await fetch('/api/stars?limit=1');
            if (response.ok) {
                serverReady = true;
            } else {
                throw new Error('Server not ready');
            }
        } catch (error) {
            attempts++;
            console.log(`Server check attempt ${attempts}/${maxAttempts} failed:`, error.message);
            if (attempts < maxAttempts) {
                updateStatus(`Waiting for server... (${attempts}/${maxAttempts})`, true);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    
    if (serverReady) {
        updateStarmap(); // Load initial starmap
    } else {
        updateStatus('Failed to connect to server. Please refresh the page.', false);
    }
}

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

async function updateStarmap(retryCount = 0) {
    const magLimit = document.getElementById('magLimit').value;
    const starCount = document.getElementById('starCount').value;
    
    updateStatus('Loading starmap...', true);
    
    try {
        // Fetch star data with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch('/api/stars', {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        currentStars = await response.json();
        
        if (!Array.isArray(currentStars)) {
            throw new Error('Invalid data format received from server');
        }
        
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
                size: filteredStars.map(star => {
                    const baseSize = Math.max(2, 8 - star.mag);
                    // Reduce Sol's (star ID 0) circle radius by half
                    return star.id === 0 ? baseSize / 2 : baseSize;
                }), // Brighter stars are bigger
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
            responsive: true,
            doubleClick: 'reset'
        };
        
        // Create the plot
        starmapPlot = await Plotly.newPlot('starmap', [trace], layout, config);
        
        // Add legend click event listener to prevent default double-click behavior
        document.getElementById('starmap').on('plotly_legendclick', function(data) {
            // Allow single clicks on legend items but prevent double-click toggle all
            return false; // This prevents the default behavior
        });
        
        document.getElementById('starmap').on('plotly_legenddoubleclick', function(data) {
            // Prevent double-click legend behavior entirely
            return false;
        });
        
        // Add click event listener
        document.getElementById('starmap').on('plotly_click', function(data) {
            try {
                if (data.points && data.points.length > 0) {
                    const point = data.points[0];
                    
                    // Check if this is a stellar region click
                    if (point.data && point.data.name && point.data.name.startsWith('Region: ')) {
                        const regionName = point.data.name.replace('Region: ', '');
                        console.debug('Stellar region clicked:', regionName);
                        
                        // Select the region in the dropdown
                        const regionSelect = document.getElementById('regionSelect');
                        if (regionSelect) {
                            regionSelect.value = regionName;
                            handleRegionSelection();
                        }
                        return;
                    }
                    
                    // Only process clicks on the main star trace (trace index 0) with valid customdata
                    if (point.curveNumber === 0 && point.customdata && 
                        typeof point.customdata === 'number' && point.customdata > 0) {
                        
                        const starId = point.customdata;
                        
                        if (distanceMeasurementMode) {
                            handleDistanceModeClick(starId);
                        } else {
                            selectStar(starId);
                        }
                    } else {
                        console.debug('Click ignored - not on main star trace or invalid customdata:', {
                            curveNumber: point.curveNumber,
                            customdata: point.customdata,
                            hasValidCustomdata: point.customdata && typeof point.customdata === 'number' && point.customdata > 0
                        });
                    }
                } else {
                    // Handle empty space clicks - prevent default camera movement
                    console.debug('Click on empty space - preventing default behavior');
                    return false;
                }
            } catch (error) {
                console.error('Error handling star click:', error);
                updateStatus('Error processing star selection');
            }
        });
        
        updateStatus(`Loaded ${filteredStars.length} stars successfully`);
        
        // Reapply political overlay if it was active
        reapplyPoliticalOverlay();
        
        // Reapply stellar regions overlay if it was active
        reapplyStellarRegionsOverlay();
        
    } catch (error) {
        console.error('Error updating starmap:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        
        // Retry logic for network errors
        if ((error.name === 'AbortError' || error.message.includes('fetch')) && retryCount < 3) {
            console.log(`Retrying starmap load... Attempt ${retryCount + 1}`);
            updateStatus(`Connection failed, retrying... (${retryCount + 1}/3)`, true);
            setTimeout(() => updateStarmap(retryCount + 1), 2000);
            return;
        }
        
        updateStatus(`Error loading starmap: ${error.message}. Check browser console for details.`, false);
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
            size: starData.id === 0 ? 7.5 : 15, // Reduce Sol's highlight size by half
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

function getHabitabilityHtml(starData) {
    // Create habitability section HTML - check both direct properties and nested habitability object
    let habitabilityData = starData.habitability || {};
    
    // Support both formats for backward compatibility
    const score = habitabilityData.score !== undefined ? habitabilityData.score : starData.habitability_score;
    const category = habitabilityData.category || starData.habitability_category || 'Unknown';
    const priority = habitabilityData.exploration_priority || starData.exploration_priority || 'Unknown';
    
    // If no habitability data available, return empty
    if (score === undefined || score === null) {
        return '';
    }
    
    // Determine color based on habitability category
    let categoryColor = 'secondary';
    let priorityColor = 'secondary';
    
    switch (category) {
        case 'Excellent':
            categoryColor = 'success';
            break;
        case 'Good':
            categoryColor = 'primary';
            break;
        case 'Moderate':
            categoryColor = 'warning';
            break;
        case 'Poor':
            categoryColor = 'danger';
            break;
        case 'Unsuitable':
            categoryColor = 'dark';
            break;
    }
    
    switch (priority) {
        case 'High':
            priorityColor = 'success';
            break;
        case 'Medium-High':
            priorityColor = 'primary';
            break;
        case 'Medium':
            priorityColor = 'warning';
            break;
        case 'Low':
            priorityColor = 'danger';
            break;
        case 'None':
            priorityColor = 'dark';
            break;
    }
    
    return `
        <div class="habitability-section mb-3 p-2" style="background-color: rgba(40, 167, 69, 0.1); border: 1px solid #28a745; border-radius: 4px;">
            <div class="star-property">
                <span><strong>🌍 Habitability Score:</strong></span>
                <span class="fw-bold">${(score * 100).toFixed(1)}%</span>
            </div>
            <div class="star-property">
                <span><strong>Category:</strong></span>
                <span class="badge bg-${categoryColor}">${category}</span>
            </div>
            <div class="star-property">
                <span><strong>Exploration Priority:</strong></span>
                <span class="badge bg-${priorityColor}">${priority}</span>
            </div>
            <div class="star-property">
                <span><strong>Assessment:</strong></span>
                <span class="text-muted small" id="habitability-explanation-${starData.id}">Loading...</span>
            </div>
        </div>
    `;
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

        // Build nation data section if available
        let nationDataHtml = '';
        if (starData.nation && starData.nation.id !== 'neutral_zone') {
            nationDataHtml = `
                <div class="nation-data-section mb-3 p-2" style="background-color: rgba(${hexToRgb(starData.nation.color)}, 0.1); border: 1px solid ${starData.nation.color}; border-radius: 4px;">
                    <div class="star-property">
                        <span><strong>🏛️ Political Control:</strong></span>
                        <span class="fw-bold" style="color: ${starData.nation.color};">${starData.nation.name}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Government:</strong></span>
                        <span class="text-muted small">${starData.nation.government_type}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Population:</strong></span>
                        <span class="text-muted small">${starData.nation.population}</span>
                    </div>
                    ${starData.nation.capital_system ? `
                        <div class="star-property">
                            <span><strong>Capital System:</strong></span>
                            <span class="text-muted small">${starData.nation.capital_system}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Build fictional data section if available
        let fictionalDataHtml = '';
        if (starData.fictional_data && starData.fictional_data.name) {
            fictionalDataHtml = `
                <div class="fictional-data-section mb-3 p-2" style="background-color: rgba(255, 193, 7, 0.1); border: 1px solid #ffc107; border-radius: 4px;">
                    <div class="star-property">
                        <span><strong>🌟 Local Name:</strong></span>
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
            ${nationDataHtml}
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
            ${getHabitabilityHtml(starData)}
            <div class="star-property">
                <span><strong>Coordinates:</strong></span>
                <span>(${starData.coordinates.x.toFixed(2)}, ${starData.coordinates.y.toFixed(2)}, ${starData.coordinates.z.toFixed(2)})</span>
            </div>
        `;
        
        starInfoPanel.style.display = 'block';
        
        // Fetch and display habitability explanation if habitability data is available
        if (starData.habitability_score !== undefined) {
            fetchHabitabilityExplanation(starData.id);
        }
        
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
                size: filteredStars.map(star => {
                    const baseSize = Math.max(2, 8 - star.magnitude);
                    // Reduce Sol's (star ID 0) circle radius by half
                    return star.id === 0 ? baseSize / 2 : baseSize;
                }), // Brighter stars are bigger
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
            responsive: true,
            doubleClick: 'reset'
        };
        
        // Update the plot with filtered data
        await Plotly.newPlot('starmap', [trace], layout, config);
        
        // Re-add click event listener
        document.getElementById('starmap').on('plotly_click', function(data) {
            try {
                if (data.points && data.points.length > 0) {
                    const point = data.points[0];
                    
                    // Check if this is a stellar region click
                    if (point.data && point.data.name && point.data.name.startsWith('Region: ')) {
                        const regionName = point.data.name.replace('Region: ', '');
                        console.debug('Stellar region clicked:', regionName);
                        
                        // Select the region in the dropdown
                        const regionSelect = document.getElementById('regionSelect');
                        if (regionSelect) {
                            regionSelect.value = regionName;
                            handleRegionSelection();
                        }
                        return;
                    }
                    
                    // Only process clicks on the main star trace (trace index 0) with valid customdata
                    if (point.curveNumber === 0 && point.customdata && 
                        typeof point.customdata === 'number' && point.customdata > 0) {
                        
                        const starId = point.customdata;
                        
                        if (distanceMeasurementMode) {
                            handleDistanceModeClick(starId);
                        } else {
                            selectStar(starId);
                        }
                    } else {
                        console.debug('Click ignored - not on main star trace or invalid customdata:', {
                            curveNumber: point.curveNumber,
                            customdata: point.customdata,
                            hasValidCustomdata: point.customdata && typeof point.customdata === 'number' && point.customdata > 0
                        });
                    }
                } else {
                    // Handle empty space clicks - prevent default camera movement
                    console.debug('Click on empty space - preventing default behavior');
                    return false;
                }
            } catch (error) {
                console.error('Error handling star click:', error);
                updateStatus('Error processing star selection');
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
        updateStatus('Could not find star coordinates for visualization');
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
    
    if (selectedStarsForDistance.includes(starId)) {
        updateStatus('Star already selected for distance measurement');
        return;
    }
    
    selectedStarsForDistance.push(starId);
    
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

// Political Overlay Functions
async function loadNationsData() {
    try {
        const response = await fetch('/api/nations');
        if (!response.ok) throw new Error('Failed to fetch nations data');
        
        const data = await response.json();
        nationsData = data.nations;
        updateStatus('Nations data loaded successfully');
    } catch (error) {
        console.error('Error loading nations data:', error);
        updateStatus('Error loading nations data');
    }
}

function togglePoliticalOverlay() {
    const checkbox = document.getElementById('politicalOverlay');
    politicalOverlayActive = checkbox.checked;
    
    if (politicalOverlayActive) {
        // Ensure we have current star data
        if (!currentStars || currentStars.length === 0) {
            updateStatus('Loading star data for political overlay...');
            // Reload starmap which will trigger reapplyPoliticalOverlay
            updateStarmap();
            return;
        }
        
        if (Object.keys(nationsData).length === 0) {
            updateStatus('Loading nations data...');
            loadNationsData().then(() => {
                applyPoliticalOverlay();
            }).catch(error => {
                console.error('Error loading nations data:', error);
                updateStatus('Error loading nations data');
                checkbox.checked = false;
                politicalOverlayActive = false;
            });
        } else {
            applyPoliticalOverlay();
        }
    } else {
        clearPoliticalOverlay();
    }
}

function applyPoliticalOverlay() {
    if (!starmapPlot || !currentStars) return;
    
    // Update star colors based on nation control
    const updatedColors = currentStars.map(star => {
        // Check if this star belongs to any nation
        for (const [nationId, nation] of Object.entries(nationsData)) {
            if (nationId !== 'neutral_zone' && nation.territories && nation.territories.includes(star.id)) {
                return nation.color;
            }
        }
        // For unaligned stars, use original magnitude-based colors
        return getOriginalStarColor(star.mag);
    });
    
    // Update the main star trace colors and disable colorscale when using direct colors
    Plotly.restyle('starmap', {
        'marker.color': [updatedColors],
        'marker.colorscale': null,
        'marker.cmin': null,
        'marker.cmax': null
    }, [0]);
    
    updateStatus('Political overlay applied');
}

function reapplyPoliticalOverlay() {
    // Reapply political overlay if it's currently active
    if (politicalOverlayActive && currentStars && starmapPlot) {
        try {
            applyPoliticalOverlay();
        } catch (error) {
            console.error('Error reapplying political overlay:', error);
            updateStatus('Warning: Political overlay may need to be refreshed');
        }
    }
}

function clearPoliticalOverlay() {
    if (!starmapPlot || !currentStars) return;
    
    // Reset to original magnitude-based colors using numeric values and colorscale
    const originalColors = currentStars.map(star => star.mag);
    
    Plotly.restyle('starmap', {
        'marker.color': [originalColors],
        'marker.colorscale': [
            [0, '#ffffff'],      // Bright stars - white
            [0.3, '#ffff99'],    // Yellow
            [0.6, '#ff9933'],    // Orange
            [1, '#ff3333']       // Dim stars - red
        ],
        'marker.cmin': undefined,
        'marker.cmax': undefined
    }, [0]);
    
    // Clear any political traces
    clearPoliticalTraces();
    
    updateStatus('Political overlay cleared');
}

function getOriginalStarColor(magnitude) {
    // Convert magnitude to actual color values based on the colorscale used in the starmap
    // The colorscale is: [0, '#ffffff'], [0.3, '#ffff99'], [0.6, '#ff9933'], [1, '#ff3333']
    // We need to normalize the magnitude to 0-1 range and interpolate the colors
    
    // Most stars have magnitude between -2 and 8, so we'll normalize to this range
    const minMag = -2;
    const maxMag = 8;
    let normalizedMag = (magnitude - minMag) / (maxMag - minMag);
    
    // Clamp to 0-1 range
    normalizedMag = Math.max(0, Math.min(1, normalizedMag));
    
    // Map to color based on the colorscale
    if (normalizedMag <= 0.3) {
        // Interpolate between white (#ffffff) and yellow (#ffff99)
        const ratio = normalizedMag / 0.3;
        const r = 255;
        const g = 255;
        const b = Math.round(255 - (255 - 153) * ratio);
        return `rgb(${r}, ${g}, ${b})`;
    } else if (normalizedMag <= 0.6) {
        // Interpolate between yellow (#ffff99) and orange (#ff9933)
        const ratio = (normalizedMag - 0.3) / 0.3;
        const r = 255;
        const g = Math.round(255 - (255 - 153) * ratio);
        const b = Math.round(153 - (153 - 51) * ratio);
        return `rgb(${r}, ${g}, ${b})`;
    } else {
        // Interpolate between orange (#ff9933) and red (#ff3333)
        const ratio = (normalizedMag - 0.6) / 0.4;
        const r = 255;
        const g = Math.round(153 - 153 * ratio);
        const b = Math.round(51 - 51 * ratio);
        return `rgb(${r}, ${g}, ${b})`;
    }
}

function toggleTradeRoutes() {
    const checkbox = document.getElementById('tradeRoutes');
    tradeRoutesActive = checkbox.checked;
    
    if (tradeRoutesActive) {
        showTradeRoutes();
    } else {
        hideTradeRoutes();
    }
}

async function showTradeRoutes() {
    if (!starmapPlot) return;
    
    // Clear existing trade route traces
    hideTradeRoutes();
    
    try {
        // Ensure nations data is loaded before showing trade routes
        if (Object.keys(nationsData).length === 0) {
            updateStatus('Loading nations data for trade routes...', true);
            await loadNationsData();
        }
        
        // Load trade routes data
        updateStatus('Loading trade routes data...', true);
        const response = await fetch('/api/trade-routes');
        if (!response.ok) throw new Error('Failed to fetch trade routes');
        
        const tradeData = await response.json();
        const allRoutes = tradeData.trade_routes;
        
        updateStatus('Processing trade routes...', true);
        let processedRoutes = 0;
        let skippedRoutes = 0;
        
        // Process all route groups
        Object.entries(allRoutes).forEach(([routeGroup, routes]) => {
            routes.forEach((route, index) => {
                const fromStar = currentStars.find(s => s.id === route.from_star_id);
                const toStar = currentStars.find(s => s.id === route.to_star_id);
                
                if (!fromStar || !toStar) {
                    console.warn(`Trade route "${route.name}" skipped - missing stars:`, {
                        from_star_id: route.from_star_id,
                        to_star_id: route.to_star_id,
                        fromStar: fromStar ? 'found' : 'not found',
                        toStar: toStar ? 'found' : 'not found'
                    });
                    skippedRoutes++;
                    return;
                }
                
                // Get nation color for the route
                let routeColor = '#FFFFFF'; // Default white
                if (route.controlling_nation && nationsData[route.controlling_nation]) {
                    routeColor = nationsData[route.controlling_nation].color;
                } else if (route.controlling_nation) {
                    console.warn(`Nation "${route.controlling_nation}" not found for route "${route.name}"`);
                }
                
                // Determine line style based on route type
                let lineStyle = 'dash';
                let lineWidth = 3;
                if (route.route_type === 'Primary Trade') {
                    lineStyle = 'solid';
                    lineWidth = 5;
                } else if (route.route_type === 'Administrative') {
                    lineStyle = 'dot';
                    lineWidth = 4;
                } else if (route.route_type === 'Research/Military') {
                    lineStyle = 'dashdot';
                    lineWidth = 3;
                } else if (route.route_type === 'Military Alliance') {
                    lineStyle = 'solid';
                    lineWidth = 4;
                } else if (route.route_type === 'Neutral Trade') {
                    lineStyle = 'longdash';
                    lineWidth = 2;
                }
                
                const tradeRouteTrace = {
                    x: [fromStar.x, toStar.x],
                    y: [fromStar.y, toStar.y],
                    z: [fromStar.z, toStar.z],
                    mode: 'lines',
                    type: 'scatter3d',
                    line: {
                        color: routeColor,
                        width: lineWidth,
                        dash: lineStyle
                    },
                    name: `Trade Route: ${route.name}`,
                    hovertemplate: `<b>${route.name}</b><br>` +
                                 `${fromStar.name} → ${toStar.name}<br>` +
                                 `Type: ${route.route_type}<br>` +
                                 `Est. ${route.established}<br>` +
                                 `Frequency: ${route.frequency}<br>` +
                                 `Travel Time: ${route.travel_time_days} days<br>` +
                                 `Security: ${route.security_level}<br>` +
                                 `Controlling Nation: ${route.controlling_nation}<br>` +
                                 `${route.description}<extra></extra>`,
                    showlegend: false,
                    hoverinfo: 'skip'
                };
                
                Plotly.addTraces('starmap', tradeRouteTrace);
                politicalTraces.push(tradeRouteTrace);
                processedRoutes++;
            });
        });
        
        const totalRoutes = Object.values(allRoutes).flat().length;
        updateStatus(`Trade routes displayed (${processedRoutes}/${totalRoutes} routes${skippedRoutes > 0 ? `, ${skippedRoutes} skipped` : ''})`);
        
        if (skippedRoutes > 0) {
            console.warn(`${skippedRoutes} trade routes were skipped due to missing star data`);
        }
        
    } catch (error) {
        console.error('Error loading trade routes:', error);
        updateStatus('Error loading trade routes');
    }
}

function hideTradeRoutes() {
    clearTradeRouteTraces();
}

function toggleTerritoryBorders() {
    const checkbox = document.getElementById('territoryBorders');
    territoryBordersActive = checkbox.checked;
    
    if (territoryBordersActive) {
        showTerritoryBorders();
    } else {
        hideTerritoryBorders();
    }
}

function showTerritoryBorders() {
    if (!starmapPlot || !currentStars || Object.keys(nationsData).length === 0) return;
    
    // Clear existing border traces
    hideTerritoryBorders();
    
    try {
        // Create territory borders for each nation
        Object.entries(nationsData).forEach(([nationId, nation]) => {
            if (nationId === 'neutral_zone') return;
            
            // Get stars belonging to this nation
            const nationStars = currentStars.filter(star => 
                nation.territories && nation.territories.includes(star.id)
            );
            
            if (nationStars.length >= 1) {
                createTerritoryBoundary(nationStars, nation);
            }
        });
        
        updateStatus('Territory borders displayed');
    } catch (error) {
        console.error('Error showing territory borders:', error);
        updateStatus('Error displaying territory borders');
    }
}

function createTerritoryBoundary(stars, nation) {
    if (stars.length < 1) return;
    
    // Calculate bounding sphere center and radius
    const center = calculateCentroid(stars);
    let radius = calculateBoundingRadius(stars, center);
    
    // For single-star nations, set a minimum radius
    if (stars.length === 1) {
        radius = Math.max(radius, 5.0); // Minimum 5 parsecs radius
    }
    
    // Create a multiplier based on the number of stars in the nation
    // More stars = larger territory radius to encompass the space
    const baseMultiplier = 1.2; // Base multiplier for all nations
    const starCountFactor = Math.log10(stars.length + 1) * 0.5; // Logarithmic scale
    let multiplier = baseMultiplier + starCountFactor;
    
    // Special adjustment for Protelani and Dorsai Republics - scale down by half
    if (nation.name === "Protelani Republic" || nation.name === "Dorsai Republic") {
        multiplier = multiplier * 0.5; // Reduce border size by half
    }
    
    const borderRadius = radius * multiplier;
    
    // Create sphere wireframe
    const sphereTrace = createSphereWireframe(center, borderRadius, nation);
    
    // Add connecting lines between all stars in the nation
    const connectionTrace = createStarConnections(stars, nation);
    
    // Add traces to the plot
    Plotly.addTraces('starmap', [sphereTrace, connectionTrace]);
    politicalTraces.push(sphereTrace, connectionTrace);
}

function calculateCentroid(stars) {
    const sum = stars.reduce((acc, star) => ({
        x: acc.x + star.x,
        y: acc.y + star.y,
        z: acc.z + star.z
    }), { x: 0, y: 0, z: 0 });
    
    return {
        x: sum.x / stars.length,
        y: sum.y / stars.length,
        z: sum.z / stars.length
    };
}

function calculateBoundingRadius(stars, center) {
    return Math.max(...stars.map(star => 
        Math.sqrt(
            Math.pow(star.x - center.x, 2) + 
            Math.pow(star.y - center.y, 2) + 
            Math.pow(star.z - center.z, 2)
        )
    ));
}

function createSphereWireframe(center, radius, nation) {
    const points = [];
    const lines = [];
    
    // Create latitude/longitude grid on sphere
    const latSteps = 8; // Number of latitude lines
    const lonSteps = 12; // Number of longitude lines
    
    // Generate sphere points
    for (let lat = 0; lat <= latSteps; lat++) {
        const theta = (lat * Math.PI) / latSteps; // 0 to π
        for (let lon = 0; lon <= lonSteps; lon++) {
            const phi = (lon * 2 * Math.PI) / lonSteps; // 0 to 2π
            
            const x = center.x + radius * Math.sin(theta) * Math.cos(phi);
            const y = center.y + radius * Math.sin(theta) * Math.sin(phi);
            const z = center.z + radius * Math.cos(theta);
            
            points.push({ x, y, z });
        }
    }
    
    // Create wireframe lines
    const x_coords = [];
    const y_coords = [];
    const z_coords = [];
    
    // Latitude lines
    for (let lat = 0; lat <= latSteps; lat++) {
        for (let lon = 0; lon < lonSteps; lon++) {
            const idx1 = lat * (lonSteps + 1) + lon;
            const idx2 = lat * (lonSteps + 1) + (lon + 1);
            
            if (lat > 0 && lat < latSteps) { // Skip poles for cleaner look
                x_coords.push(points[idx1].x, points[idx2].x, null);
                y_coords.push(points[idx1].y, points[idx2].y, null);
                z_coords.push(points[idx1].z, points[idx2].z, null);
            }
        }
    }
    
    // Longitude lines
    for (let lon = 0; lon <= lonSteps; lon += 2) { // Skip some for cleaner look
        for (let lat = 0; lat < latSteps; lat++) {
            const idx1 = lat * (lonSteps + 1) + lon;
            const idx2 = (lat + 1) * (lonSteps + 1) + lon;
            
            x_coords.push(points[idx1].x, points[idx2].x, null);
            y_coords.push(points[idx1].y, points[idx2].y, null);
            z_coords.push(points[idx1].z, points[idx2].z, null);
        }
    }
    
    return {
        x: x_coords,
        y: y_coords,
        z: z_coords,
        mode: 'lines',
        type: 'scatter3d',
        line: {
            color: nation.border_color || nation.color,
            width: 2,
            dash: 'dot'
        },
        name: `${nation.name} Territory`,
        hovertemplate: `<b>${nation.name}</b><br>Territory Boundary<extra></extra>`,
        showlegend: false,
        opacity: 0.6,
        hoverinfo: 'skip'
    };
}

function createStarConnections(stars, nation) {
    const x_coords = [];
    const y_coords = [];
    const z_coords = [];
    
    // Create lines connecting all stars to the centroid for a "web" effect
    const center = calculateCentroid(stars);
    
    stars.forEach(star => {
        x_coords.push(center.x, star.x, null);
        y_coords.push(center.y, star.y, null);
        z_coords.push(center.z, star.z, null);
    });
    
    return {
        x: x_coords,
        y: y_coords,
        z: z_coords,
        mode: 'lines',
        type: 'scatter3d',
        line: {
            color: nation.color,
            width: 1,
            dash: 'dash'
        },
        name: `${nation.name} Connections`,
        hovertemplate: `<b>${nation.name}</b><br>Internal Connections<extra></extra>`,
        showlegend: false,
        opacity: 0.4,
        hoverinfo: 'skip'
    };
}

function hideTerritoryBorders() {
    // Clear territory border traces
    clearTerritoryBorderTraces();
    updateStatus('Territory borders hidden');
}

function clearPoliticalTraces() {
    if (!starmapPlot) return;
    
    // Remove all political traces from the plot
    const currentData = starmapPlot.data;
    const nonPoliticalTraces = currentData.filter((trace, index) => {
        return index === 0 || trace.name === 'Highlighted Star' || trace.name === 'Distance Line';
    });
    
    if (nonPoliticalTraces.length !== currentData.length) {
        Plotly.deleteTraces('starmap', Array.from({length: currentData.length - nonPoliticalTraces.length}, (_, i) => nonPoliticalTraces.length + i));
    }
    
    politicalTraces = [];
}

function clearTradeRouteTraces() {
    if (!starmapPlot) return;
    
    try {
        // Remove only trade route traces from the plot
        const currentData = starmapPlot.data;
        const traceIndicesToRemove = [];
        
        currentData.forEach((trace, index) => {
            if (trace.name && trace.name.includes('Trade Route')) {
                traceIndicesToRemove.push(index);
            }
        });
        
        if (traceIndicesToRemove.length > 0) {
            // Remove traces in reverse order to maintain indices
            traceIndicesToRemove.reverse().forEach(index => {
                try {
                    Plotly.deleteTraces('starmap', index);
                } catch (traceError) {
                    console.error('Failed to delete trace at index', index, traceError);
                }
            });
        }
        
        // Reapply political overlay if it was active
        reapplyPoliticalOverlay();
        
        updateStatus('Trade routes cleared');
    } catch (error) {
        console.error('Error clearing trade route traces:', error);
        updateStatus('Error clearing trade routes');
    }
}

function clearTerritoryBorderTraces() {
    if (!starmapPlot) return;
    
    // Remove only territory border traces from the plot
    const currentData = starmapPlot.data;
    const traceIndicesToRemove = [];
    
    currentData.forEach((trace, index) => {
        if (trace.name && (trace.name.includes('Territory') || trace.name.includes('Border'))) {
            traceIndicesToRemove.push(index);
        }
    });
    
    if (traceIndicesToRemove.length > 0) {
        // Remove traces in reverse order to maintain indices
        traceIndicesToRemove.reverse().forEach(index => {
            Plotly.deleteTraces('starmap', index);
        });
    }
    
    // Reapply political overlay if it was active
    reapplyPoliticalOverlay();
    
    updateStatus('Territory borders cleared');
}

async function showNationLegend() {
    if (Object.keys(nationsData).length === 0) {
        await loadNationsData();
    }
    
    const legendContent = document.getElementById('nationLegendContent');
    let html = '<div class="row">';
    
    Object.entries(nationsData).forEach(([nationId, nation]) => {
        // Get stars belonging to this nation
        const nationStars = currentStars.filter(star => 
            nation.territories && nation.territories.includes(star.id)
        );
        
        // Build star list HTML
        let starListHtml = '';
        if (nationStars.length > 0) {
            starListHtml = `
                <div class="mt-2">
                    <strong class="text-info">Star Systems:</strong>
                    <ul class="list-unstyled mt-1 ms-2">
                        ${nationStars.map(star => {
                            const fictionalName = star.fictional_name ? ` (${star.fictional_name})` : '';
                            const distance = star.dist ? ` - ${star.dist.toFixed(1)} pc` : '';
                            return `<li class="small">
                                <span style="color: ${nation.color};">•</span> 
                                <strong>${star.name}</strong>${fictionalName}${distance}
                            </li>`;
                        }).join('')}
                    </ul>
                </div>
            `;
        }
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="card bg-secondary h-100" onclick="selectNation('${nationId}')">
                    <div class="card-header d-flex align-items-center">
                        <div class="nation-color-indicator me-2" 
                             style="width: 20px; height: 20px; background-color: ${nation.color}; border-radius: 3px;"></div>
                        <strong>${nation.name}</strong>
                    </div>
                    <div class="card-body">
                        <p class="card-text small">${nation.description}</p>
                        <div class="text-muted small">
                            <div><strong>Government:</strong> ${nation.government_type}</div>
                            <div><strong>Capital:</strong> ${nation.capital_system || 'None'}</div>
                            <div><strong>Systems:</strong> ${nation.territories.length}</div>
                            <div><strong>Population:</strong> ${nation.population}</div>
                        </div>
                        ${starListHtml}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    legendContent.innerHTML = html;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('nationModal'));
    modal.show();
}

function selectNation(nationId) {
    selectedNation = nationId;
    
    // Update visual indication of selection
    document.querySelectorAll('#nationLegendContent .card').forEach(card => {
        card.classList.remove('border-success');
    });
    
    event.currentTarget.classList.add('border-success');
}

function focusOnNation() {
    if (!selectedNation || !nationsData[selectedNation]) {
        updateStatus('Please select a nation first');
        return;
    }
    
    const nation = nationsData[selectedNation];
    const nationStars = currentStars.filter(star => 
        nation.territories.includes(star.id)
    );
    
    if (nationStars.length === 0) {
        updateStatus('No stars found for selected nation');
        return;
    }
    
    // Calculate bounding box for nation's territory
    const xCoords = nationStars.map(s => s.x);
    const yCoords = nationStars.map(s => s.y);
    const zCoords = nationStars.map(s => s.z);
    
    const xRange = [Math.min(...xCoords) - 5, Math.max(...xCoords) + 5];
    const yRange = [Math.min(...yCoords) - 5, Math.max(...yCoords) + 5];
    const zRange = [Math.min(...zCoords) - 5, Math.max(...zCoords) + 5];
    
    // Update the camera view to focus on the nation
    Plotly.relayout('starmap', {
        'scene.camera': {
            center: {
                x: (xRange[0] + xRange[1]) / 2 / 100,
                y: (yRange[0] + yRange[1]) / 2 / 100,
                z: (zRange[0] + zRange[1]) / 2 / 100
            },
            eye: { x: 1.5, y: 1.5, z: 1.5 }
        }
    });
    
    // Close the modal
    bootstrap.Modal.getInstance(document.getElementById('nationModal')).hide();
    
    updateStatus(`Focused on ${nation.name} territory`);
}

// Galactic Directions Functions
async function loadGalacticDirections() {
    try {
        const response = await fetch(`/api/galactic-directions?distance=${galacticDistance}&grid=${galacticGridActive}`);
        if (!response.ok) throw new Error('Failed to fetch galactic directions');
        
        galacticDirectionsData = await response.json();
        updateStatus(`Loaded ${galacticDirectionsData.total_markers} galactic direction markers`);
    } catch (error) {
        console.error('Error loading galactic directions:', error);
        updateStatus(`Error loading galactic directions: ${error.message}`);
    }
}

async function toggleGalacticDirections() {
    const checkbox = document.getElementById('galacticDirections');
    galacticDirectionsActive = checkbox.checked;
    
    if (galacticDirectionsActive) {
        await loadGalacticDirections();
    }
    
    updateGalacticDirectionsDisplay();
}

async function toggleGalacticGrid() {
    const checkbox = document.getElementById('galacticGrid');
    galacticGridActive = checkbox.checked;
    
    if (galacticDirectionsActive || galacticGridActive) {
        await loadGalacticDirections();
    }
    
    updateGalacticDirectionsDisplay();
}

function updateGalacticDistance() {
    const distanceSlider = document.getElementById('galacticDistance');
    const distanceValue = document.getElementById('galacticDistanceValue');
    
    galacticDistance = parseInt(distanceSlider.value);
    distanceValue.textContent = galacticDistance;
    
    if (galacticDirectionsActive || galacticGridActive) {
        loadGalacticDirections().then(() => {
            updateGalacticDirectionsDisplay();
        });
    }
}

function updateGalacticDirectionsDisplay() {
    if (!starmapPlot) return;
    
    // Remove existing galactic traces
    galacticTraces.forEach(traceIndex => {
        Plotly.deleteTraces('starmap', traceIndex);
    });
    galacticTraces = [];
    
    if (!galacticDirectionsData.markers) return;
    
    const tracesToAdd = [];
    
    // Add cardinal direction markers
    if (galacticDirectionsActive) {
        const markers = galacticDirectionsData.markers;
        
        const cardinalTrace = {
            x: markers.map(m => m.x),
            y: markers.map(m => m.y),
            z: markers.map(m => m.z),
            mode: 'markers+text',
            type: 'scatter3d',
            marker: {
                size: 12,
                color: markers.map(m => m.color),
                symbol: 'diamond',
                opacity: 0.9,
                line: {
                    width: 2,
                    color: '#ffffff'
                }
            },
            text: markers.map(m => m.symbol),
            textposition: 'middle center',
            textfont: {
                size: 16,
                color: '#ffffff'
            },
            hovertemplate: markers.map(m => 
                `<b>${m.name}</b><br>` +
                `${m.description}<br>` +
                `Galactic L: ${m.galactic_l}°<br>` +
                `Galactic B: ${m.galactic_b}°<br>` +
                `Position: (${m.x.toFixed(1)}, ${m.y.toFixed(1)}, ${m.z.toFixed(1)}) pc<br>` +
                `<extra></extra>`
            ),
            name: 'Galactic Directions',
            showlegend: true,
            legendgroup: 'galactic'
        };
        
        tracesToAdd.push(cardinalTrace);
    }
    
    // Add galactic grid lines
    if (galacticGridActive && galacticDirectionsData.grid) {
        galacticDirectionsData.grid.forEach(gridLine => {
            const points = gridLine.points;
            if (points && points.length > 0) {
                const gridTrace = {
                    x: points.map(p => p[0]),
                    y: points.map(p => p[1]),
                    z: points.map(p => p[2]),
                    mode: 'lines',
                    type: 'scatter3d',
                    line: {
                        color: gridLine.color,
                        width: 2,
                        dash: gridLine.type === 'galactic_equator' ? 'solid' : 'dash'
                    },
                    hoverinfo: 'skip',
                    showlegend: false,
                    name: `Grid ${gridLine.type}`,
                    legendgroup: 'galactic'
                };
                
                tracesToAdd.push(gridTrace);
            }
        });
    }
    
    // Add all traces at once
    if (tracesToAdd.length > 0) {
        Plotly.addTraces('starmap', tracesToAdd).then(() => {
            // Store trace indices for removal later
            const plotData = starmapPlot.data;
            galacticTraces = tracesToAdd.map((_, index) => plotData.length - tracesToAdd.length + index);
        });
    }
}

// Image Export Functionality
function exportImage(format) {
    if (!starmapPlot) {
        alert('Please update the starmap first before exporting.');
        return;
    }

    // Get the current timestamp for filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const filename = `starmap-felgenland-${timestamp}`;
    
    // Check if we should include UI elements
    const includeUI = document.getElementById('includeUI').checked;
    
    // Export configuration
    const config = {
        filename: filename,
        format: format,
        width: includeUI ? 1920 : 1600,
        height: includeUI ? 1080 : 1200,
        scale: 2 // Higher resolution
    };

    // Show loading indicator
    const statusBar = document.getElementById('statusBar');
    const originalStatus = statusBar.innerHTML;
    statusBar.innerHTML = '<span class="loading"></span>Exporting ' + format.toUpperCase() + ' image...';

    try {
        if (format === 'png') {
            Plotly.downloadImage('starmap', {
                format: 'png',
                width: config.width,
                height: config.height,
                filename: config.filename,
                scale: config.scale
            }).then(() => {
                statusBar.innerHTML = '✅ PNG exported successfully!';
                setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
            }).catch(error => {
                console.error('PNG export failed:', error);
                statusBar.innerHTML = '❌ PNG export failed. Please try again.';
                setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
            });
        } else if (format === 'jpg') {
            Plotly.downloadImage('starmap', {
                format: 'jpeg',
                width: config.width,
                height: config.height,
                filename: config.filename,
                scale: config.scale
            }).then(() => {
                statusBar.innerHTML = '✅ JPG exported successfully!';
                setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
            }).catch(error => {
                console.error('JPG export failed:', error);
                statusBar.innerHTML = '❌ JPG export failed. Please try again.';
                setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
            });
        } else if (format === 'pdf') {
            // For PDF, we'll use a different approach
            exportToPDF(config);
        }
    } catch (error) {
        console.error('Export failed:', error);
        statusBar.innerHTML = '❌ Export failed. Please try again.';
        setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
    }
}

function exportToPDF(config) {
    // First get the image as base64
    Plotly.toImage('starmap', {
        format: 'png',
        width: config.width,
        height: config.height,
        scale: config.scale
    }).then(function(dataURL) {
        // Create PDF using jsPDF (we'll need to include this library)
        // For now, we'll convert the image to PDF on the client side
        
        // Create a temporary canvas to draw the image
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw white background
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw the starmap image
            ctx.drawImage(img, 0, 0);
            
            // Add title and metadata
            ctx.fillStyle = '#000000';
            ctx.font = '24px Arial';
            ctx.fillText('Starmap: A Picture of the Felgenland Saga', 50, 50);
            
            ctx.font = '14px Arial';
            ctx.fillText('Generated on: ' + new Date().toLocaleDateString(), 50, 80);
            
            // Convert canvas to blob and download
            canvas.toBlob(function(blob) {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = config.filename + '.png'; // We'll save as PNG for now
                link.click();
                
                const statusBar = document.getElementById('statusBar');
                statusBar.innerHTML = '✅ PDF (as PNG) exported successfully!';
                setTimeout(() => statusBar.innerHTML = 'Ready - Starmap exported', 3000);
            }, 'image/png');
        };
        
        img.src = dataURL;
    }).catch(error => {
        console.error('PDF export failed:', error);
        const statusBar = document.getElementById('statusBar');
        statusBar.innerHTML = '❌ PDF export failed. Please try again.';
        setTimeout(() => statusBar.innerHTML = 'Ready - Click "Update Starmap" to load stars', 3000);
    });
}

// Enhanced CSV export with image metadata
function exportCSV() {
    if (currentStars.length === 0) {
        alert('No star data to export. Please update the starmap first.');
        return;
    }

    const statusBar = document.getElementById('statusBar');
    const originalStatus = statusBar.innerHTML;
    statusBar.innerHTML = '<span class="loading"></span>Exporting CSV data...';

    try {
        // Add timestamp and export metadata
        const timestamp = new Date().toISOString();
        const metadata = [
            '# Starmap CSV Export - Felgenland Saga',
            '# Generated: ' + timestamp,
            '# Total Stars: ' + currentStars.length,
            '# Magnitude Limit: ' + document.getElementById('magLimit').value,
            '# Max Stars: ' + document.getElementById('starCount').value,
            '#'
        ];

        // Create CSV header
        const headers = ['name', 'ra', 'dec', 'distance', 'magnitude', 'spectral_type', 'x', 'y', 'z'];
        
        // Create CSV content
        let csvContent = metadata.join('\n') + '\n';
        csvContent += headers.join(',') + '\n';
        
        currentStars.forEach(star => {
            const row = [
                `"${star.name || 'Unknown'}"`,
                star.ra || 0,
                star.dec || 0,
                star.distance || 0,
                star.magnitude || 0,
                `"${star.spectral_type || 'Unknown'}"`,
                star.x || 0,
                star.y || 0,
                star.z || 0
            ];
            csvContent += row.join(',') + '\n';
        });

        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `starmap-felgenland-${timestamp.replace(/[:.]/g, '-').slice(0, 19)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        statusBar.innerHTML = '✅ CSV exported successfully!';
        setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
    } catch (error) {
        console.error('CSV export failed:', error);
        statusBar.innerHTML = '❌ CSV export failed. Please try again.';
        setTimeout(() => statusBar.innerHTML = originalStatus, 3000);
    }
}

// ==========================================
// STELLAR REGIONS OVERLAY FUNCTIONS
// ==========================================

async function toggleStellarRegions() {
    console.log('toggleStellarRegions called');
    const checkbox = document.getElementById('stellarRegions');
    stellarRegionsActive = checkbox.checked;
    
    console.log('Stellar regions active:', stellarRegionsActive);
    
    if (stellarRegionsActive) {
        console.log('Loading stellar regions...');
        try {
            await loadStellarRegions();
            console.log('Stellar regions loaded successfully');
        } catch (error) {
            console.error('Failed to load stellar regions:', error);
            return;
        }
    }
    
    console.log('Calling updateStellarRegionsDisplay...');
    updateStellarRegionsDisplay();
}

async function loadStellarRegions() {
    if (Object.keys(stellarRegionsData).length > 0) {
        return; // Already loaded
    }
    
    try {
        updateStatus('Loading stellar regions data...', true);
        
        const response = await fetch('/api/stellar-regions');
        if (!response.ok) {
            throw new Error('Failed to fetch stellar regions data');
        }
        
        const data = await response.json();
        stellarRegionsData = data;
        
        console.log('Stellar regions loaded:', stellarRegionsData);
        updateStatus(`Stellar regions data loaded successfully (${data.regions?.length || 0} regions)`);
        
    } catch (error) {
        console.error('Error loading stellar regions:', error);
        updateStatus(`Error loading stellar regions: ${error.message}`);
        throw error;
    }
}

function generateOctantWireframe(xRange, yRange, zRange) {
    const [xMin, xMax] = xRange;
    const [yMin, yMax] = yRange;
    const [zMin, zMax] = zRange;
    
    // Define the 8 vertices of the cube
    const vertices = [
        [xMin, yMin, zMin], // 0
        [xMax, yMin, zMin], // 1
        [xMax, yMax, zMin], // 2
        [xMin, yMax, zMin], // 3
        [xMin, yMin, zMax], // 4
        [xMax, yMin, zMax], // 5
        [xMax, yMax, zMax], // 6
        [xMin, yMax, zMax]  // 7
    ];
    
    // Define the 12 edges of the cube
    const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0], // bottom face
        [4, 5], [5, 6], [6, 7], [7, 4], // top face
        [0, 4], [1, 5], [2, 6], [3, 7]  // vertical edges
    ];
    
    const x = [], y = [], z = [];
    
    // Generate line segments for each edge
    edges.forEach(edge => {
        const [start, end] = edge;
        const startVertex = vertices[start];
        const endVertex = vertices[end];
        
        // Add start point
        x.push(startVertex[0]);
        y.push(startVertex[1]);
        z.push(startVertex[2]);
        
        // Add end point
        x.push(endVertex[0]);
        y.push(endVertex[1]);
        z.push(endVertex[2]);
        
        // Add NaN to separate line segments
        x.push(NaN);
        y.push(NaN);
        z.push(NaN);
    });
    
    return { x, y, z };
}

function generateSpherePoints(center, radius, resolution = 16) {
    const x = [], y = [], z = [];
    const i = [], j = [], k = [];
    
    // Generate sphere vertices using spherical coordinates
    for (let phi = 0; phi <= resolution; phi++) {
        for (let theta = 0; theta <= resolution; theta++) {
            const phiRad = (phi * Math.PI) / resolution;
            const thetaRad = (theta * 2 * Math.PI) / resolution;
            
            const px = center[0] + radius * Math.sin(phiRad) * Math.cos(thetaRad);
            const py = center[1] + radius * Math.sin(phiRad) * Math.sin(thetaRad);
            const pz = center[2] + radius * Math.cos(phiRad);
            
            x.push(px);
            y.push(py);
            z.push(pz);
        }
    }
    
    // Generate triangular faces for the sphere mesh
    for (let phi = 0; phi < resolution; phi++) {
        for (let theta = 0; theta < resolution; theta++) {
            const first = phi * (resolution + 1) + theta;
            const second = first + resolution + 1;
            
            // First triangle
            i.push(first);
            j.push(second);
            k.push(first + 1);
            
            // Second triangle
            i.push(second);
            j.push(second + 1);
            k.push(first + 1);
        }
    }
    
    return { x, y, z, i, j, k };
}

function getStarsInRegion(region) {
    const regionStars = [];
    
    // For octant-based regions, check all stars against X,Y,Z ranges
    if (region.x_range && region.y_range && region.z_range) {
        currentStars.forEach(star => {
            if (isStarInRegionByLocation(star, region)) {
                regionStars.push(star);
            }
        });
    }
    // Legacy support for old region format
    else if (region.sectors) {
        region.sectors.forEach(sector => {
            if (sector.star_id) {
                const star = currentStars.find(s => s.id === sector.star_id);
                if (star) {
                    regionStars.push(star);
                }
            }
        });
    }
    
    return regionStars;
}

function isStarInRegionByLocation(star, region) {
    // Check based on X,Y,Z ranges for octant-based regions
    if (region.x_range && region.y_range && region.z_range) {
        const x = star.x || 0;
        const y = star.y || 0;
        const z = star.z || 0;
        
        const [xMin, xMax] = region.x_range;
        const [yMin, yMax] = region.y_range;
        const [zMin, zMax] = region.z_range;
        
        return (x >= xMin && x <= xMax && 
                y >= yMin && y <= yMax && 
                z >= zMin && z <= zMax);
    }
    // Legacy support for RA/Dec ranges
    else if (region.ra_range && region.dec_range && region.distance_range) {
        const ra = star.ra || 0;
        const dec = star.dec || 0;
        const dist = star.dist || 0;
        
        const [raMin, raMax] = region.ra_range;
        const [decMin, decMax] = region.dec_range;
        const [distMin, distMax] = region.distance_range;
        
        return (ra >= raMin && ra <= raMax && 
                dec >= decMin && dec <= decMax && 
                dist >= distMin && dist <= distMax);
    }
    return false;
}

function updateStellarRegionsDisplay() {
    if (!starmapPlot) {
        console.error('Starmap plot not initialized');
        return;
    }
    
    // Remove existing stellar regions traces
    clearStellarRegionsTraces();
    
    if (!stellarRegionsActive) {
        console.log('Stellar regions not active, skipping display');
        return;
    }
    
    if (!stellarRegionsData || !stellarRegionsData.regions) {
        console.error('No stellar regions data available');
        return;
    }
    
    console.log('Updating stellar regions display with', stellarRegionsData.regions.length, 'regions');
    
    const tracesToAdd = [];
    
    // Add octant boundary traces
    stellarRegionsData.regions.forEach((region, index) => {
        console.log(`Processing region: ${region.name}`);
        
        // Only handle octant-based regions with x,y,z ranges
        if (region.x_range && region.y_range && region.z_range) {
            console.log(`Creating wireframe for ${region.name}`);
            
            const wireframeData = generateOctantWireframe(region.x_range, region.y_range, region.z_range);
            
            const regionTrace = {
                type: 'scatter3d',
                mode: 'lines',
                x: wireframeData.x,
                y: wireframeData.y,
                z: wireframeData.z,
                line: {
                    color: region.color_rgb ? `rgb(${region.color_rgb.join(',')})` : '#888888',
                    width: 3
                },
                name: `${region.short_name || region.name}`,
                showlegend: true,
                legendgroup: `stellar_region_${index}`,
                hovertemplate: 
                    `<b>${region.name}</b><br>` +
                    `${region.description}<br>` +
                    `X: ${region.x_range[0]} to ${region.x_range[1]} parsecs<br>` +
                    `Y: ${region.y_range[0]} to ${region.y_range[1]} parsecs<br>` +
                    `Z: ${region.z_range[0]} to ${region.z_range[1]} parsecs<br>` +
                    `<extra></extra>`
            };
            
            const labelTrace = {
                x: [region.center_point[0]],
                y: [region.center_point[1]],
                z: [region.center_point[2]],
                mode: 'text',
                type: 'scatter3d',
                text: [region.short_name || region.name],
                textfont: {
                    size: 10,
                    color: region.color_rgb ? `rgb(${region.color_rgb.join(',')})` : '#ffffff'
                },
                name: `${region.name} Label`,
                showlegend: false,
                hoverinfo: 'skip'
            };
            
            tracesToAdd.push(regionTrace);
            tracesToAdd.push(labelTrace);
        } else {
            console.warn(`Region ${region.name} does not have x_range, y_range, z_range`);
        }
    });
    
    // Add all traces to the plot
    if (tracesToAdd.length > 0) {
        console.log('Adding', tracesToAdd.length, 'traces to plot');
        Plotly.addTraces('starmap', tracesToAdd).then(() => {
            // Track trace indices for cleanup
            const currentTraceCount = starmapPlot.data.length;
            for (let i = 0; i < tracesToAdd.length; i++) {
                stellarRegionsTraces.push(currentTraceCount - tracesToAdd.length + i);
            }
            
            console.log('Successfully added stellar regions traces');
            updateStatus(`Stellar regions overlay applied (${stellarRegionsData.regions.length} octants)`);
        }).catch(error => {
            console.error('Error adding traces:', error);
            updateStatus(`Error displaying stellar regions: ${error.message}`);
        });
    } else {
        console.warn('No traces to add');
        updateStatus('No stellar regions to display');
    }
}

function clearStellarRegionsTraces() {
    if (!starmapPlot || stellarRegionsTraces.length === 0) return;
    
    // Remove traces in reverse order to maintain indices
    stellarRegionsTraces.reverse().forEach(traceIndex => {
        if (traceIndex < starmapPlot.data.length) {
            Plotly.deleteTraces('starmap', traceIndex);
        }
    });
    
    stellarRegionsTraces = [];
}

function selectStellarRegion(regionName) {
    selectedRegion = regionName;
    
    // Find the region data
    const region = stellarRegionsData.regions?.find(r => r.name === regionName);
    if (!region) return;
    
    // Update status with region info
    updateStatus(`Selected region: ${region.name} (${region.population})`);
    
    // Optional: Focus camera on region center
    if (starmapPlot) {
        const center = region.center_point;
        const currentCamera = starmapPlot.layout.scene.camera;
        
        // Calculate camera position to look at region center
        const distance = 100; // Distance from center
        const newCamera = {
            eye: {
                x: center[0] / distance + 1,
                y: center[1] / distance + 1,
                z: center[2] / distance + 1
            },
            center: {
                x: center[0] / distance,
                y: center[1] / distance,
                z: center[2] / distance
            }
        };
        
        Plotly.relayout('starmap', {
            'scene.camera': newCamera
        });
    }
}

async function loadRegionBoundaries(regionName) {
    try {
        updateStatus(`Loading boundaries for ${regionName}...`, true);
        
        const response = await fetch(`/api/stellar-region/${regionName}/boundaries?resolution=20`);
        if (!response.ok) {
            throw new Error(`Failed to fetch boundaries for ${regionName}`);
        }
        
        const data = await response.json();
        
        // Add boundary trace
        if (data.boundary_points && data.boundary_points.length > 0) {
            const boundaryTrace = {
                x: data.boundary_points.map(p => p[0]),
                y: data.boundary_points.map(p => p[1]),
                z: data.boundary_points.map(p => p[2]),
                mode: 'markers',
                type: 'scatter3d',
                marker: {
                    size: 3,
                    color: '#ffffff',
                    opacity: 0.2
                },
                name: `${regionName} Boundaries`,
                showlegend: false,
                hovertemplate: `${regionName} Boundary<extra></extra>`,
                hoverinfo: 'skip'
            };
            
            Plotly.addTraces('starmap', [boundaryTrace]).then(() => {
                stellarRegionsTraces.push(starmapPlot.data.length - 1);
                updateStatus(`Boundaries loaded for ${regionName}`);
            });
        }
        
    } catch (error) {
        console.error(`Error loading boundaries for ${regionName}:`, error);
        updateStatus(`Error loading boundaries: ${error.message}`);
    }
}

// Function to reapply stellar regions overlay after starmap updates
function reapplyStellarRegionsOverlay() {
    if (stellarRegionsActive && stellarRegionsData.regions) {
        try {
            updateStellarRegionsDisplay();
        } catch (error) {
            console.error('Error reapplying stellar regions overlay:', error);
            updateStatus('Warning: Stellar regions overlay may need to be refreshed');
        }
    }
}

// ==========================================
// STELLAR REGIONS SELECTION FUNCTIONS
// ==========================================

function showRegionSelectionUI() {
    const regionSelectionDiv = document.getElementById('regionSelection');
    const regionSelect = document.getElementById('regionSelect');
    
    if (regionSelectionDiv && regionSelect) {
        // Clear existing options
        regionSelect.innerHTML = '<option value="">Select a Region...</option>';
        
        // Add regions to the dropdown
        if (stellarRegionsData.regions) {
            stellarRegionsData.regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region.name;
                option.textContent = region.name;
                regionSelect.appendChild(option);
            });
        }
        
        // Remove any existing event listener and add new one
        regionSelect.removeEventListener('change', handleRegionSelection);
        regionSelect.addEventListener('change', handleRegionSelection);
        
        // Show the region selection UI
        regionSelectionDiv.style.display = 'block';
    }
}

function hideRegionSelectionUI() {
    const regionSelectionDiv = document.getElementById('regionSelection');
    if (regionSelectionDiv) {
        regionSelectionDiv.style.display = 'none';
    }
}

function handleRegionSelection() {
    const regionSelect = document.getElementById('regionSelect');
    const selectedRegionName = regionSelect.value;
    
    // Enable/disable buttons based on selection
    const focusBtn = document.getElementById('focusRegionBtn');
    const detailsBtn = document.getElementById('detailsRegionBtn');
    const boundariesBtn = document.getElementById('boundariesRegionBtn');
    
    if (selectedRegionName) {
        focusBtn.disabled = false;
        detailsBtn.disabled = false;
        boundariesBtn.disabled = false;
        selectedRegion = selectedRegionName;
        updateStatus(`Selected region: ${selectedRegionName}`);
    } else {
        focusBtn.disabled = true;
        detailsBtn.disabled = true;
        boundariesBtn.disabled = true;
        selectedRegion = null;
        updateStatus('Region selection cleared');
    }
}

function focusOnSelectedRegion() {
    if (!selectedRegion || !stellarRegionsData.regions) {
        updateStatus('Please select a region first');
        return;
    }
    
    const region = stellarRegionsData.regions.find(r => r.name === selectedRegion);
    if (!region) {
        updateStatus('Selected region not found');
        return;
    }
    
    // Focus the camera on the region's center
    const centerX = region.center_point[0];
    const centerY = region.center_point[1];
    const centerZ = region.center_point[2];
    
    // Calculate appropriate zoom level based on region diameter
    const diameter = region.diameter || 50;
    const distance = Math.max(diameter * 2, 100); // Minimum distance of 100
    
    const newCamera = {
        center: {
            x: centerX / distance,
            y: centerY / distance,
            z: centerZ / distance
        },
        eye: {
            x: centerX / distance + 1.5,
            y: centerY / distance + 1.5,
            z: centerZ / distance + 1.5
        }
    };
    
    Plotly.relayout('starmap', {
        'scene.camera': newCamera
    });
    
    updateStatus(`Focused on ${selectedRegion}`);
}

function showRegionDetails() {
    if (!selectedRegion || !stellarRegionsData.regions) {
        updateStatus('Please select a region first');
        return;
    }
    
    const region = stellarRegionsData.regions.find(r => r.name === selectedRegion);
    if (!region) {
        updateStatus('Selected region not found');
        return;
    }
    
    // Show region details in the search results panel
    const searchResults = document.getElementById('searchResults');
    const searchResultsList = document.getElementById('searchResultsList');
    
    if (searchResults && searchResultsList) {
        const detailsHtml = `
            <div class="region-details">
                <h6 class="text-primary mb-3">🌌 ${region.name}</h6>
                
                <div class="region-info mb-3">
                    <div class="star-property">
                        <span><strong>Description:</strong></span>
                        <span>${region.description}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Established:</strong></span>
                        <span>${region.established}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Population:</strong></span>
                        <span>${region.population}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Diameter:</strong></span>
                        <span>${region.diameter} parsecs</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Economic Zone:</strong></span>
                        <span>${region.economic_zone}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Trade Routes:</strong></span>
                        <span>${region.trade_routes}</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Significance:</strong></span>
                        <span>${region.significance}</span>
                    </div>
                </div>
                
                <div class="region-coordinates mb-3">
                    <h6>Coordinates</h6>
                    <div class="star-property">
                        <span><strong>Center:</strong></span>
                        <span>(${region.center_point[0].toFixed(2)}, ${region.center_point[1].toFixed(2)}, ${region.center_point[2].toFixed(2)})</span>
                    </div>
                    <div class="star-property">
                        <span><strong>RA Range:</strong></span>
                        <span>${region.ra_range[0]}° - ${region.ra_range[1]}°</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Dec Range:</strong></span>
                        <span>${region.dec_range[0]}° - ${region.dec_range[1]}°</span>
                    </div>
                    <div class="star-property">
                        <span><strong>Distance Range:</strong></span>
                        <span>${region.distance_range[0]} - ${region.distance_range[1]} parsecs</span>
                    </div>
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="focusOnSelectedRegion()">Focus on Region</button>
                    <button class="btn btn-sm btn-outline-success" onclick="showRegionBoundaries()">Show Boundaries</button>
                    <button class="btn btn-sm btn-outline-light" onclick="clearRegionSelection()">Clear</button>
                </div>
            </div>
        `;
        
        searchResultsList.innerHTML = detailsHtml;
        searchResults.style.display = 'block';
        
        updateStatus(`Showing details for ${selectedRegion}`);
    }
}

function showRegionBoundaries() {
    if (!selectedRegion) {
        updateStatus('Please select a region first');
        return;
    }
    
    loadRegionBoundaries(selectedRegion);
}

function clearRegionSelection() {
    const regionSelect = document.getElementById('regionSelect');
    if (regionSelect) {
        regionSelect.value = '';
        handleRegionSelection(); // This will disable buttons and clear selectedRegion
    }
    
    // Clear the search results panel
    const searchResults = document.getElementById('searchResults');
    if (searchResults) {
        searchResults.style.display = 'none';
    }
}

function clearRegionBoundaries() {
    // Clear existing boundary traces
    if (starmapPlot && starmapPlot.data) {
        const traces = starmapPlot.data;
        const boundaryIndices = [];
        
        traces.forEach((trace, index) => {
            if (trace.name && trace.name.includes('Boundaries')) {
                boundaryIndices.push(index);
            }
        });
        
        if (boundaryIndices.length > 0) {
            boundaryIndices.reverse().forEach(index => {
                try {
                    Plotly.deleteTraces('starmap', index);
                } catch (error) {
                    console.error('Error deleting boundary trace:', error);
                }
            });
        }
    }
    
    updateStatus('Region boundaries cleared');
}

// Function to fetch habitability explanation for a star
async function fetchHabitabilityExplanation(starId) {
    try {
        const response = await fetch(`/api/star/${starId}/habitability`);
        if (!response.ok) {
            throw new Error('Failed to fetch habitability explanation');
        }
        
        const data = await response.json();
        
        if (data.success && data.data.explanation) {
            const explanationElement = document.getElementById(`habitability-explanation-${starId}`);
            if (explanationElement) {
                explanationElement.textContent = data.data.explanation;
            }
        }
    } catch (error) {
        console.error('Error fetching habitability explanation:', error);
        const explanationElement = document.getElementById(`habitability-explanation-${starId}`);
        if (explanationElement) {
            explanationElement.textContent = 'Unable to load habitability assessment.';
        }
    }
}