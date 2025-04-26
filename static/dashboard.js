document.addEventListener("DOMContentLoaded", function () {
    // Total Spend per Week
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

    // Top 10 Departments
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

    // Active Households per Week
    fetch("/api/active_households")
        .then(res => res.json())
        .then(data => {
            const weeks = data.map(row => `W${row.WEEK_NUM} ${row.YEAR}`);
            const households = data.map(row => row.active_households);

            Plotly.newPlot('active-households-chart', [{
                x: weeks,
                y: households,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: 'green' }
            }], {
                title: 'Active Households by Week',
                xaxis: { title: 'Week' },
                yaxis: { title: '# of Households' }
            });
        });

    // Avg Spend per Household per Week
    fetch("/api/avg_spend_per_household")
        .then(res => res.json())
        .then(data => {
            const weeks = data.map(row => `W${row.WEEK_NUM} ${row.YEAR}`);
            const avgSpend = data.map(row => row.avg_spend);

            Plotly.newPlot('avg-spend-chart', [{
                x: weeks,
                y: avgSpend,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: 'purple' }
            }], {
                title: 'Average Spend Per Household by Week',
                xaxis: { title: 'Week' },
                yaxis: { title: 'Avg Spend ($)' }
            });
        });
});
