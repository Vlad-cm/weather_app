import time
import random
import requests

LOCAL_DEBUG = False

if LOCAL_DEBUG:
    url = 'http://localhost:8080'
else:
    url = 'https://vlad-weather-application.herokuapp.com'

random.seed(version=2)

while True:
        temp = round((24 + random.random()), 2)
        bright = random.randint(100, 255)
        api_url = f'{url}/send-data?temp={temp}&bright={bright}'
        print(api_url)
        try:
            requests.get(api_url)
        except requests.exceptions.RequestException as e:
            print(e)
        time.sleep(0.1)