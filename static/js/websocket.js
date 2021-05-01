let temperature = document.querySelector("#temperature"),
    humidity = document.querySelector("#humidity"),
    heatindex = document.querySelector("#heatindex"),
    lampswitch = document.querySelector("#lampswitch"),
    usersonline = document.querySelector("#online"),
    websocket = new WebSocket("wss://wbskt.herokuapp.com/");
lampswitch.onclick = function(event) {
    let state = false;
    if (lampswitch.checked) {
        state = true
    }
    websocket.send(JSON.stringify({ action: 'lampstate', lamp_on: state }));
}
websocket.onmessage = function(event) {
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
        case 'lampstate':
            lampswitch.checked = data.lamp_on;
            break;
        case 'users':
            usersonline.textContent = data.count;
            break;
        default:
            console.error(
                "unsupported event", data);
    }
};