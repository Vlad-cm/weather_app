#!/usr/bin/env python3

import sys
import uuid
import time
import serial
import json
import websocket
try:
    import thread
except ImportError:
    import _thread as thread

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

if LOCAL_DEBUG:
    url = 'http://localhost:8080'
else:
    url = 'https://vlad-weather-application.herokuapp.com'

websocket_server = "wbskt.herokuapp.com"
server_uuid = uuid.uuid5(uuid.NAMESPACE_URL, websocket_server)

LAMPSTATE = False
PREVIOUS_STATE = True

notify_dataset = {
    "action": "weather_data",
    "data": {
        "temperature": "",
        "humidity": "",
        "heatindex": "",
        "code": "200"
    }
}

def serial_worker(ws):
    global PREVIOUS_STATE
    try:
        ser = serial.Serial(SERIAL, 115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            ser.readline()
            ser.write(str.encode(sys.argv[1] + '\n'))
        while True:
            if LAMPSTATE != PREVIOUS_STATE:
                PREVIOUS_STATE = LAMPSTATE
                if LAMPSTATE:
                    ser.write(str.encode("light_on" + '\n'))
                    if LOCAL_DEBUG:
                        print("Sent a message to the controller: ", "light_on" )
                    time.sleep(0.5)
                else:
                    ser.write(str.encode("light_off" + '\n'))
                    if LOCAL_DEBUG:
                        print("Sent a message to the controller: ","light_off" )
                    time.sleep(0.5)
            try:
                line = json.loads(ser.readline())
                if line["data"]["code"] == "200":
                    if LOCAL_DEBUG:
                        print("Received a message from the controller: \n", line)
                    notify_dataset["action"] = line["action"]
                    notify_dataset["data"]["temperature"] = str(line["data"]["temperature"])
                    notify_dataset["data"]["humidity"] = str(line["data"]["humidity"])
                    notify_dataset["data"]["heatindex"] = str(line["data"]["heatindex"])
                    ws.send(json.dumps(notify_dataset))
                    if LOCAL_DEBUG:
                        print("Sent a message to the websocket server: \n", json.dumps(notify_dataset))
            except ValueError:
                pass
    except Exception as e:
        print(e)
    finally:
        ser.close()


def on_message(ws, message):
    global LAMPSTATE
    data = json.loads(message)
    if data["type"] == "lampstate":
        LAMPSTATE = data["lamp_on"]
        if LOCAL_DEBUG:
            print("LAMPSTATE: ", LAMPSTATE)

def on_open(ws):
    def run(*args):
        serial_worker(ws)
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    ws = websocket.WebSocketApp(f"wss://{websocket_server}", on_open=on_open, on_message=on_message)
    ws.run_forever()
