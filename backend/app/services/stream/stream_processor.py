import io
import wave
import pyaudio
import logging
import tempfile
from flask_socketio import emit
from concurrent.futures import ThreadPoolExecutor
from app.services.translate.s2tt_service import S2TTService
from app.services.translate.model import TranslationModel
from app.services.tts.tts_service import TTSProcessor
from app.services.tts.tts_model import TTSModel
from app.services.vad.vad_service import VadService
from app.services.audio.audio_service import AudioService
from app.services.history.history_service import HistoryService
from app.constants import OutputFormat, AudioFormat, TranslationType
from app.utils.audio_utils import bytes_to_torch

logger = logging.getLogger(__name__)


class StreamProcessor:
    @classmethod
    def save_wave(data, filename, channels=1, sampwidth=2, framerate=44100):
        with wave.open(filename, 'wb') as wave_file:
            wave_file.setnchannels(channels)
            wave_file.setsampwidth(sampwidth)
            wave_file.setframerate(framerate)
            wave_file.writeframes(data)
    @classmethod
    def process_audio_async(cls, info, byte_data, text):
        torch_data, rate = bytes_to_torch(byte_data)
        audio_output = AudioService.create_audio_by_torch_data(
            torch_data, rate, AudioFormat.WAV.value
        )
        audio_id = audio_output.id
        history_data = {
            "type": TranslationType.SPEECH.value,
            "text": text,
            "audio_id": audio_id,
        }
        HistoryService.create_history(info["role"], history_data)

    @classmethod
    def process_accumulated_voice_frames(cls, channels, sample_rate, sample_size, info):
        audio_data_bytes = b"".join(info["voice_frames"])
        if VadService.is_speech_with_wiz_vad(
            audio_format="pcm", sample_rate=sample_rate, data=audio_data_bytes
        ):
            logger.info("Is speech, process")
            if not info["origin_silent"]:
                emit(
                    "origin_audio_stream_output",
                    audio_data_bytes,
                    broadcast=True,
                    include_self=False,
                )
            # torch_data, rate = bytes_to_torch(audio_data_bytes)
            # audio_input = AudioService.create_audio_by_torch_data(
            #     torch_data, rate, AudioFormat.WAV.value
            # )
            # audio_id = audio_input.id
            # history_data = {
            #     "type": TranslationType.SPEECH.value,
            #     "text": "",
            #     "audio_id": audio_id,
            # }
            # HistoryService.create_history(info["role"], history_data)
            with io.BytesIO() as mem_file:
                with wave.open(mem_file, "wb") as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(pyaudio.get_sample_size(sample_size))
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data_bytes)
                complete_wav_data = mem_file.getvalue()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(complete_wav_data)
                temp_file_path = temp_file.name
            trans_model = TranslationModel.get_translate_model_value("M4T-0830V1")
            text = S2TTService.speech_to_translated_text(
                temp_file_path,
                info["source_language"],
                info["target_language"],
                trans_model,
            )
            logger.info(f"Translation output text: {text} ")
            tts = TTSProcessor(info["target_language"])
            tts_model_value = TTSModel.get_tts_model_value("TTS_WIZ")
            byte_data, _ = tts.text_to_speech(
                text, tts_model_value, output=OutputFormat.BYTE.value
            )
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.submit(cls.process_audio_async, info, byte_data, text)
            emit("audio_stream_output", byte_data, broadcast=True, include_self=False)
        info["voice_frames"].clear()
        info["is_currently_speaking"] = False
