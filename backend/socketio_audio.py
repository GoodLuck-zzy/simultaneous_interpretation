from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # 导入flask-cors模块

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

users = []


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    print("Client connected")
    users.append(request.sid)
    print(users)
    print("----------------")


@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")
    users.remove(request.sid)
    print(users)
    print("----------------")


@socketio.on("audio_stream")
def handle_audio_stream(data):
    emit("audio_stream", data, broadcast=True, include_self=False)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
