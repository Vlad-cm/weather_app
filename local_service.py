#! /usr/bin/python3

import sys
import time
import requests
import serial
import json

LOCAL_DEBUG = False

if sys.version == "win32":
    import win32con
    import win32gui
    if not LOCAL_DEBUG:
        hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hide, win32con.SW_HIDE)
    SERIAL = "COM3"
else:
    SERIAL = "/dev/ttyUSB0"

PREVIOUS_STATE = False

if LOCAL_DEBUG:
    url = 'http://localhost:8080'
else:
    url = 'https://vlad-weather-application.herokuapp.com'

lamp_state_api_url = f'{url}/lamp-state'

try:
    ser = serial.Serial(SERIAL, 115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        ser.readline()
        ser.write(str.encode(sys.argv[1]+'\n'))
    while True:
        try:
            answer = json.loads(requests.get(lamp_state_api_url).text)
            if answer["code"] == 200 and answer["lamp_on"] != PREVIOUS_STATE:
                PREVIOUS_STATE = answer["lamp_on"]
                if answer["lamp_on"]:
                    ser.write(str.encode("light_on" + '\n'))
                    time.sleep(0.5)
                else:
                    ser.write(str.encode("light_off" + '\n'))
                    time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(e)
        try:
            line = json.loads(ser.readline())
            if line["code"] == "200":
                if LOCAL_DEBUG:
                    print(line)
                temperature = line["temperature"]
                humidity = line["humidity"]
                heatindex = line["heatindex"]
                api_url = f'{url}/send-data?temp={temperature}&humidity={humidity}&heatindex={heatindex}'
                if LOCAL_DEBUG:
                    print(api_url)
                try:
                    requests.get(api_url)
                except requests.exceptions.RequestException as e:
                    print(e)
        except ValueError:
            pass
        time.sleep(0.5)
except Exception as e:
    print(e)
finally:
    ser.close()
