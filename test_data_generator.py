#! /usr/bin/python3

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
        humidity = round((43 + random.random()), 2)
        heat_index = round((23 + random.random()), 2)
        api_url = f'{url}/send-data?temp={temp}&humidity={humidity}&heatindex={heat_index}'
        print(api_url)
        try:
            requests.get(api_url)
        except requests.exceptions.RequestException as e:
            print(e)
        time.sleep(0.1)