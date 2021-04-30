$(document).ready(function() {
    $.getJSON("/get-data", function(response) {
        let temperature = response['temp'];
        let humidity = response['humidity'];
        let heat_index = response['heat_index'];
        let date = response['date'];
        let bgclr = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'
        ];
        let brdrclr = ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'
        ];
        var ctx = document.getElementById('myChart').getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: date,
                datasets: [{
                        label: '# temperature',
                        data: temperature,
                        backgroundColor: bgclr,
                        borderColor: brdrclr,
                        borderWidth: 1
                    },
                    {
                        label: '# humidity',
                        data: humidity,
                        backgroundColor: bgclr,
                        borderColor: brdrclr,
                        borderWidth: 1
                    },
                    {
                        label: '# heat index',
                        data: heat_index,
                        backgroundColor: bgclr,
                        borderColor: brdrclr,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Data for the day'
                    }
                }
            }
        });

    });
})