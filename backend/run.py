import time
import pyaudio
import webrtcvad
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from collections import deque
from app.constants import Role
from app.controller import urls
from app.services.stream.stream_processor import StreamProcessor
from app.utils.util import ensure_dir

logger = logging.getLogger(__name__)

ensure_dir("logs")
ensure_dir("data")

app = Flask(__name__)
app.register_blueprint(urls.api)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
MAX_USERS = 2
client_queue = {}
vad = webrtcvad.Vad(1)
frame_duration = 20  # 可以是10, 20, 或30毫秒
bytes_per_sample = 2
SAMPLE_RATE = 8000
samples_per_frame = int(SAMPLE_RATE * frame_duration / 1000)
CHUNK = samples_per_frame * bytes_per_sample  # 每次处理的块大小
FORMAT = pyaudio.paInt16
CHANNELS = 1
SPEAK_MAX_TIME = 5
SILENT_MAX_FRAME = 30


@socketio.on("connect")
def on_connect():
    role = request.args.get("role")
    origin_silent = request.args.get("origin_silent")
    if len(client_queue) >= MAX_USERS:
        logger.warning("Maximum number of connections reached")
        emit("connection_response", {"status": "rejected"}, to=request.sid)
    elif request.sid in client_queue.keys():
        logger.warning(f"Client {request.sid} already connected")
        emit("connection_response", {"status": "already_connected"}, to=request.sid)
    else:
        logger.info(f"Client {request.sid} connected with role {role}")
        client_queue[request.sid] = {}
        client_queue[request.sid]["role"] = role
        client_queue[request.sid]["voice_frames"] = deque()
        client_queue[request.sid]["audio_buffer"] = b""
        client_queue[request.sid]["is_currently_speaking"] = False
        client_queue[request.sid]["silent_frames"] = 0
        client_queue[request.sid]["last_speech_time"] = None
        client_queue[request.sid]["origin_silent"] = origin_silent
        if role == Role.CLIENT.value:
            client_queue[request.sid]["source_language"] = "eng"
            client_queue[request.sid]["target_language"] = "ind"
        elif role == Role.STAFF.value:
            client_queue[request.sid]["source_language"] = "ind"
            client_queue[request.sid]["target_language"] = "eng"
        emit(
            "connection_response", {"status": "accepted", "role": role}, to=request.sid
        )


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in client_queue.keys():
        logger.info(f"Client {request.sid} disconnected")
        del client_queue[request.sid]
        emit("disconnection_response", {"status": "accepted"}, to=request.sid)
    else:
        emit(
            "disconnection_response", {"status": "already_disconnected"}, to=request.sid
        )


@socketio.on("audio_stream")
def handle_audio_stream(data):
    if request.sid not in client_queue.keys():
        emit("error", {"error": "connection not establish"}, to=request.sid)
        return
    info = client_queue[request.sid]
    info["audio_buffer"] += data
    while len(info["audio_buffer"]) >= CHUNK:
        data_block = info["audio_buffer"][:CHUNK]
        info["audio_buffer"] = info["audio_buffer"][CHUNK:]
        is_speech = vad.is_speech(data_block, SAMPLE_RATE)
        is_currently_speaking = info["is_currently_speaking"]
        if is_speech:
            now = time.time()
            if not is_currently_speaking:
                logger.info("Start waitting")
                info["is_currently_speaking"] = True
                info["silent_frames"] = 0
                info["last_speech_time"] = now
            info["voice_frames"].append(data_block)
            if now - info["last_speech_time"] > SPEAK_MAX_TIME:
                logger.info(f"More than {SPEAK_MAX_TIME}s voice, process.")
                StreamProcessor.process_accumulated_voice_frames(
                    CHANNELS, SAMPLE_RATE, FORMAT, info
                )
        else:
            if is_currently_speaking and info["voice_frames"]:
                info["silent_frames"] += 1
                if info["silent_frames"] >= SILENT_MAX_FRAME:
                    logger.info(f"More than {SILENT_MAX_FRAME} silent frames, process.")
                    StreamProcessor.process_accumulated_voice_frames(
                        CHANNELS, SAMPLE_RATE, FORMAT, info
                    )


if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host="0.0.0.0")
