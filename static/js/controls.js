// Controls Window JavaScript
// This handles communication between the control window and main starmap window

let mainWindow = null;
let isControlWindow = window.location.pathname.includes('/controls');

// Connection management
function setupWindowCommunication() {
    if (isControlWindow) {
        // This is the control window
        mainWindow = window.opener;
        
        if (!mainWindow) {
            document.getElementById('connectionStatus').textContent = 'Disconnected';
            document.getElementById('connectionStatus').className = 'badge bg-danger';
            return;
        }
        
        // Check connection periodically
        setInterval(checkConnection, 1000);
        
        // Listen for messages from main window
        window.addEventListener('message', handleMainWindowMessage);
        
        // Set up event listeners for controls
        setupControlEventListeners();
        
        // Initial sync request
        sendToMainWindow('requestSync', {});
        
    } else {
        // This is the main window - set up to handle control window messages
        window.addEventListener('message', handleControlWindowMessage);
    }
}

function checkConnection() {
    if (!mainWindow || mainWindow.closed) {
        document.getElementById('connectionStatus').textContent = 'Disconnected';
        document.getElementById('connectionStatus').className = 'badge bg-danger';
    } else {
        document.getElementById('connectionStatus').textContent = 'Connected';
        document.getElementById('connectionStatus').className = 'badge bg-success';
    }
}

function sendToMainWindow(action, data) {
    if (mainWindow && !mainWindow.closed) {
        mainWindow.postMessage({ action, data, source: 'controls' }, '*');
    }
}

function sendToControlWindow(action, data) {
    // Find control window (if any) and send message
    // This would be called from the main window
    if (window.controlWindow && !window.controlWindow.closed) {
        window.controlWindow.postMessage({ action, data, source: 'main' }, '*');
    }
}

// Handle messages from main window (when in control window)
function handleMainWindowMessage(event) {
    if (event.data.source !== 'main') return;
    
    const { action, data } = event.data;
    
    switch (action) {
        case 'syncControls':
            syncControlsFromMain(data);
            break;
        case 'updateStarInfo':
            updateStarInfoDisplay(data);
            break;
        case 'updateSearchResults':
            updateSearchResultsDisplay(data);
            break;
        case 'updatePlanetInfo':
            updatePlanetInfoDisplay(data);
            break;
        case 'updateStatus':
            updateStatusDisplay(data);
            break;
        case 'updateDistanceMode':
            updateDistanceModeDisplay(data);
            break;
    }
}

// Handle messages from control window (when in main window)
function handleControlWindowMessage(event) {
    if (event.data.source !== 'controls') return;
    
    const { action, data } = event.data;
    
    switch (action) {
        case 'requestSync':
            syncControlsToWindow();
            break;
        case 'updateStarmap':
            updateStarmap();
            break;
        case 'searchStars':
            searchStars(data.query);
            break;
        case 'filterBySpectralType':
            filterBySpectralType();
            break;
        case 'toggleDistanceMeasurement':
            toggleDistanceMeasurement();
            break;
        case 'togglePoliticalOverlay':
            togglePoliticalOverlay();
            break;
        case 'toggleTradeRoutes':
            toggleTradeRoutes();
            break;
        case 'toggleTerritoryBorders':
            toggleTerritoryBorders();
            break;
        case 'toggleGalacticDirections':
            toggleGalacticDirections();
            break;
        case 'toggleGalacticGrid':
            toggleGalacticGrid();
            break;
        case 'updateGalacticDistance':
            updateGalacticDistance();
            break;
        case 'resetView':
            resetView();
            break;
        case 'clearHighlight':
            clearHighlight();
            break;
        case 'exportCSV':
            exportCSV();
            break;
        case 'exportImage':
            exportImage(data.format);
            break;
        case 'showNationLegend':
            showNationLegend();
            break;
        case 'toggleSystemView':
            toggleSystemView();
            break;
        case 'updateSliderValue':
            updateSliderValueInMain(data.id, data.value);
            break;
    }
}

// Control window specific functions
function setupControlEventListeners() {
    if (!isControlWindow) return;
    
    // Range slider updates
    document.getElementById('magLimit').addEventListener('input', function() {
        document.getElementById('magValue').textContent = this.value;
        sendToMainWindow('updateSliderValue', { id: 'magLimit', value: this.value });
    });
    
    document.getElementById('starCount').addEventListener('input', function() {
        document.getElementById('countValue').textContent = this.value;
        sendToMainWindow('updateSliderValue', { id: 'starCount', value: this.value });
    });
    
    document.getElementById('galacticDistance').addEventListener('input', function() {
        document.getElementById('galacticDistanceValue').textContent = this.value;
        sendToMainWindow('updateSliderValue', { id: 'galacticDistance', value: this.value });
        sendToMainWindow('updateGalacticDistance', {});
    });
    
    // Search on Enter key
    document.getElementById('starSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendToMainWindow('searchStars', { query: this.value });
        }
    });
    
    // Checkbox change events
    document.getElementById('politicalOverlay').addEventListener('change', function() {
        sendToMainWindow('togglePoliticalOverlay', { checked: this.checked });
    });
    
    document.getElementById('tradeRoutes').addEventListener('change', function() {
        sendToMainWindow('toggleTradeRoutes', { checked: this.checked });
    });
    
    document.getElementById('territoryBorders').addEventListener('change', function() {
        sendToMainWindow('toggleTerritoryBorders', { checked: this.checked });
    });
    
    document.getElementById('galacticDirections').addEventListener('change', function() {
        sendToMainWindow('toggleGalacticDirections', { checked: this.checked });
    });
    
    document.getElementById('galacticGrid').addEventListener('change', function() {
        sendToMainWindow('toggleGalacticGrid', { checked: this.checked });
    });
}

// Sync functions
function syncControlsFromMain(data) {
    if (!isControlWindow) return;
    
    // Update slider values
    if (data.magLimit) {
        document.getElementById('magLimit').value = data.magLimit;
        document.getElementById('magValue').textContent = data.magLimit;
    }
    if (data.starCount) {
        document.getElementById('starCount').value = data.starCount;
        document.getElementById('countValue').textContent = data.starCount;
    }
    if (data.galacticDistance) {
        document.getElementById('galacticDistance').value = data.galacticDistance;
        document.getElementById('galacticDistanceValue').textContent = data.galacticDistance;
    }
    
    // Update checkboxes
    if (data.politicalOverlay !== undefined) {
        document.getElementById('politicalOverlay').checked = data.politicalOverlay;
    }
    if (data.tradeRoutes !== undefined) {
        document.getElementById('tradeRoutes').checked = data.tradeRoutes;
    }
    if (data.territoryBorders !== undefined) {
        document.getElementById('territoryBorders').checked = data.territoryBorders;
    }
    if (data.galacticDirections !== undefined) {
        document.getElementById('galacticDirections').checked = data.galacticDirections;
    }
    if (data.galacticGrid !== undefined) {
        document.getElementById('galacticGrid').checked = data.galacticGrid;
    }
}

function syncControlsToWindow() {
    if (isControlWindow) return;
    
    // Get current values from main window and send to control window
    const data = {
        magLimit: document.getElementById('magLimit')?.value || 10,
        starCount: document.getElementById('starCount')?.value || 500,
        galacticDistance: document.getElementById('galacticDistance')?.value || 50,
        politicalOverlay: politicalOverlayActive,
        tradeRoutes: tradeRoutesActive,
        territoryBorders: territoryBordersActive,
        galacticDirections: galacticDirectionsActive,
        galacticGrid: galacticGridActive
    };
    
    sendToControlWindow('syncControls', data);
}

// Update display functions for control window
function updateStarInfoDisplay(data) {
    if (!isControlWindow) return;
    
    const starInfo = document.getElementById('starInfo');
    const starDetails = document.getElementById('starDetails');
    
    if (data && data.star) {
        starDetails.innerHTML = data.html;
        starInfo.style.display = 'block';
    } else {
        starInfo.style.display = 'none';
    }
}

function updateSearchResultsDisplay(data) {
    if (!isControlWindow) return;
    
    const searchResults = document.getElementById('searchResults');
    const searchResultsList = document.getElementById('searchResultsList');
    
    if (data && data.results) {
        searchResultsList.innerHTML = data.html;
        searchResults.style.display = 'block';
    } else {
        searchResults.style.display = 'none';
    }
}

function updatePlanetInfoDisplay(data) {
    if (!isControlWindow) return;
    
    const planetInfo = document.getElementById('planetInfo');
    const planetDetails = document.getElementById('planetDetails');
    const planetSystemTitle = document.getElementById('planetSystemTitle');
    
    if (data && data.planets) {
        planetDetails.innerHTML = data.html;
        planetSystemTitle.textContent = data.title || 'Planetary System';
        planetInfo.style.display = 'block';
    } else {
        planetInfo.style.display = 'none';
    }
}

function updateStatusDisplay(data) {
    if (!isControlWindow) return;
    
    const statusBar = document.getElementById('statusBar');
    if (data && data.message) {
        statusBar.innerHTML = data.message;
    }
}

function updateDistanceModeDisplay(data) {
    if (!isControlWindow) return;
    
    const distanceToggle = document.getElementById('distanceToggle');
    const distanceModeIndicator = document.getElementById('distanceModeIndicator');
    
    if (data.active) {
        distanceToggle.textContent = '📏 Stop Distance Mode';
        distanceModeIndicator.style.display = 'block';
    } else {
        distanceToggle.textContent = '📏 Start Distance Mode';
        distanceModeIndicator.style.display = 'none';
    }
}

function updateSliderValueInMain(id, value) {
    if (isControlWindow) return;
    
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
        
        // Update corresponding display elements
        if (id === 'magLimit') {
            const display = document.getElementById('magValue');
            if (display) display.textContent = value;
        } else if (id === 'starCount') {
            const display = document.getElementById('countValue');
            if (display) display.textContent = value;
        } else if (id === 'galacticDistance') {
            const display = document.getElementById('galacticDistanceValue');
            if (display) display.textContent = value;
        }
    }
}

// Control window button functions
function updateStarmap() {
    if (isControlWindow) {
        sendToMainWindow('updateStarmap', {});
    }
    // Don't call anything in main window - let starmap.js handle it
}

function searchStars(query) {
    if (isControlWindow) {
        const searchInput = document.getElementById('starSearch');
        sendToMainWindow('searchStars', { query: query || searchInput.value });
    } else {
        // Original searchStars function will be called
        window.originalSearchStars();
    }
}

function filterBySpectralType() {
    if (isControlWindow) {
        sendToMainWindow('filterBySpectralType', {});
    } else {
        // Original function will be called
        window.originalFilterBySpectralType();
    }
}

function toggleDistanceMeasurement() {
    if (isControlWindow) {
        sendToMainWindow('toggleDistanceMeasurement', {});
    } else {
        // Original function will be called
        window.originalToggleDistanceMeasurement();
    }
}

function togglePoliticalOverlay() {
    if (isControlWindow) {
        sendToMainWindow('togglePoliticalOverlay', {});
    } else {
        // Original function will be called
        window.originalTogglePoliticalOverlay();
    }
}

function toggleTradeRoutes() {
    if (isControlWindow) {
        sendToMainWindow('toggleTradeRoutes', {});
    } else {
        // Original function will be called
        window.originalToggleTradeRoutes();
    }
}

function toggleTerritoryBorders() {
    if (isControlWindow) {
        sendToMainWindow('toggleTerritoryBorders', {});
    } else {
        // Original function will be called
        window.originalToggleTerritoryBorders();
    }
}

function toggleGalacticDirections() {
    if (isControlWindow) {
        sendToMainWindow('toggleGalacticDirections', {});
    } else {
        // Original function will be called
        window.originalToggleGalacticDirections();
    }
}

function toggleGalacticGrid() {
    if (isControlWindow) {
        sendToMainWindow('toggleGalacticGrid', {});
    } else {
        // Original function will be called
        window.originalToggleGalacticGrid();
    }
}

function updateGalacticDistance() {
    if (isControlWindow) {
        sendToMainWindow('updateGalacticDistance', {});
    } else {
        // Original function will be called
        window.originalUpdateGalacticDistance();
    }
}

function resetView() {
    if (isControlWindow) {
        sendToMainWindow('resetView', {});
    } else {
        // Original function will be called
        window.originalResetView();
    }
}

function clearHighlight() {
    if (isControlWindow) {
        sendToMainWindow('clearHighlight', {});
    } else {
        // Original function will be called
        window.originalClearHighlight();
    }
}

function exportCSV() {
    if (isControlWindow) {
        sendToMainWindow('exportCSV', {});
    } else {
        // Original function will be called
        window.originalExportCSV();
    }
}

function exportImage(format) {
    if (isControlWindow) {
        sendToMainWindow('exportImage', { format });
    } else {
        // Original function will be called
        window.originalExportImage(format);
    }
}

function showNationLegend() {
    if (isControlWindow) {
        sendToMainWindow('showNationLegend', {});
    } else {
        // Original function will be called
        window.originalShowNationLegend();
    }
}

function toggleSystemView() {
    if (isControlWindow) {
        sendToMainWindow('toggleSystemView', {});
    } else {
        // Original function will be called
        window.originalToggleSystemView();
    }
}

// Main window function to open control window
function openControlWindow() {
    if (isControlWindow) return;
    
    // Calculate window position (offset from main window)
    const left = window.screenX + window.outerWidth - 620;
    const top = window.screenY + 50;
    
    const controlWindow = window.open(
        '/controls',
        'starmapControls',
        `width=600,height=800,left=${left},top=${top},scrollbars=yes,resizable=yes,location=no,menubar=no,toolbar=no,status=no`
    );
    
    if (controlWindow) {
        window.controlWindow = controlWindow;
        
        // Focus the control window
        controlWindow.focus();
        
        // Wait for control window to load, then sync
        setTimeout(function() {
            if (!controlWindow.closed) {
                syncControlsToWindow();
            }
        }, 1000);
        
        // Check if window was blocked by popup blocker
        setTimeout(function() {
            if (!controlWindow || controlWindow.closed) {
                alert('Control window was blocked by popup blocker. Please allow popups for this site and try again.');
            }
        }, 100);
    } else {
        alert('Failed to open control window. Please check your browser settings and allow popups for this site.');
    }
}

// Initialize communication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupWindowCommunication();
    
    if (!isControlWindow) {
        // Store original functions in main window BEFORE redefining them
        window.originalUpdateStarmap = window.updateStarmap;
        window.originalSearchStars = window.searchStars;
        window.originalFilterBySpectralType = window.filterBySpectralType;
        window.originalToggleDistanceMeasurement = window.toggleDistanceMeasurement;
        window.originalTogglePoliticalOverlay = window.togglePoliticalOverlay;
        window.originalToggleTradeRoutes = window.toggleTradeRoutes;
        window.originalToggleTerritoryBorders = window.toggleTerritoryBorders;
        window.originalToggleGalacticDirections = window.toggleGalacticDirections;
        window.originalToggleGalacticGrid = window.toggleGalacticGrid;
        window.originalUpdateGalacticDistance = window.updateGalacticDistance;
        window.originalResetView = window.resetView;
        window.originalClearHighlight = window.clearHighlight;
        window.originalExportCSV = window.exportCSV;
        window.originalExportImage = window.exportImage;
        window.originalShowNationLegend = window.showNationLegend;
        window.originalToggleSystemView = window.toggleSystemView;
        
        // Override functions with wrapper versions for main window
        window.updateStarmap = function() {
            if (window.originalUpdateStarmap) {
                window.originalUpdateStarmap();
            }
        };
        
        window.searchStars = function() {
            if (window.originalSearchStars) {
                window.originalSearchStars();
            }
        };
        
        window.filterBySpectralType = function() {
            if (window.originalFilterBySpectralType) {
                window.originalFilterBySpectralType();
            }
        };
        
        window.toggleDistanceMeasurement = function() {
            if (window.originalToggleDistanceMeasurement) {
                window.originalToggleDistanceMeasurement();
            }
        };
        
        window.togglePoliticalOverlay = function() {
            if (window.originalTogglePoliticalOverlay) {
                window.originalTogglePoliticalOverlay();
            }
        };
        
        window.toggleTradeRoutes = function() {
            if (window.originalToggleTradeRoutes) {
                window.originalToggleTradeRoutes();
            }
        };
        
        window.toggleTerritoryBorders = function() {
            if (window.originalToggleTerritoryBorders) {
                window.originalToggleTerritoryBorders();
            }
        };
        
        window.toggleGalacticDirections = function() {
            if (window.originalToggleGalacticDirections) {
                window.originalToggleGalacticDirections();
            }
        };
        
        window.toggleGalacticGrid = function() {
            if (window.originalToggleGalacticGrid) {
                window.originalToggleGalacticGrid();
            }
        };
        
        window.updateGalacticDistance = function() {
            if (window.originalUpdateGalacticDistance) {
                window.originalUpdateGalacticDistance();
            }
        };
        
        window.resetView = function() {
            if (window.originalResetView) {
                window.originalResetView();
            }
        };
        
        window.clearHighlight = function() {
            if (window.originalClearHighlight) {
                window.originalClearHighlight();
            }
        };
        
        window.exportCSV = function() {
            if (window.originalExportCSV) {
                window.originalExportCSV();
            }
        };
        
        window.exportImage = function(format) {
            if (window.originalExportImage) {
                window.originalExportImage(format);
            }
        };
        
        window.showNationLegend = function() {
            if (window.originalShowNationLegend) {
                window.originalShowNationLegend();
            }
        };
        
        window.toggleSystemView = function() {
            if (window.originalToggleSystemView) {
                window.originalToggleSystemView();
            }
        };
    }
});