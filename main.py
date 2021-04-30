import json
import os
import sys

import web
import requests
import statistics

if 'DATABASE_URL' in os.environ:
    db = web.database(dburl=os.environ['DATABASE_URL'])
else:
    with open('.dburl', 'r') as file:
        dburl = file.readline()
        if len(dburl) > 0:
            db = web.database(dburl=dburl)
        else:
            print("Please set db url as DATABASE_URL enviroment variables or add to .dburl file and re-run app!")
            sys.exit()

temp_lst = []
humidity_lst = []
heat_index_lst = []

urls = (
    '/get-data', 'get_data',
    '/lamp-state', 'lamp_state',
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


def get_lamp_state():
    return str(db.select("lamp_state", order="id DESC LIMIT 1")[0]["state"]).strip() == "on"


def get_data_from_db():
    data = db.select("room_temp", where="date > current_date - interval '1' day")
    data_set = {"temp": [],
                "humidity": [],
                "heat_index": [],
                "date": []
                }
    temp, humidity, heat_index, date = [], [], [], []
    for row in data:
        if row["temp"] != None:
            temp.append(float(row["temp"]))
        else:
            temp.append(0)
        if row["humidity"] != None:
            humidity.append(float(row["humidity"]))
        else:
            humidity.append(0)
        if row["heat_index"] != None:
            heat_index.append(float(row["heat_index"]))
        else:
            heat_index.append(0)
        date.append(row["date"])
    j = 0
    for i in range(int(len(temp)/10)):
        if j + 10 <= len(temp):
            data_set.get("temp").append(round(statistics.mean(temp[j:j+10]), 2))
            data_set.get("humidity").append(round(statistics.mean(humidity[j:j+10]), 2))
            data_set.get("heat_index").append(round(statistics.mean(heat_index[j:j+10]), 2))
            data_set.get("date").append((date[j] + (date[j + 9] - date[j]) / 10).strftime("%b %d %H:%M"))
            j += 10
    return json.dumps(data_set, indent=4)


class get_data:
    def GET(self):
        return get_data_from_db()


class lamp_state:
    def GET(self):
        output = {
            "lamp_on": get_lamp_state(),
            "code": 200
        }
        return json.dumps(output, indent=4)

    def POST(self):
        db.insert('lamp_state', state=str(web.input().get("lampswitch")).strip(),
                  date=web.SQLLiteral("current_timestamp"))
        raise web.seeother('/' + str(web.input().get("cityname")).strip())


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


class send_data:
    def GET(self):
        i = web.input(temp=None, humidity=None, heatindex=None)
        if is_float(i.temp) or i.temp.isdigit():
            if -50.0 <= float(i.temp) <= 50.0:
                temp_lst.append(float(i.temp))
        if is_float(i.humidity) or i.humidity.isdigit():
            if 0 <= float(i.humidity) <= 100.0:
                humidity_lst.append(float(i.humidity))
        if is_float(i.heatindex) or i.heatindex.isdigit():
            if -50.0 <= float(i.heatindex) <= 50.0:
                heat_index_lst.append(float(i.heatindex))
        if (len(temp_lst) or len(humidity_lst) or len(heat_index_lst)) >= 100:
            db.insert('room_temp', temp=round(statistics.mean(temp_lst), 2),
                      humidity=round(statistics.mean(humidity_lst), 2),
                      heat_index=round(statistics.mean(heat_index_lst), 2),
                      date=web.SQLLiteral("current_timestamp"))
            temp_lst.clear()
            humidity_lst.clear()
            heat_index_lst.clear()
        return {"code": 200}


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
    else:
        data = get_open_weather_data(name)
        is_room = False
    return data, data_from_home, is_room


class get_weather:
    def GET(self, name):
        data, data_from_home, is_room = request_init(name.lower())
        return render.index(data=data, hometemp=data_from_home, is_room=is_room, lamp_state=get_lamp_state())

    def POST(self, name=None):
        data, data_from_home, is_room = request_init(web.input().get("name").lower())
        return render.index(data=data, hometemp=data_from_home, is_room=is_room, lamp_state=get_lamp_state())


if __name__ == "__main__":
    app.run()
