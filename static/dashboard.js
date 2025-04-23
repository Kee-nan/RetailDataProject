document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/spending_over_time")
        .then(res => res.json())
        .then(data => {
            const weeks = data.map(row => `W${row.WEEK_NUM} ${row.YEAR}`);
            const spend = data.map(row => row.total_spend);

            Plotly.newPlot('spend-chart', [{
                x: weeks,
                y: spend,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: 'blue' }
            }], {
                title: 'Total Spend by Week',
                xaxis: { title: 'Week' },
                yaxis: { title: 'Spend ($)' }
            });
        });

    fetch("/api/top_departments")
        .then(res => res.json())
        .then(data => {
            const departments = data.map(row => row.DEPARTMENT);
            const spend = data.map(row => row.total_spend);

            Plotly.newPlot('departments-chart', [{
                x: departments,
                y: spend,
                type: 'bar',
                marker: { color: 'orange' }
            }], {
                title: 'Top Departments by Spend',
                xaxis: { title: 'Department' },
                yaxis: { title: 'Spend ($)' }
            });
        });
});
