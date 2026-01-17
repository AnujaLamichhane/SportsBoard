
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        // Remove active class from all items
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        
        // Add active class to the clicked item
        this.classList.add('active');
    });
});


function toggleSidebar() {
            const sidebar = document.getElementById('geminiSidebar');
            const mainContent = document.querySelector('.main-content');
            // This toggles the class we defined in CSS
            sidebar.classList.toggle('sidebar-collapsed');
            if (mainContent) {
                mainContent.classList.toggle('sidebar-collapsed');
            
        }
        }
        const chartData = JSON.parse('{{ sales_data_json|safe }}');