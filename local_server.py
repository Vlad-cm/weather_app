import serial
import requests

LOCAL_DEBUG = False

local_url = 'http://localhost:8080'
remote_url = 'https://vlad-weather-application.herokuapp.com'
url = ''

try:
    ser = serial.Serial('COM3', 115200, timeout=0)
    while True:
        line = ser.readline()
        if line != b'' and line != b'\r\n':
            line = str(line)[2:-1].split()
            temp=line[0].split(':')[1]
            bright = line[1].split(':')[1]
            if LOCAL_DEBUG:
                url = local_url
            else:
                url = remote_url
            api_url = f'{url}/send-data?temp={temp}&bright={bright}'
            try:
                requests.get(api_url)
            except requests.exceptions.RequestException as e:
                print(e)
except:
    pass
finally:
    ser.close()
