// Add this inside your script tag for the sportChart
const gradient = ctx.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, '#ff8900');
gradient.addColorStop(1, '#ffc107');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {{ labels|safe }},
        datasets: [{
            label: 'Events',
            data: {{ values|safe }},
            backgroundColor: gradient, // Use gradient here
            borderRadius: 10,
            hoverBackgroundColor: '#e67a00'
        }]
    },
    options: {
        plugins: {
            legend: { display: false }
        },
        scales: {
            y: { beginAtZero: true, grid: { display: false } },
            x: { grid: { display: false } }
        }
    }
});