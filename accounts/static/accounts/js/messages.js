// static/accounts/js/messages.js

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // 1. Determine the timing: 2 seconds for warnings/errors, 5 for others
        let displayTime = 5000; 
        if (alert.classList.contains('alert-warning') || alert.classList.contains('alert-danger')) {
            displayTime = 2000; // Fast-track warning messages
        }

        // 2. Schedule the fade out for this specific alert
        setTimeout(function() {
            // Smooth transition effects
            alert.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)"; 
            
            // 3. Remove from DOM after transition completes
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 600);
        }, displayTime);
    });
});