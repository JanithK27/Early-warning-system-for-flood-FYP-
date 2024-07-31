document.addEventListener('DOMContentLoaded', function () {
    const alertList = document.getElementById('alert-list');

    // Dummy data for alerts
    const alerts = [
        { message: 'Flood warning in Area A. Expected to submerge within 2 hours.', level: 'high' },
        { message: 'Flood alert in Area B. Be prepared to evacuate.', level: 'medium' },
        { message: 'Flood watch in Area C. Monitor the situation closely.', level: 'low' }
    ];

    function displayAlerts(alerts) {
        alertList.innerHTML = '';
        alerts.forEach(alert => {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.textContent = alert.message;
            alertList.appendChild(alertDiv);
        });
    }

    // Simulate fetching alerts from a server
    setTimeout(() => {
        displayAlerts(alerts);
    }, 1000);

    // Button event listeners
    document.getElementById('user-button').addEventListener('click', () => {
        alert('User button clicked');
    });

    document.getElementById('notification-button').addEventListener('click', () => {
        alert('Notification button clicked');
    });

    document.getElementById('alert-button').addEventListener('click', () => {
        alert('Alert button clicked');
    });
});
