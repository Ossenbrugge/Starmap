// Star Data Window JavaScript
// This handles communication between the star data window and main starmap window

let mainWindow = null;
let isStarDataWindow = window.location.pathname.includes('/stardata');

// Connection management
function setupStarDataCommunication() {
    if (isStarDataWindow) {
        // This is the star data window
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
        
        // Initial sync request
        sendToMainWindow('requestStarDataSync', {});
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
        mainWindow.postMessage({ action, data, source: 'stardata' }, '*');
    }
}

// Handle messages from main window (when in star data window)
function handleMainWindowMessage(event) {
    if (event.data.source !== 'main') return;
    
    const { action, data } = event.data;
    
    switch (action) {
        case 'updateStarInfo':
            updateStarInfoDisplay(data);
            break;
        case 'updateSearchResults':
            updateSearchResultsDisplay(data);
            break;
        case 'updatePlanetInfo':
            updatePlanetInfoDisplay(data);
            break;
        case 'updateDistanceResults':
            updateDistanceResultsDisplay(data);
            break;
        case 'clearStarData':
            clearAllDataDisplays();
            break;
    }
}

// Update display functions for star data window
function updateStarInfoDisplay(data) {
    if (!isStarDataWindow) return;
    
    const starInfo = document.getElementById('starInfo');
    const starDetails = document.getElementById('starDetails');
    const noDataMessage = document.getElementById('noDataMessage');
    const focusButton = document.getElementById('focusButton');
    
    if (data && data.star) {
        starDetails.innerHTML = data.html;
        starInfo.style.display = 'block';
        noDataMessage.style.display = 'none';
        focusButton.disabled = false;
        
        // Store star data for focus function
        window.currentStarData = data.star;
    } else {
        starInfo.style.display = 'none';
        noDataMessage.style.display = 'block';
        focusButton.disabled = true;
        window.currentStarData = null;
    }
}

function updateSearchResultsDisplay(data) {
    if (!isStarDataWindow) return;
    
    const searchResults = document.getElementById('searchResults');
    const searchResultsList = document.getElementById('searchResultsList');
    const noDataMessage = document.getElementById('noDataMessage');
    
    if (data && data.results && data.results.length > 0) {
        searchResultsList.innerHTML = data.html;
        searchResults.style.display = 'block';
        noDataMessage.style.display = 'none';
    } else {
        searchResults.style.display = 'none';
        if (!document.getElementById('starInfo').style.display || document.getElementById('starInfo').style.display === 'none') {
            noDataMessage.style.display = 'block';
        }
    }
}

function updatePlanetInfoDisplay(data) {
    if (!isStarDataWindow) return;
    
    const planetInfo = document.getElementById('planetInfo');
    const planetDetails = document.getElementById('planetDetails');
    const planetSystemTitle = document.getElementById('planetSystemTitle');
    const noDataMessage = document.getElementById('noDataMessage');
    
    if (data && data.planets) {
        planetDetails.innerHTML = data.html;
        planetSystemTitle.textContent = data.title || 'Planetary System';
        planetInfo.style.display = 'block';
        noDataMessage.style.display = 'none';
    } else {
        planetInfo.style.display = 'none';
        if (!document.getElementById('starInfo').style.display || document.getElementById('starInfo').style.display === 'none') {
            noDataMessage.style.display = 'block';
        }
    }
}

function updateDistanceResultsDisplay(data) {
    if (!isStarDataWindow) return;
    
    const distanceResults = document.getElementById('distanceResults');
    const distanceDetails = document.getElementById('distanceDetails');
    const noDataMessage = document.getElementById('noDataMessage');
    
    if (data && data.measurement) {
        distanceDetails.innerHTML = data.html;
        distanceResults.style.display = 'block';
        noDataMessage.style.display = 'none';
    } else {
        distanceResults.style.display = 'none';
        if (!document.getElementById('starInfo').style.display || document.getElementById('starInfo').style.display === 'none') {
            noDataMessage.style.display = 'block';
        }
    }
}

function clearAllDataDisplays() {
    if (!isStarDataWindow) return;
    
    document.getElementById('starInfo').style.display = 'none';
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('planetInfo').style.display = 'none';
    document.getElementById('distanceResults').style.display = 'none';
    document.getElementById('noDataMessage').style.display = 'block';
    document.getElementById('focusButton').disabled = true;
    window.currentStarData = null;
}

// Star data window action functions
function focusOnStar() {
    if (isStarDataWindow && window.currentStarData) {
        sendToMainWindow('focusOnStar', { star: window.currentStarData });
    }
}

function clearSelection() {
    if (isStarDataWindow) {
        sendToMainWindow('clearHighlight', {});
        clearAllDataDisplays();
    }
}

function toggleSystemView() {
    if (isStarDataWindow) {
        sendToMainWindow('toggleSystemView', {});
    }
}

// Initialize communication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (isStarDataWindow) {
        setupStarDataCommunication();
    }
});