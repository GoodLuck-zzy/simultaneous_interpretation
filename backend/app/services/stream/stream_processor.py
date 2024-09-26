import io
import wave
import pyaudio
import logging
from flask_socketio import emit
from fairseq2.memory import MemoryBlock
from app.services.m4t.m4t_model import voice_predictor
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
    def process_accumulated_voice_frames(cls, channels, sample_rate, sample_size, info):
        audio_data_bytes = b"".join(info["voice_frames"])
        if VadService.is_speech_with_wiz_vad(
            audio_format="pcm", sample_rate=sample_rate, data=audio_data_bytes
        ):
            logger.info("is speech, process")
            if not info["origin_silent"]:
                emit("origin_audio_stream_output", audio_data_bytes, broadcast=True, include_self=False)
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
            mem_block = MemoryBlock(complete_wav_data)
            decoded_audio = voice_predictor.translator.decode_audio(mem_block)
            trans_model = TranslationModel.get_translate_model_value("M4T-0830V1")
            text = S2TTService.speech_to_translated_text(
                decoded_audio["waveform"],
                info["source_language"],
                info["target_language"],
                trans_model,
            )
            logger.info(f"output text: {text} ")
            tts = TTSProcessor(info["target_language"])
            tts_model_value = TTSModel.get_tts_model_value("TTS_WIZ")
            byte_data, _ = tts.text_to_speech(
                text, tts_model_value, output=OutputFormat.BYTE.value
            )
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
            emit("audio_stream_output", byte_data, broadcast=True, include_self=False)
            info["is_currently_speaking"] = False
            info["silent_frames"] = 0
        else:
            logger.info("silent...")
        info["voice_frames"].clear()
