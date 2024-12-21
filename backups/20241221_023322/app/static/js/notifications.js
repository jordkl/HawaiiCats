// Notification system
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;

    // Set notification type class
    notification.className = 'notification';
    notification.classList.add(`notification-${type}`);

    // Set message
    notification.textContent = message;

    // Show notification
    notification.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
