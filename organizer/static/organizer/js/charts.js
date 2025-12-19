//// organizer/static/organizer/js/charts.js
//
//document.addEventListener('DOMContentLoaded', function() {
//    // chartData is made globally available by the template script tag
//
//    if (typeof chartData !== 'undefined' && chartData.length > 0) {
//
//        const labels = chartData.map(item => item.event__name);
//        const dataCounts = chartData.map(item => item.sales_count);
//
//        const ctx = document.getElementById('salesChart');
//
//        new Chart(ctx, {
//            type: 'doughnut',
//            data: {
//                labels: labels,
//                datasets: [{
//                    label: 'Tickets Sold',
//                    data: dataCounts,
//                    backgroundColor: [
//                        '#FF9900', // Orange
//                        '#36A2EB', // Blue
//                        '#FF6384', // Red
//                        '#4BC0C0', // Teal
//                        '#9966FF', // Purple
//                    ],
//                    hoverOffset: 4
//                }]
//            },
//            options: {
//                responsive: true,
//                maintainAspectRatio: false,
//                plugins: {
//                    legend: {
//                        labels: {
//                            color: '#a0a0a0' // Light grey legend text for dark mode
//                        }
//                    }
//                }
//            }
//        });
//    } else {
//         // You can optionally render a message if no data exists
//         const chartDiv = document.getElementById('salesChart').parentNode;
//         chartDiv.innerHTML = '<p class="text-muted text-center">No sales data yet to display.</p>';
//    }
//});

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;

    if (typeof chartData !== 'undefined' && chartData.length > 0) {
        const labels = chartData.map(item => item.event__name);
        const dataCounts = chartData.map(item => item.sales_count);

        // Helper function to get color based on current theme state
        const getTextColor = () => document.body.classList.contains('dark-mode') ? '#ffffff' : '#111111';

        const salesChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tickets Sold',
                    data: dataCounts,
                    backgroundColor: ['#FF9900', '#36A2EB', '#FF6384', '#4BC0C0', '#9966FF'],
                    hoverOffset: 4,
                    borderColor: 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getTextColor(),
                            font: { family: 'Poppins', size: 14 }
                        }
                    }
                }
            }
        });

        // --- Live Theme Update Logic ---

        const updateChartTheme = () => {
            salesChart.options.plugins.legend.labels.color = getTextColor();
            salesChart.update();
        };

        // Option A: Listen for the custom event from base.html (Best Practice)
        window.addEventListener('themeChanged', updateChartTheme);

        // Option B: Safety toggle listener (Matching your button ID "themeToggle")
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                setTimeout(updateChartTheme, 50); // Small delay to let CSS class settle
            });
        }

    } else {
         const chartDiv = ctx.parentNode;
         chartDiv.innerHTML = '<p class="text-muted text-center" style="margin-top: 50px;">No sales data yet to display.</p>';
    }
});