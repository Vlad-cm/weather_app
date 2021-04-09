import sys
import time

import serial
import requests

LOCAL_DEBUG = False

if LOCAL_DEBUG:
    url = 'http://localhost:8080'
else:
    url = 'https://vlad-weather-application.herokuapp.com'

try:
    ser = serial.Serial('COM3', 115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        ser.readline()
        ser.write(str.encode(sys.argv[1]+'\n'))

    while True:
        line = ser.readline()
        if line != b'' and line != b'\r\n':
            if LOCAL_DEBUG:
                print(line)
            line = str(line)[2:-5].split()
            temp = line[0].split(':')[1]
            bright = line[1].split(':')[1]
            api_url = f'{url}/send-data?temp={temp}&bright={bright}'
            if LOCAL_DEBUG:
                print(api_url)
            try:
                requests.get(api_url)
            except requests.exceptions.RequestException as e:
                print(e)
except Exception as e:
    print(e)
finally:
    ser.close()
