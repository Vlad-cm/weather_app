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

function removeOldestData(chart) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    chart.update();
}

if (myChart != null)
{
    $.getJSON("/get-data", function(response) {
        for (var i = 0; i < response["temp"].length; i++) {
            myChart.data.labels.push(response["date"][i]);
            myChart.data.datasets[0].data.push(response["temp"][i]);
            myChart.data.datasets[1].data.push(response["humidity"][i]);
        };
        myChart.update();
    });
}


const interval = setInterval(function() {
    $.getJSON("/get-data", function(response) {
        let difflabels = response["date"].filter(x => !myChart.data.labels.includes(x));
        if (difflabels.length > 0) {
            let difftemp = response["temp"].filter(x => !myChart.data.labels.includes(x));
            let diffhumidity = response["humidity"].filter(x => !myChart.data.labels.includes(x));
            for (var i = 0; i < difflabels.length; i++) {
                removeOldestData(chart);
                myChart.data.labels.push(difflabels[i]);
                myChart.data.datasets[0].data.push(difftemp[i]);
                myChart.data.datasets[1].data.push(diffhumidity[i]);
            };
            myChart.update();
        }
    });
 }, 60000);