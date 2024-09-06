import os
from flask import Flask
from app.controller import urls

# from flask_socketio import SocketIO


app = Flask(__name__)


# socketio = SocketIO(app, cors_allowed_origins="*")
# @socketio.on("client")
# def handle_my_custom_event(data):
#     print(f"received data {len(data)} length")
#     socketio.emit("server", data)
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)



ensure_dir("logs")
ensure_dir("data")

if __name__ == "__main__":
    app.run(port=15000, host="0.0.0.0", debug=True)
