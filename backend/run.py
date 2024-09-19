import os
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from collections import deque
from fairseq2.memory import MemoryBlock
from app.services.m4t.m4t_model import voice_predictor
from app.services.translate.s2tt_service import S2TTService
from app.services.tts.tts_service import TTSProcessor
from app.services.tts.tts_model import TTSModel
from app.controller import urls


import webrtcvad
import io
import time
import wave
import requests
import json
import pyaudio


app = Flask(__name__)
CORS(app)
app.register_blueprint(urls.api)
socketio = SocketIO(app, cors_allowed_origins="*")
users = {}
max_users = 2
client_queue = {}
vad = webrtcvad.Vad(3)
frame_duration = 20  # 可以是10, 20, 或30毫秒
SAMPLE_RATE = 8000
samples_per_frame = int(SAMPLE_RATE * frame_duration / 1000)
bytes_per_sample = 2
CHUNK = samples_per_frame * bytes_per_sample
FORMAT = pyaudio.paInt16
CHANNELS = 1


def process_accumulated_voice_frames(info):
    audio_data_bytes = b"".join(info["voice_frames"])
    if is_speech_by_wiz(audio_data_bytes, SAMPLE_RATE, audio_format="pcm"):
        with io.BytesIO() as mem_file:
            with wave.open(mem_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data_bytes)
            complete_wav_data = mem_file.getvalue()
        mem_block = MemoryBlock(complete_wav_data)
        decoded_audio = voice_predictor.translator.decode_audio(mem_block)
        text = S2TTService.speech_to_translated_text(
            decoded_audio["waveform"], info["language"]
        )
        print(f"output text: {text} ")
        tts = TTSProcessor(info["language"])
        tts_model_value = TTSModel.get_tts_model_value("TTS_WIZ")
        byte_data, _ = tts.text_to_speech(text, tts_model_value, output="byte")
        emit("audio_stream_output", byte_data, broadcast=True, include_self=False)
        info["is_currently_speaking"] = False
        info["silent_frames"] = 0
    else:
        print("silent...")
    info["voice_frames"].clear()


def is_speech_by_wiz(data, sample_rate, audio_format="pcm"):
    if len(data) % 2 != 0:
        data += b"\x00"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/octet-stream",
    }
    params = {"format": audio_format, "sample_rate": sample_rate}
    response = requests.post(
        "http://192.168.32.69:9002/asr/audio_classifier",
        params=params,
        headers=headers,
        data=data,
    )
    print(response.text)
    if response.status_code == 200:
        return json.loads(response.text).get("is_speech", False)
    print("request failed.")
    return False


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
        client_queue[request.sid] = {}
        client_queue[request.sid]["voice_frames"] = deque()
        client_queue[request.sid]["audio_buffer"] = b""
        client_queue[request.sid]["is_currently_speaking"] = False
        client_queue[request.sid]["silent_frames"] = 0
        client_queue[request.sid]["last_speech_time"] = None
        if role == "client":
            client_queue[request.sid]["language"] = "ind"
        elif role == "staff":
            client_queue[request.sid]["language"] = "eng"
        emit(
            "connection_response", {"status": "accepted", "role": role}, to=request.sid
        )


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in users:
        print(f"Client {request.sid} disconnected")
        del users[request.sid]
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
        if is_speech:
            now = time.time()
            if not info["is_currently_speaking"]:
                info["is_currently_speaking"] = True
                info["silent_frames"] = 0
                info["last_speech_time"] = now
            info["voice_frames"].append(data_block)
            if now - info["last_speech_time"] > 10:
                process_accumulated_voice_frames(info)
        else:
            if info["is_currently_speaking"] and info["voice_frames"]:
                info["silent_frames"] += 1
                if info["silent_frames"] >= 20:
                    process_accumulated_voice_frames(info)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


ensure_dir("logs")
ensure_dir("data")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host="0.0.0.0")
