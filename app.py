import eventlet.wsgi
from flask import jsonify,Flask
import socketio
import random

link = "http://localhost:4000"
link_ip = "159.65.144.235"

# standard Python
sio = socketio.Client()

app = Flask(__name__)

@app.route("/ticket/reset",methods=["POST"])
def reset():
    code = {"code":random.getrandbits()}
    sio.emit("reset_tickets",code)
    return jsonify(code)

@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


try:
    sio.connect("http://localhost:5000/")
except socketio.exceptions.ConnectionError:
    print("Error! Could not connect to the socket server.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=4000)
    # eventlet.wsgi.server(eventlet.listen(('', 4000)), app)
