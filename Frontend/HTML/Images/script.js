// Dummy data for flood alerts
const alerts = [
    "Flood warning in area 1. Expected in 2 hours.",
    "River level rising in area 2. Possible flood in 3 hours.",
    "Heavy rainfall in area 3. Stay alert for updates."
];

// Function to initialize map
function initMap() {
    const map = document.getElementById('map');
    map.innerHTML = "<p>Interactive Map Here</p>"; // Placeholder content
    // Add map integration code here (e.g., using Leaflet or Google Maps API)
}

// Function to display alerts
function displayAlerts() {
    const alertList = document.getElementById('alerts');
    alerts.forEach(alert => {
        const li = document.createElement('li');
        li.textContent = alert;
        alertList.appendChild(li);
    });
}

// Initialize map and alerts on page load
window.onload = function() {
    initMap();
    displayAlerts();
};
