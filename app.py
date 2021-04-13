from eventlet import wsgi
import time
from datetime import datetime, timedelta
import requests
from dateutil import parser

link = "http://localhost:4000"
link_ip = "159.65.144.235"


def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        # nowTime >= startTime and nowTime <= endTime
        return startTime <= nowTime <= endTime
    else:
        return nowTime >= startTime or nowTime <= endTime


def log(msg):
    print(f"{datetime.now().strftime('%d:%m:%Y %H:%M:%S')} — {msg}")
    return True


# get db reset time
while True:
    time.sleep(10)
    try:
        reset_data = requests.get("http://localhost:9000/get/reset/details")
        if reset_data:
            details = reset_data.json()
            try:

                timeStart = parser.parse(details['time'])
                timeEnd = timeStart + timedelta(minutes=1)

                timeEnd = timeEnd.strftime("%I:%M%p")
                timeStart = timeStart.strftime("%I:%M%p")

                timeNow = datetime.now().strftime("%I:%M%p")
                print(timeStart, timeEnd, timeNow)
                if isNowInTimePeriod(timeStart, timeEnd, timeNow):
                    try:
                        if details["active"]:
                            # online request
                            online = requests.post("http://159.65.144.235:4000/reset/ticket/counter",
                                                   json={"key_": details[
                                                       "key_"]})
                            # offline request
                            offline = requests.post("http://localhost:1000/reset/ticket/counter")
                            log("we are eveluatiing reset")
                        else:
                            log("Tickets are not set to reset")
                        continue
                    except requests.exceptions.ConnectionError:
                        log("cannot connect to the reset servers")
                else:
                    log("its not time to reset yet!")
            except KeyError:
                log("reset time has not been set")
        else:
            log("Application not activated.")
    except requests.exceptions.ConnectionError:
        log("cannot connect to details server")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True, port=9999)
    eventlet.wsgi.server(eventlet.listen(('', 9999)), app)
