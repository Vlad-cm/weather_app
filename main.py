import web
import requests
import statistics

db = web.database(
    dburl="postgres://eqroiidmlipflp:505f497547db185a4824a73f51eba0f00801b146849d6676898be869c4909ebf@ec2-34-252-251-16.eu-west-1.compute.amazonaws.com:5432/d6lc3m0qdp3q1")

temp_lst = []
bright_lst = []

urls = (
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


class lamp_state:
    def GET(self):
        return get_lamp_state()

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
        i = web.input(temp=None, bright=None)
        if is_float(i.temp) or i.temp.isdigit():
            if -50.0 <= float(i.temp) <= 50.0:
                temp_lst.append(float(i.temp))
        if i.bright.isdigit():
            if 0 <= int(i.bright) <= 255:
                bright_lst.append(int(i.bright))
        if (len(temp_lst) or len(bright_lst)) >= 100:
            db.insert('room_temp', temp=round(statistics.mean(temp_lst), 2), bright=int(statistics.mean(bright_lst)),
                      date=web.SQLLiteral("current_timestamp"))
            temp_lst.clear()
            bright_lst.clear()
        return {'cod': 200}


class get_temp:
    def GET(self):
        i = web.input(name=None)
        data = get_open_weather_data(i.name)
        return "{\"temp\":" + str(data["main"]["temp"]) + ", \"cod\": 200}"


def get_data_from_home():
    last_row = db.select("room_temp", order="id DESC LIMIT 1")[0]
    return {"temp": last_row["temp"], "bright": last_row["bright"]}


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
