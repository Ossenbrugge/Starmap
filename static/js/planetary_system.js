// Planetary System Visualization Module

let currentSystemData = null;
let systemPlot = null;
let animationInterval = null;
let animationRunning = false;
let currentAnimationTime = 0;

// Planet type colors and characteristics with proper scaling
const PLANET_TYPES = {
    'Terrestrial': { color: '#8B4513', baseSize: 6 },      // Brown - Rocky planets
    'Super-Earth': { color: '#228B22', baseSize: 8 },      // Green - Large rocky planets  
    'Sub-Earth': { color: '#CD853F', baseSize: 4 },        // Tan - Small rocky planets
    'Gas Giant': { color: '#FF4500', baseSize: 12 },       // Orange - Jupiter-like planets
    'Hot Jupiter': { color: '#FF6347', baseSize: 11 },     // Red - Close-in gas giants
    'Ice Giant': { color: '#4169E1', baseSize: 9 },        // Blue - Uranus/Neptune-like
    'Neptune-like': { color: '#0000CD', baseSize: 9 },     // Dark blue - Neptune analogs
    'Unknown': { color: '#696969', baseSize: 6 }           // Gray - Unclassified planets
};

// Base habitable zone boundaries for Sun-like stars (G2V, 1.0 solar luminosity)
const BASE_HABITABLE_ZONE = {
    inner: 0.95,  // AU
    outer: 1.37   // AU
};

// Calculate habitable zone for a star based on its luminosity
function calculateHabitableZone(starLuminosity) {
    const luminosity = starLuminosity || 1.0; // Default to solar luminosity if not available
    return {
        inner: BASE_HABITABLE_ZONE.inner * Math.sqrt(luminosity),
        outer: BASE_HABITABLE_ZONE.outer * Math.sqrt(luminosity)
    };
}

// Binary star detection and separation calculation
function detectBinarySystem(starData) {
    const spectralClass = starData.properties.spectral_class || '';
    const hasSpectralSeparator = /[+\/&]/.test(spectralClass);
    const hasComponentData = starData.properties.comp || starData.properties.comp_primary;
    
    if (hasSpectralSeparator || hasComponentData) {
        return {
            isBinary: true,
            spectralClass: spectralClass,
            components: parseSpectralComponents(spectralClass),
            estimatedSeparation: estimateBinarySeparation(starData)
        };
    }
    
    return { isBinary: false };
}

// Parse spectral components from combined spectral class
function parseSpectralComponents(spectralClass) {
    const components = [];
    
    // Split by common separators
    const separators = ['+', '/', '&'];
    for (const sep of separators) {
        if (spectralClass.includes(sep)) {
            const parts = spectralClass.split(sep).map(s => s.trim());
            parts.forEach((part, index) => {
                if (part) {
                    components.push({
                        spectralType: part,
                        component: index === 0 ? 'A' : 'B',
                        isPrimary: index === 0
                    });
                }
            });
            break;
        }
    }
    
    // If no separators found, assume single star
    if (components.length === 0) {
        components.push({
            spectralType: spectralClass,
            component: 'A',
            isPrimary: true
        });
    }
    
    return components;
}

// Estimate binary star separation for visualization
function estimateBinarySeparation(starData) {
    const spectralClass = starData.properties.spectral_class || '';
    const distance = starData.properties.distance || 10; // parsecs
    
    // Estimate separation based on spectral type and distance
    // Most visual binaries have separations between 0.1" to 10" as seen from Earth
    // Convert to AU using distance: separation_AU = separation_arcsec * distance_pc
    
    let estimatedSeparationArcsec = 1.0; // Default 1 arcsecond
    
    // Adjust based on spectral type patterns
    if (spectralClass.includes('M')) {
        estimatedSeparationArcsec = 0.5; // M-dwarf binaries tend to be closer
    } else if (spectralClass.includes('G') || spectralClass.includes('K')) {
        estimatedSeparationArcsec = 1.0; // Sun-like stars
    } else if (spectralClass.includes('A') || spectralClass.includes('F')) {
        estimatedSeparationArcsec = 2.0; // Hotter stars can be wider
    }
    
    // Convert to AU
    const separationAU = estimatedSeparationArcsec * distance;
    
    // For visualization purposes, ensure minimum separation
    return Math.max(separationAU, 0.1);
}

// Planet size calculation for better proportional display
function calculatePlanetSize(planet, typeInfo) {
    const radius = planet.radius_earth || 1.0;
    
    // Use logarithmic scaling for very large planets to prevent Jupiter/Saturn from being huge
    let scaledRadius;
    if (radius > 5.0) {
        // Logarithmic scaling for gas giants and ice giants
        scaledRadius = 5 + Math.log(radius - 4) * 3;
    } else {
        // Linear scaling for smaller planets
        scaledRadius = radius;
    }
    
    // Apply base size from planet type and ensure minimum size
    const calculatedSize = typeInfo.baseSize * Math.sqrt(scaledRadius);
    
    // Ensure planets don't get too large or too small
    return Math.max(4, Math.min(calculatedSize, 20));
}

function openSystemView(starData) {
    if (!starData.planets || starData.planets.length === 0) {
        updateStatus('No planetary data available for this star');
        return;
    }
    
    currentSystemData = starData;
    
    // Update modal title
    document.getElementById('systemModalLabel').textContent = 
        `${starData.name} Planetary System`;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('systemModal'));
    modal.show();
    
    // Initialize the system view when modal is shown
    document.getElementById('systemModal').addEventListener('shown.bs.modal', function() {
        initializeSystemView();
    }, { once: true });
}

function initializeSystemView() {
    if (!currentSystemData) return;
    
    // Update system information
    updateSystemInfo();
    
    // Create the planetary system visualization
    createSystemVisualization();
    
    updateStatus(`Viewing ${currentSystemData.name} system with ${currentSystemData.planets.length} planets`);
}

function updateSystemInfo() {
    const starDetails = document.getElementById('starSystemDetails');
    const planetList = document.getElementById('planetList');
    
    // Check if this is a binary system
    const binaryInfo = detectBinarySystem(currentSystemData);
    
    // Star information
    let starInfoHtml = `
        <div class="system-star-info">
            <div class="mb-2">
                <strong>Star:</strong> ${currentSystemData.name}
            </div>
            <div class="mb-2">
                <strong>Type:</strong> ${currentSystemData.designation_type}
            </div>
            <div class="mb-2">
                <strong>Constellation:</strong> ${currentSystemData.constellation_full || currentSystemData.constellation}
            </div>
            <div class="mb-2">
                <strong>Distance:</strong> ${currentSystemData.properties.distance.toFixed(2)} pc
            </div>`;
    
    if (binaryInfo.isBinary) {
        starInfoHtml += `
            <div class="mb-2">
                <strong>System Type:</strong> <span class="text-warning">Binary Star System</span>
            </div>
            <div class="mb-2">
                <strong>Components:</strong> ${binaryInfo.components.map(comp => `${comp.component}: ${comp.spectralType}`).join(', ')}
            </div>
            <div class="mb-2">
                <strong>Est. Separation:</strong> ${binaryInfo.estimatedSeparation.toFixed(2)} AU
            </div>`;
    } else {
        starInfoHtml += `
            <div class="mb-2">
                <strong>Spectral Class:</strong> ${currentSystemData.properties.spectral_class}
            </div>`;
    }
    
    starInfoHtml += `
            <div class="mb-2">
                <strong>Planets:</strong> ${currentSystemData.planets.length}
            </div>
        </div>
    `;
    
    starDetails.innerHTML = starInfoHtml;
    
    // Calculate habitable zone for this star
    const starLuminosity = currentSystemData.properties.luminosity || 1.0;
    const habitableZone = calculateHabitableZone(starLuminosity);
    
    // Planet list
    let planetsHtml = '';
    currentSystemData.planets.forEach((planet, index) => {
        const typeInfo = PLANET_TYPES[planet.type] || PLANET_TYPES['Unknown'];
        const inHabitableZone = planet.distance_au >= habitableZone.inner && 
                               planet.distance_au <= habitableZone.outer;
        
        planetsHtml += `
            <div class="planet-card mb-2 p-2" style="border: 1px solid #444; border-radius: 4px; cursor: pointer;"
                 onclick="highlightPlanet(${index})" id="planet-card-${index}">
                <div class="d-flex align-items-center mb-1">
                    <div class="planet-color-indicator me-2" 
                         style="width: 12px; height: 12px; border-radius: 50%; background-color: ${typeInfo.color};"></div>
                    <strong class="text-info">${planet.name}</strong>
                    ${planet.confirmed ? '<span class="badge bg-success ms-2">Confirmed</span>' : '<span class="badge bg-warning ms-2">Candidate</span>'}
                    ${inHabitableZone ? '<span class="badge bg-primary ms-1">Habitable Zone</span>' : ''}
                </div>
                <div class="planet-details">
                    <small class="text-muted">
                        <div>Type: ${planet.type}</div>
                        <div>Distance: ${planet.distance_au} AU</div>
                        <div>Mass: ${planet.mass_earth}× Earth</div>
                        <div>Radius: ${planet.radius_earth}× Earth</div>
                        <div>Period: ${planet.orbital_period_days} days</div>
                        <div>Discovery: ${planet.discovery_year}</div>
                        ${planet.moons && planet.moons.length > 0 ? `
                            <div class="text-info mt-1">
                                🌙 ${planet.moons.length} moon${planet.moons.length > 1 ? 's' : ''}: 
                                ${planet.moons.map(moon => moon.name).join(', ')}
                            </div>
                        ` : ''}
                    </small>
                </div>
            </div>
        `;
    });
    
    planetList.innerHTML = planetsHtml;
}

function createSystemVisualization() {
    if (!currentSystemData || !currentSystemData.planets) return;
    
    const planets = currentSystemData.planets;
    
    // Work directly in AU - no artificial scaling needed
    const maxDistance = Math.max(...planets.map(p => p.distance_au));
    // Remove artificial scaling - work in real AU coordinates
    
    // Create traces for planets
    const traces = [];
    
    // Calculate habitable zone for this star
    const starLuminosity = currentSystemData.properties.luminosity || 1.0;
    const habitableZone = calculateHabitableZone(starLuminosity);
    
    // Add habitable zone in AU
    const hzInner = habitableZone.inner;
    const hzOuter = habitableZone.outer;
    
    // Habitable zone ring
    const hzAngles = Array.from({length: 100}, (_, i) => i * 2 * Math.PI / 100);
    traces.push({
        x: hzAngles.map(a => hzInner * Math.cos(a)),
        y: hzAngles.map(a => hzInner * Math.sin(a)),
        mode: 'lines',
        type: 'scatter',
        line: { color: 'rgba(0, 255, 0, 0.3)', width: 2, dash: 'dot' },
        name: 'Habitable Zone (Inner)',
        showlegend: false,
        hoverinfo: 'skip'
    });
    
    traces.push({
        x: hzAngles.map(a => hzOuter * Math.cos(a)),
        y: hzAngles.map(a => hzOuter * Math.sin(a)),
        mode: 'lines',
        type: 'scatter',
        line: { color: 'rgba(0, 255, 0, 0.3)', width: 2, dash: 'dot' },
        name: 'Habitable Zone (Outer)',
        showlegend: false,
        hoverinfo: 'skip'
    });
    
    // Add orbital paths
    planets.forEach((planet, index) => {
        const orbitRadius = planet.distance_au;
        const angles = Array.from({length: 100}, (_, i) => i * 2 * Math.PI / 100);
        
        traces.push({
            x: angles.map(a => orbitRadius * Math.cos(a)),
            y: angles.map(a => orbitRadius * Math.sin(a)),
            mode: 'lines',
            type: 'scatter',
            line: { color: 'rgba(255, 255, 255, 0.3)', width: 1 },
            name: `${planet.name} Orbit`,
            showlegend: false,
            hoverinfo: 'skip'
        });
    });
    
    // Add planets with improved sizing
    planets.forEach((planet, index) => {
        const typeInfo = PLANET_TYPES[planet.type] || PLANET_TYPES['Unknown'];
        const orbitRadius = planet.distance_au;
        
        // Calculate initial position (can be animated later)
        const angle = (index * 60) * Math.PI / 180; // Spread planets around
        
        // Improved planet size calculation
        const planetSize = calculatePlanetSize(planet, typeInfo);
        
        traces.push({
            x: [orbitRadius * Math.cos(angle)],
            y: [orbitRadius * Math.sin(angle)],
            mode: 'markers',
            type: 'scatter',
            marker: {
                color: typeInfo.color,
                size: planetSize,
                line: { color: 'white', width: 1 }
            },
            name: planet.name,
            text: [`${planet.name}<br>Type: ${planet.type}<br>Distance: ${planet.distance_au} AU<br>Mass: ${planet.mass_earth}× Earth<br>Radius: ${planet.radius_earth}× Earth<br>Discovery: ${planet.discovery_year}`],
            hovertemplate: '%{text}<extra></extra>',
            customdata: [index],
            showlegend: true
        });
    });
    
    // Add the star(s) at center - handle binary systems
    const binaryInfo = detectBinarySystem(currentSystemData);
    
    if (binaryInfo.isBinary && binaryInfo.components.length > 1) {
        // Binary star system - display both components
        const separationAU = binaryInfo.estimatedSeparation;
        
        // Position stars along X-axis for simplicity (in AU)
        const star1X = -separationAU / 2;
        const star2X = separationAU / 2;
        
        // Primary star (Component A)
        traces.push({
            x: [star1X],
            y: [0],
            mode: 'markers',
            type: 'scatter',
            marker: {
                color: 'yellow',
                size: 22,
                symbol: 'star',
                line: { color: 'orange', width: 2 }
            },
            name: `${currentSystemData.name} A`,
            text: [`${currentSystemData.name} A (Primary)<br>Spectral Class: ${binaryInfo.components[0].spectralType}<br>Distance: ${currentSystemData.properties.distance.toFixed(2)} pc<br>Estimated Separation: ${separationAU.toFixed(2)} AU`],
            hovertemplate: '%{text}<extra></extra>',
            showlegend: true
        });
        
        // Secondary star (Component B)
        const secondarySize = binaryInfo.components[1].spectralType.includes('M') ? 16 : 20;
        const secondaryColor = binaryInfo.components[1].spectralType.includes('M') ? 'red' : 
                              binaryInfo.components[1].spectralType.includes('K') ? 'orange' : 'yellow';
        
        traces.push({
            x: [star2X],
            y: [0],
            mode: 'markers',
            type: 'scatter',
            marker: {
                color: secondaryColor,
                size: secondarySize,
                symbol: 'star',
                line: { color: 'darkorange', width: 2 }
            },
            name: `${currentSystemData.name} B`,
            text: [`${currentSystemData.name} B (Secondary)<br>Spectral Class: ${binaryInfo.components[1].spectralType}<br>Distance: ${currentSystemData.properties.distance.toFixed(2)} pc<br>Estimated Separation: ${separationAU.toFixed(2)} AU`],
            hovertemplate: '%{text}<extra></extra>',
            showlegend: true
        });
        
        // Add a line connecting the binary pair
        traces.push({
            x: [star1X, star2X],
            y: [0, 0],
            mode: 'lines',
            type: 'scatter',
            line: { color: 'rgba(255, 255, 255, 0.5)', width: 2, dash: 'dash' },
            name: 'Binary Connection',
            showlegend: false,
            hoverinfo: 'skip'
        });
    } else {
        // Single star system
        traces.push({
            x: [0],
            y: [0],
            mode: 'markers',
            type: 'scatter',
            marker: {
                color: 'yellow',
                size: 20,
                symbol: 'star',
                line: { color: 'orange', width: 2 }
            },
            name: currentSystemData.name,
            text: [`${currentSystemData.name}<br>Spectral Class: ${currentSystemData.properties.spectral_class}<br>Distance: ${currentSystemData.properties.distance.toFixed(2)} pc`],
            hovertemplate: '%{text}<extra></extra>',
            showlegend: true
        });
    }
    
    const layout = {
        title: {
            text: `${currentSystemData.name} Planetary System`,
            font: { color: 'white', size: 16 }
        },
        xaxis: {
            title: 'Distance (AU)',
            gridcolor: '#444',
            zerolinecolor: '#666',
            showgrid: true,
            zeroline: true,
            scaleanchor: 'y',
            scaleratio: 1,
            tickformat: '.1f',
            ticksuffix: ' AU'
        },
        yaxis: {
            title: 'Distance (AU)',
            gridcolor: '#444',
            zerolinecolor: '#666',
            showgrid: true,
            zeroline: true,
            tickformat: '.1f',
            ticksuffix: ' AU'
        },
        paper_bgcolor: '#000000',
        plot_bgcolor: '#000000',
        font: { color: 'white' },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        showlegend: true,
        legend: {
            x: 1.02,
            y: 1,
            bgcolor: 'rgba(0,0,0,0.5)',
            bordercolor: '#444',
            borderwidth: 1
        }
    };
    
    const config = {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
        responsive: true
    };
    
    // Create the plot
    systemPlot = Plotly.newPlot('systemMap', traces, layout, config);
    
    // Add click event for planet highlighting
    document.getElementById('systemMap').on('plotly_click', function(data) {
        if (data.points && data.points.length > 0) {
            const point = data.points[0];
            console.log('Clicked point:', point); // Debug
            
            // Check if this is a planet (has customdata)
            if (point.customdata !== undefined && Array.isArray(point.customdata)) {
                const planetIndex = point.customdata[0];
                if (planetIndex !== undefined) {
                    highlightPlanet(planetIndex);
                }
            } else if (point.customdata !== undefined) {
                // Handle single value customdata
                const planetIndex = point.customdata;
                if (planetIndex !== undefined) {
                    highlightPlanet(planetIndex);
                }
            }
        }
    });
}

function highlightPlanet(planetIndex) {
    // Highlight planet card
    document.querySelectorAll('.planet-card').forEach(card => {
        card.style.backgroundColor = '';
        card.style.borderColor = '#444';
    });
    
    const planetCard = document.getElementById(`planet-card-${planetIndex}`);
    if (planetCard) {
        planetCard.style.backgroundColor = 'rgba(116, 185, 255, 0.2)';
        planetCard.style.borderColor = '#74b9ff';
    }
    
    // Update status
    const planet = currentSystemData.planets[planetIndex];
    updateStatus(`Selected: ${planet.name} (${planet.type})`);
}

function toggleSystemView() {
    if (currentSystemData && currentSystemData.planets && currentSystemData.planets.length > 0) {
        openSystemView(currentSystemData);
    } else {
        updateStatus('No planetary system data available');
    }
}

function toggleSystemAnimation() {
    const toggleButton = document.getElementById('animationToggleText');
    
    if (animationRunning) {
        // Stop animation
        if (animationInterval) {
            clearInterval(animationInterval);
            animationInterval = null;
        }
        animationRunning = false;
        toggleButton.textContent = '▶️ Start Animation';
    } else {
        // Start animation
        animationRunning = true;
        toggleButton.textContent = '⏸️ Stop Animation';
        
        animationInterval = setInterval(() => {
            animateSystem();
        }, 100); // Update every 100ms
    }
}

function animateSystem() {
    if (!systemPlot || !currentSystemData) return;
    
    try {
        currentAnimationTime += 0.01; // Animation speed
        
        // Work directly in AU coordinates
        // Collect all updates for batch processing
        const updates = {};
        const traceIndices = [];
        
        currentSystemData.planets.forEach((planet, index) => {
            const orbitRadius = planet.distance_au;
            
            // Calculate orbital speed (faster for closer planets - Kepler's laws)
            const orbitalSpeed = 0.5 / Math.sqrt(planet.distance_au); // Slower animation
            const angle = (currentAnimationTime * orbitalSpeed) + (index * Math.PI / 3); // Offset start positions
            
            const newX = orbitRadius * Math.cos(angle);
            const newY = orbitRadius * Math.sin(angle);
            
            // Find the correct trace index for this planet
            const plotDiv = document.getElementById('systemMap');
            if (plotDiv && plotDiv.data) {
                const traceIndex = plotDiv.data.findIndex(trace => trace.name === planet.name);
                if (traceIndex !== -1) {
                    traceIndices.push(traceIndex);
                    if (!updates.x) updates.x = [];
                    if (!updates.y) updates.y = [];
                    updates.x.push([newX]);
                    updates.y.push([newY]);
                }
            }
        });
        
        // Apply all updates at once
        if (traceIndices.length > 0) {
            Plotly.restyle('systemMap', updates, traceIndices);
        }
        
    } catch (error) {
        console.error('Animation error:', error);
        // Stop animation on error
        if (animationInterval) {
            clearInterval(animationInterval);
            animationInterval = null;
            animationRunning = false;
            const toggleButton = document.getElementById('animationToggleText');
            if (toggleButton) {
                toggleButton.textContent = '▶️ Start Animation';
            }
        }
    }
}

// Export functions for use in main starmap.js
window.PlanetarySystem = {
    openSystemView,
    toggleSystemView,
    toggleSystemAnimation,
    highlightPlanet
};