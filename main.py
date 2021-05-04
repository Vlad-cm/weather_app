import json
import os
import sys
import uuid
import requests
import web
from websocket import create_connection

if 'DATABASE_URL' in os.environ:
    db = web.database(dburl=os.environ['DATABASE_URL'])
else:
    with open('.dburl', 'r') as file:
        dburl = file.readline().strip()
        if len(dburl) > 0:
            db = web.database(dburl=dburl)
        else:
            print("Please set db url as DATABASE_URL enviroment variables or add to .dburl file and re-run app!")
            sys.exit()

websocket_server = "wbskt.herokuapp.com"
server_uuid = uuid.uuid5(uuid.NAMESPACE_URL, websocket_server)

urls = (
    '/get-data', 'get_data',
    '/send-data', 'send_data',
    '/get-temp', 'get_temp',
    '/(.*)', 'get_weather'
)

render = web.template.render('templates/')

api_url = "http://api.openweathermap.org/data/2.5/weather"
app = web.application(urls, globals())

params = {
    'q': 'Zhlobin',
    'appid': '55a68388e0e2edf105c6dcb94ac9d6ba',
    'units': 'metric'
}

notify_dataset = {
    "action": "weather_data",
    "data": {
        "temperature": "",
        "humidity": "",
        "heatindex": "",
        "code": "200"
    }
}


class get_data:
    def GET(self):
        data = list(db.select("room_temp", where="date > current_timestamp - interval '1' day", order="id DESC LIMIT 72"))[::-1]
        data_set = {
            "temp": [],
            "humidity": [],
            "date": []
        }
        previous_data = [data[0]["temp"], data[0]["humidity"]]
        for row in data[1:]:
            if list([row["temp"], row["humidity"]]) != previous_data:
                previous_data = list([row["temp"], row["humidity"]])
                if (row["temp"] and row["humidity"]) != None:
                    data_set.get("temp").append(str(round(row["temp"], 2)))
                    data_set.get("humidity").append(str(round(row["humidity"], 2)))
                    data_set.get("date").append(row["date"].strftime("%d, %H:%M"))
        return json.dumps(data_set, indent=4)


def get_open_weather_data(name):
    if name is not None:
        params.update({'q': name})
    return requests.get(api_url, params=params).json()


def is_float(str):
    result = False
    if str.count(".") == 1:
        if str.replace(".", "").isdigit():
            result = True
    return result


def notify_weather_data(json_data):
    ws = create_connection("wss://" + websocket_server)
    ws.send(json_data)
    ws.close()


class send_data:
    def GET(self):
        status_code = 400
        temperature, humidity, heatindex = None, None, None
        i = web.input(temp=None, humidity=None, heatindex=None, suuid=None)
        if i.suuid == str(server_uuid):
            if is_float(i.temp) or i.temp.isdigit():
                if -50.0 <= float(i.temp) <= 50.0:
                    temperature = float(i.temp)
            if is_float(i.humidity) or i.humidity.isdigit():
                if 0 <= float(i.humidity) <= 100.0:
                    humidity = float(i.humidity)
            if is_float(i.heatindex) or i.heatindex.isdigit():
                if -50.0 <= float(i.heatindex) <= 50.0:
                    heatindex = float(i.heatindex)
            if (temperature and humidity and heatindex) is not None:
                db.insert('room_temp', temp=temperature, humidity=humidity, heat_index=heatindex,
                          date=web.SQLLiteral("current_timestamp"))
                status_code = 200
        return json.dumps({"code": status_code})


class get_temp:
    def GET(self):
        i = web.input(name=None)
        data = get_open_weather_data(i.name)
        output = {
            "temp": data["main"]["temp"],
            "code": 200
        }
        return json.dumps(output, indent=4)


def get_data_from_home():
    last_row = db.select("room_temp", order="id DESC LIMIT 1")[0]
    return {"temp": last_row["temp"], "humidity": last_row["humidity"], "heat_index": last_row["heat_index"]}


def request_init(name):
    data_from_home = {'cod': 404}
    if name == "room":
        data = {'cod': 404}
        is_room = True
        data_from_home = get_data_from_home()
        notify_dataset["data"]["temperature"] = str(data_from_home["temp"])
        notify_dataset["data"]["humidity"] = str(data_from_home["humidity"])
        notify_dataset["data"]["heatindex"] = str(data_from_home["heat_index"])
        notify_weather_data(json.dumps(notify_dataset))
    else:
        data = get_open_weather_data(name)
        is_room = False
    return data, data_from_home, is_room


class get_weather:
    def GET(self, name):
        data, data_from_home, is_room = request_init(name.lower())
        return render.index(data=data, hometemp=data_from_home, is_room=is_room)

    def POST(self, name=None):
        data, data_from_home, is_room = request_init(web.input().get("name").lower())
        return render.index(data=data, hometemp=data_from_home, is_room=is_room)


if __name__ == "__main__":
    app.run()
