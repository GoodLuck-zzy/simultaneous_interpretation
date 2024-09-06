import json
import logging

from flask import request, Response
from flask.views import MethodView
from app.services.translate.model import TranslationModel
from app.services.tts.tts_service import TTSProcessor
from app.services.tts.tts_model import TTSModel
from app.services.audio.audio_service import AudioService
from app.services.history.history_service import HistoryService
from app.constants import TranslationType, AudioFormat, Role

logger = logging.getLogger(__name__)


class TTSViews(MethodView):
    def post(self):
        params = request.json
        tts_model = params.get("tts_model", "tts_model")
        target_language = params.get("target_language", "IN")
        input = params.get("input")
        history_data = {}
        try:
            history_data = {
                "type": TranslationType.TEXT.value,
                "text": input,
                "audio_id": "",
            }
            HistoryService.create_history(Role.CLIENT.value, history_data)
            tts_model_value = TTSModel.get_translate_model_value(tts_model)
            torch_data = None
            audio_id = ""
            lang = TranslationModel.get_language_value(target_language)
            tts = TTSProcessor(lang)
            torch_data, rate = tts.text_to_speech(input, tts_model_value)
            audio = AudioService.create_audio_by_torch_data(
                torch_data, rate, AudioFormat.WAV.value
            )
            audio_id = audio.id
            history_data = {
                "type": TranslationType.SPEECH.value,
                "text": "",
                "audio_id": audio_id,
            }
            HistoryService.create_history(Role.STAFF.value, history_data)
            return Response(
                json.dumps({"audio_id": audio_id}),
                200,
                content_type="application/json",
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}, ensure_ascii=False),
                status=400,
                content_type='application/json',
            )
