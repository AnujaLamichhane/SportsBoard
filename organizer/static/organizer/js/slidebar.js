function toggleSidebar() {
    const sidebar = document.getElementById('geminiSidebar');
    // Find the parent container (the <aside> tag)
    const container = document.querySelector('.sidebar-container');
    
    if (sidebar && container) {
        sidebar.classList.toggle('sidebar-collapsed');
        container.classList.toggle('collapsed-parent');
        
        // Save state so it stays collapsed on refresh
        const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebarStatus', isCollapsed ? 'collapsed' : 'expanded');
    } else {
        console.error("Sidebar elements not found. Check your IDs and Classes.");
    }
}