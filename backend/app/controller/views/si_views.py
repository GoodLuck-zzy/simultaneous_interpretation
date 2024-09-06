import json
import logging

from flask import request, Response
from flask.views import MethodView
from app.services.translate.t2tt_service import T2TTService
from app.services.translate.t2st_service import T2STService
from app.services.translate.model import TranslationModel
from app.services.tts.tts_service import TTSProcessor
from app.services.audio.audio_service import AudioService
from app.constants import TranslationType, AudioFormat

logger = logging.getLogger(__name__)


class TextGenerate(MethodView):
    def post(self):
        params = request.json
        si_model = params.get("si_model", "s2tt_model")
        source_language = params.get("source_language", "EN")
        target_language = params.get("target_language", "IN")
        output_type = params.get("output_type", TranslationType.TEXT.value)
        use_tts = params.get("use_tts", True)
        input = params.get("input")
        try:
            trans_model = TranslationModel.get_translate_model_value(si_model)
            np_data = None
            audio_id = ""
            if output_type == TranslationType.TEXT.value:
                trans_text = T2TTService.text_to_text_translated(
                    input, source_language, target_language, trans_model
                )
            elif output_type == TranslationType.SPEECH.value:
                if use_tts:
                    trans_text = T2TTService.text_to_text_translated(
                        input, source_language, target_language, trans_model
                    )
                    lang = TranslationModel.get_language_value(target_language)
                    tts = TTSProcessor(lang)
                    np_data, rate = tts.text_to_speech(trans_text)
                else:
                    trans_text, np_data, rate = T2STService.text_to_speech_translated(
                        input, source_language, target_language, trans_model
                    )
                audio = AudioService.create_audio_by_npdata(np_data, rate, AudioFormat.WAV.value)
                audio_id = audio.id
            return Response(
                json.dumps({"audio_id": audio_id, "translated_text": trans_text}),
                200,
                content_type="application/json",
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}, ensure_ascii=False),
                status=400,
                content_type='application/json"',
            )