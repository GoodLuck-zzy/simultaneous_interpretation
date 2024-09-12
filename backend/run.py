import os
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from app.controller import urls


app = Flask(__name__)
CORS(app)
app.register_blueprint(urls.api)
socketio = SocketIO(app, cors_allowed_origins="*")
users = {}
max_users = 2


@socketio.on("connect")
def on_connect():
    role = request.args.get("role")
    if len(users) >= max_users:
        print("Maximum number of connections reached")
        emit("connection_response", {"status": "rejected"}, to=request.sid)
    elif request.sid in users:
        print(f"Client {request.sid} already connected")
        emit("connection_response", {"status": "already_connected"}, to=request.sid)
    else:
        print(f"Client {request.sid} connected with role {role}")
        users[request.sid] = role
        emit(
            "connection_response", {"status": "accepted", "role": role}, to=request.sid
        )


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in users:
        print(f"Client {request.sid} disconnected")
        del users[request.sid]


@socketio.on("audio_stream")
def handle_audio_stream(data):
    emit("audio_stream", data, broadcast=True, include_self=False)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


ensure_dir("logs")
ensure_dir("data")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
