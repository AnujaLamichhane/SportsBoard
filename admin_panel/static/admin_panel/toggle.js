// admin_panel/js/toggle.js

// 1. ATTACH TO WINDOW IMMEDIATELY
window.toggleSidebar = function() {
    const sidebar = document.getElementById('adminSidebar');
    const wrapper = document.getElementById('adminWrapper');

    if (sidebar && wrapper) {
        sidebar.classList.toggle('sidebar-collapsed');
        wrapper.classList.toggle('collapsed');

        // Save state to localStorage
        const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
        localStorage.setItem('adminSidebarState', isCollapsed ? 'collapsed' : 'expanded');
        console.log("Toggle Clicked! State is now:", isCollapsed ? "Collapsed" : "Expanded");
    } else {
        console.error("Sidebar or Wrapper ID missing from DOM.");
    }
};

// 2. RUN RESTORATION ON LOAD
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('adminSidebar');
    const wrapper = document.getElementById('adminWrapper');
    const savedState = localStorage.getItem('adminSidebarState');

    if (savedState === 'collapsed' && sidebar && wrapper) {
        sidebar.classList.add('sidebar-collapsed');
        wrapper.classList.add('collapsed');
    }

    // Active Link Logic
    const navLinks = document.querySelectorAll('.dnav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});