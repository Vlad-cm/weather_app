import web
import requests

urls = (
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


class get_temp:
    def GET(self):
        i = web.input(name=None)
        data = get_open_weather_data(i.name)
        return data["main"]["temp"]


class get_weather:
    def GET(self, name):
        return render.index(get_open_weather_data(name))


if __name__ == "__main__":
    app.run()
