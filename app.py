from eventlet import wsgi
import time
from datetime import datetime, timedelta
import requests
from dateutil import parser
import math
import socketio

local_sockets = "http://localhost:5500/"
link = "http://localhost:4000"
link_ip = "159.65.144.235"

sio_local = socketio.Client()


# socket connections
@sio_local.event
def connect():
    log('Local Socket Connected')


@sio_local.event
def disconnect():
    log('Local Socket connected')


def is_now_in_time_period(startTime, endTime, nowTime):
    return startTime <= nowTime <= endTime


def log(msg):
    print(f"{datetime.now().strftime('%d:%m:%Y %H:%M:%S')} — {msg}")
    return True


try:
    sio_local.connect(local_sockets)
except socketio.exceptions.ConnectionError as a:
    log(f"[offline] -> {a}")

# get db reset time
while True:
    time.sleep(10)
    try:
        reset_data = requests.get("http://localhost:9000/get/reset/details")
        if reset_data:
            details = reset_data.json()
            try:
                start = parser.parse(details['time'])
                now = datetime.now()
                offset = start + timedelta(seconds=30)
                log(details["time"])

                final_start = math.ceil(start.timestamp())
                final_now = math.ceil(now.timestamp())
                final_end = math.ceil(offset.timestamp())

                print(final_start,final_now,final_end)
                if is_now_in_time_period(final_start, final_end, final_now):
                    log("its time reset time ...")
                    try:
                        if details["active"]:
                            # online request
                            online = requests.post("http://159.65.144.235:4000/reset/ticket/counter",
                                                   json={"key_": details[
                                                       "key_"]})
                            # offline request
                            offline = requests.post("http://localhost:1000/reset/ticket/counter")
                            log("we are evaluating reset")
                            sio_local.emit("reset_status", {})
                        else:
                            log("Tickets are not set to reset")
                        continue
                    except requests.exceptions.ConnectionError:
                        log("cannot connect to the reset servers")
                else:
                    pass
            except KeyError:
                log("reset time has not been set")
        else:
            log("Application not activated.")
    except requests.exceptions.ConnectionError:
        log("cannot connect to details server")
