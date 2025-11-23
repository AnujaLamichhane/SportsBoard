// organizer/static/organizer/js/charts.js

document.addEventListener('DOMContentLoaded', function() {
    // chartData is made globally available by the template script tag

    if (typeof chartData !== 'undefined' && chartData.length > 0) {

        const labels = chartData.map(item => item.event__name);
        const dataCounts = chartData.map(item => item.sales_count);

        const ctx = document.getElementById('salesChart');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tickets Sold',
                    data: dataCounts,
                    backgroundColor: [
                        '#FF9900', // Orange
                        '#36A2EB', // Blue
                        '#FF6384', // Red
                        '#4BC0C0', // Teal
                        '#9966FF', // Purple
                    ],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0a0' // Light grey legend text for dark mode
                        }
                    }
                }
            }
        });
    } else {
         // You can optionally render a message if no data exists
         const chartDiv = document.getElementById('salesChart').parentNode;
         chartDiv.innerHTML = '<p class="text-muted text-center">No sales data yet to display.</p>';
    }
});