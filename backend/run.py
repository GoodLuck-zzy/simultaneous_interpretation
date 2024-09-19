import time
import pyaudio
import webrtcvad

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from collections import deque
from app.constants import Role
from app.controller import urls
from app.services.stream.stream_processor import StreamProcessor
from app.utils.util import ensure_dir


ensure_dir("logs")
ensure_dir("data")

app = Flask(__name__)
app.register_blueprint(urls.api)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
MAX_USERS = 2
client_queue = {}
vad = webrtcvad.Vad(3)
frame_duration = 20  # 可以是10, 20, 或30毫秒
bytes_per_sample = 2
SAMPLE_RATE = 8000
samples_per_frame = int(SAMPLE_RATE * frame_duration / 1000)
CHUNK = samples_per_frame * bytes_per_sample  # 每次处理的块大小
FORMAT = pyaudio.paInt16
CHANNELS = 1
SPEAK_MAX_TIME = 5
SILENT_MAX_FRAME = 20


@socketio.on("connect")
def on_connect():
    print("on_connect start")
    role = request.args.get("role")
    if len(client_queue) >= MAX_USERS:
        print("Maximum number of connections reached")
        emit("connection_response", {"status": "rejected"}, to=request.sid)
    elif request.sid in client_queue.keys():
        print(f"Client {request.sid} already connected")
        emit("connection_response", {"status": "already_connected"}, to=request.sid)
    else:
        print(f"Client {request.sid} connected with role {role}")
        client_queue[request.sid] = {}
        client_queue[request.sid]["role"] = role
        client_queue[request.sid]["voice_frames"] = deque()
        client_queue[request.sid]["audio_buffer"] = b""
        client_queue[request.sid]["is_currently_speaking"] = False
        client_queue[request.sid]["silent_frames"] = 0
        client_queue[request.sid]["last_speech_time"] = None
        if role == Role.CLIENT.value:
            client_queue[request.sid]["source_language"] = "eng"
            client_queue[request.sid]["target_language"] = "ind"
        elif role == Role.STAFF.value:
            client_queue[request.sid]["source_language"] = "ind"
            client_queue[request.sid]["target_language"] = "eng"
        emit(
            "connection_response", {"status": "accepted", "role": role}, to=request.sid
        )
        print(client_queue)


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in client_queue.keys():
        print(f"Client {request.sid} disconnected")
        del client_queue[request.sid]
        emit("disconnection_response", {"status": "accepted"}, to=request.sid)
    else:
        emit(
            "disconnection_response", {"status": "already_disconnected"}, to=request.sid
        )


@socketio.on("audio_stream")
def handle_audio_stream(data):
    info = client_queue[request.sid]
    info["audio_buffer"] += data
    while len(info["audio_buffer"]) >= CHUNK:
        data_block = info["audio_buffer"][:CHUNK]
        info["audio_buffer"] = info["audio_buffer"][CHUNK:]
        is_speech = vad.is_speech(data_block, SAMPLE_RATE)
        print(f"vad recognize is speech: {is_speech}")
        if is_speech:
            now = time.time()
            if not info["is_currently_speaking"]:
                print("start speaking...")
                info["is_currently_speaking"] = True
                info["silent_frames"] = 0
                info["last_speech_time"] = now
            info["voice_frames"].append(data_block)
            print("save voice frames")
            if now - info["last_speech_time"] > SPEAK_MAX_TIME:
                print(f"More than {SPEAK_MAX_TIME}s voice, process.")
                StreamProcessor.process_accumulated_voice_frames(
                    CHANNELS, SAMPLE_RATE, FORMAT, info
                )
        else:
            if info["is_currently_speaking"] and info["voice_frames"]:
                info["silent_frames"] += 1
                print("save silent frames")
                if info["silent_frames"] >= SILENT_MAX_FRAME:
                    print(f"More than {SILENT_MAX_FRAME} silent frames, process.")
                    StreamProcessor.process_accumulated_voice_frames(
                        CHANNELS, SAMPLE_RATE, FORMAT, info
                    )


if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host="0.0.0.0")
