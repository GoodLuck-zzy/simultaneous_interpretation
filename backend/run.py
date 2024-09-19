import os
import io
import time
import wave
import pyaudio
import webrtcvad

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from collections import deque
from fairseq2.memory import MemoryBlock
from app.services.m4t.m4t_model import voice_predictor
from app.services.translate.s2tt_service import S2TTService
from app.services.translate.model import TranslationModel
from app.services.tts.tts_service import TTSProcessor
from app.services.tts.tts_model import TTSModel
from app.services.vad.vad_service import VadService
from app.controller import urls


app = Flask(__name__)
app.register_blueprint(urls.api)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
users = {}
max_users = 2
client_queue = {}
vad = webrtcvad.Vad(3)
frame_duration = 20  # 可以是10, 20, 或30毫秒
bytes_per_sample = 2
SAMPLE_RATE = 8000
samples_per_frame = int(SAMPLE_RATE * frame_duration / 1000)
CHUNK = samples_per_frame * bytes_per_sample
FORMAT = pyaudio.paInt16
CHANNELS = 1


def process_accumulated_voice_frames(info):
    audio_data_bytes = b"".join(info["voice_frames"])
    if VadService.is_speech_with_wiz_vad(
        audio_format="pcm", sample_rate=SAMPLE_RATE, data=audio_data_bytes
    ):
        print("is speech wiz is True")
        with io.BytesIO() as mem_file:
            with wave.open(mem_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data_bytes)
            complete_wav_data = mem_file.getvalue()
        mem_block = MemoryBlock(complete_wav_data)
        decoded_audio = voice_predictor.translator.decode_audio(mem_block)
        trans_model = TranslationModel.get_translate_model_value("M4T-0830V1")
        text = S2TTService.speech_to_translated_text(
            decoded_audio["waveform"],
            info["source_language"],
            info["target_language"],
            trans_model,
        )
        print(f"output text: {text} ")
        tts = TTSProcessor(info["target_language"])
        tts_model_value = TTSModel.get_tts_model_value("TTS_WIZ")
        byte_data, _ = tts.text_to_speech(text, tts_model_value, output="byte")
        emit("audio_stream_output", byte_data, broadcast=True, include_self=False)
        info["is_currently_speaking"] = False
        info["silent_frames"] = 0
    else:
        print("silent...")
    info["voice_frames"].clear()


@socketio.on("connect")
def on_connect():
    print("on_connect start")
    role = request.args.get("role")
    if len(users) >= max_users:
        print("Maximum number of connections reached")
        emit("connection_response", {"status": "rejected"}, to=request.sid)
    elif request.sid in users.keys():
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
            client_queue[request.sid]["source_language"] = "eng"
            client_queue[request.sid]["target_language"] = "ind"
        elif role == "staff":
            client_queue[request.sid]["source_language"] = "ind"
            client_queue[request.sid]["target_language"] = "eng"
        emit(
            "connection_response", {"status": "accepted", "role": role}, to=request.sid
        )
        print(client_queue)


@socketio.on("disconnect")
def on_disconnect():
    print(request.sid)
    print(users.keys())
    if request.sid in users.keys():
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
    print(f"send data length: {len(data)}")
    print("-----------------------------------------")
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
            if now - info["last_speech_time"] > 5:
                print("More than 5s voice, process.")
                process_accumulated_voice_frames(info)
        else:
            if info["is_currently_speaking"] and info["voice_frames"]:
                info["silent_frames"] += 1
                print("save silent frames")
                if info["silent_frames"] >= 20:
                    print("More than 20 silent frames, process.")
                    process_accumulated_voice_frames(info)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


ensure_dir("logs")
ensure_dir("data")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host="0.0.0.0")
