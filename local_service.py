import sys

import requests
import serial
import win32con
import win32gui

LOCAL_DEBUG = True

PREVIOUS_STATE = "None"

if LOCAL_DEBUG:
    url = 'http://localhost:8080'
else:
    url = 'https://vlad-weather-application.herokuapp.com'

if not LOCAL_DEBUG:
    hide = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hide, win32con.SW_HIDE)

try:
    ser = serial.Serial('COM3', 115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        ser.readline()
        ser.write(str.encode(sys.argv[1]+'\n'))

    while True:
        content = ""
        api_url = f'{url}/lamp-state'
        try:
            content = requests.get(api_url)
        except requests.exceptions.RequestException as e:
            print(e)

        if content.text.strip() != PREVIOUS_STATE:
            PREVIOUS_STATE = content.text.strip()
            if content.text.strip() == "True":
                ser.write(str.encode("light_on" + '\n'))
            else:
                ser.write(str.encode("light_off" + '\n'))

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
