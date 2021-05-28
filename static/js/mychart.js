$(function(){
    $('[data-toggle="tooltip"]').tooltip();
})

let chart = document.getElementById('myChart');
let bgclr = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)',
 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'];
let brdrclr = ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)',
 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'];
let ctx, myChart;

if (chart != null)
{
    ctx = chart.getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
            {
                label: '# temperature',
                data: [],
                backgroundColor: bgclr,
                borderColor: brdrclr,
                borderWidth: 1
            },
            {
                label: '# humidity',
                data: [],
                backgroundColor: bgclr,
                borderColor: brdrclr,
                borderWidth: 1
            }
            ]},
            options: {
                scales: {
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Data for the 24h'
                    }
                }
            }
        });
}

function removeOldestData(chart, n) {
    for (var i = 0; i < n; i++) {
        chart.data.labels.shift();
        chart.data.datasets.forEach((dataset) => {
            dataset.data.shift();
        });
    }
}

function getData(checkDiff) {
    if (myChart != null)
    {
        $.getJSON("/get-data", function(response) {
            let diffed = 0
            if (checkDiff) {
                let diffTl, diffHl;
                diffTl = response["temp"].filter(x => !myChart.data.datasets[0].data.includes(x)).length;
                diffHl = response["humidity"].filter(x => !myChart.data.datasets[1].data.includes(x)).length;
                diffed = (diffTl || diffHl) > 0 ? (diffTl >= diffHl ? diffTl:diffHl):0
            }
            if (!checkDiff || diffed > 0) {
                myChart.data.labels = response["date"];
                myChart.data.datasets[0].data = response["temp"];
                myChart.data.datasets[1].data = response["humidity"];
                removeOldestData(myChart, diffed)
                myChart.update();
            }
        });
    }
}
getData();

const interval = setInterval(function() {
    getData(true)
 }, 60000);