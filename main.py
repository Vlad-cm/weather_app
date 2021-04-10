import web
import requests

data_from_home = {
    'temp': 0,
    'bright': 0
}

urls = (
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
                data_from_home.update({'temp': i.temp})
        if i.bright.isdigit():
            if 0 <= int(i.bright) <= 255:
                data_from_home.update({'bright': i.bright})
        return data_from_home


class get_temp:
    def GET(self):
        i = web.input(name=None)
        data = get_open_weather_data(i.name)
        return data["main"]["temp"]


class get_weather:
    def GET(self, name):
        if name.lower() == "room":
            return render.index(data={'cod': 404}, hometemp=data_from_home, is_room=True)
        else:
            return render.index(data=get_open_weather_data(name), hometemp=data_from_home, is_room=False)

    def POST(self, name=None):
        if web.input().get("name").lower() == "room":
            return render.index(data={'cod': 404}, hometemp=data_from_home, is_room=True)
        else:
            return render.index(data=get_open_weather_data(web.input().get("name")), hometemp=data_from_home,
                                is_room=False)


if __name__ == "__main__":
    app.run()
