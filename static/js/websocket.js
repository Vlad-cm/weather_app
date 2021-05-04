let temperature = document.querySelector("#temperature"),
    humidity = document.querySelector("#humidity"),
    heatindex = document.querySelector("#heatindex"),
    lampswitch = document.querySelector("#lampswitch"),
    usersonline = document.querySelector("#online"),
    url = "wss://wbskt.herokuapp.com/",
    ws;

lampswitch.onclick = function(event) {
    let state = false;
    if (lampswitch.checked) {
        state = true
    }
    ws.send(JSON.stringify({ action: 'lampstate', lamp_on: state }));
};

function connect() {
  ws = new WebSocket(url);
  ws.onmessage = function(event) {
    data = JSON.parse(event.data);
    switch (data.type) {
        case 'weather_data':
            if (temperature != null)
               temperature.textContent = "Temperature: " + data.data.temperature + " ℃";
            if (humidity != null)
               humidity.textContent = "Humidity: " + data.data.humidity + " %";
            if (heatindex != null)
               heatindex.textContent = "Heat index (feel like): " + data.data.heatindex + " ℃";
            break;
        case 'weather_data_avg':
           if (myChart != null)
            {
                let today = new Date();
                myChart.data.labels.push(('0' + today.getUTCDate()).slice(-2) + ", " + ('0' + today.getUTCHours()).slice(-2) + ":" + ('0' + today.getUTCMinutes()).slice(-2));
                myChart.data.datasets[0].data.push(data.data.temperature);
                myChart.data.datasets[1].data.push(data.data.humidity);
                if (myChart.data.labels.length > 48) {
                    removeOldestData(myChart, 1);
                } else {
                    myChart.update();
                }
            }
            break;
        case 'lampstate':
            lampswitch.checked = data.lamp_on;
            break;
        case 'users':
            usersonline.textContent = data.count;
            break;
        default:
            console.error("unsupported event", data);
        }
  };

  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function() {
      connect();
    }, 1000);
  };

  ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
}

connect();