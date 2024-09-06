import json
import logging

from flask import request, Response
from flask.views import MethodView
from app.services.translate.t2tt_service import T2TTService
from app.services.translate.t2st_service import T2STService
from app.services.translate.s2st_service import S2STService
from app.services.translate.s2tt_service import S2TTService
from app.services.tts.tts_service import TTSProcessor
from app.services.tts.tts_model import TTSModel
from app.services.translate.model import TranslationModel
from app.services.audio.audio_service import AudioService
from app.services.history.history_service import HistoryService
from app.constants import TranslationType, AudioFormat, Role

logger = logging.getLogger(__name__)


class TextTranslationViews(MethodView):
    def post(self):
        params = request.json
        si_model = params.get("si_model", "trans_model")
        source_language = params.get("source_language", "EN")
        target_language = params.get("target_language", "IN")
        output_type = params.get("output_type", TranslationType.TEXT.value)
        use_tts = int(params.get("use_tts", 0))
        tts_model = params.get("tts_model", "tts_model")
        input = params.get("input")
        history_data = {}

        try:
            history_data = {
                "type": TranslationType.TEXT.value,
                "text": input,
                "audio_id": "",
            }
            HistoryService.create_history(Role.CLIENT.value, history_data)
            trans_model = TranslationModel.get_translate_model_value(si_model)
            lang_source = TranslationModel.get_language_value(source_language)
            lang_target = TranslationModel.get_language_value(target_language)
            audio_id = ""
            if output_type == TranslationType.TEXT.value:
                trans_text = T2TTService.text_to_text_translated(
                    input, lang_source, lang_target, trans_model
                )
                history_data = {
                    "type": TranslationType.TEXT.value,
                    "text": trans_text,
                    "audio_id": "",
                }
            elif output_type == TranslationType.SPEECH.value:
                if use_tts:
                    trans_text = T2TTService.text_to_text_translated(
                        input, lang_source, lang_target, trans_model
                    )
                    tts = TTSProcessor(lang_target)
                    tts_model_value = TTSModel.get_translate_model_value(tts_model)
                    torch_data, rate = tts.text_to_speech(trans_text, tts_model_value)
                else:
                    trans_text, torch_data, rate = T2STService.text_to_speech_translated(
                        input, lang_source, lang_target, trans_model
                    )
                audio = AudioService.create_audio_by_torch_data(
                    torch_data, rate, AudioFormat.WAV.value
                )
                audio_id = audio.id
                history_data = {
                    "type": TranslationType.SPEECH.value,
                    "text": input,
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
                content_type="application/json",
            )


class SpeechTranslationViews(MethodView):
    def post(self):
        params = request.form
        si_model = params.get("si_model", "trans_model")
        source_language = params.get("source_language", "EN")
        target_language = params.get("target_language", "IN")
        output_type = params.get("output_type", TranslationType.TEXT.value)
        use_tts = int(params.get("use_tts", 0))
        file = request.files["file"]
        tts_model = params.get("tts_model", "tts_model")
        history_data = {}

        try:
            lang_source = TranslationModel.get_language_value(source_language)
            lang_target = TranslationModel.get_language_value(target_language)
            audio_input = AudioService.create_audio_by_file(file)
            file_full_path = audio_input.root_dir_path + "/" + audio_input.filename
            history_data = {
                "type": TranslationType.SPEECH.value,
                "text": "",
                "audio_id": audio_input.id,
            }
            HistoryService.create_history(Role.CLIENT.value, history_data)
            trans_model = TranslationModel.get_translate_model_value(si_model)
            audio_id = ""
            if output_type == TranslationType.TEXT.value:
                trans_text = S2TTService.speech_to_translated_text(
                    file_full_path, lang_source, lang_target, trans_model
                )
                history_data = {
                    "type": TranslationType.TEXT.value,
                    "text": trans_text,
                    "audio_id": "",
                }
            elif output_type == TranslationType.SPEECH.value:
                if use_tts:
                    trans_text = S2TTService.speech_to_translated_text(
                        file_full_path, lang_source, lang_target, trans_model
                    )
                    tts = TTSProcessor(lang_target)
                    tts_model_value = TTSModel.get_translate_model_value(tts_model)
                    torch_data, rate = tts.text_to_speech(trans_text, tts_model_value)
                else:
                    trans_text, torch_data, rate = S2STService.speech_to_speech_translated(
                        file_full_path,
                        lang_source,
                        lang_target,
                        trans_model,
                    )
                audio = AudioService.create_audio_by_torch_data(
                    torch_data, rate, AudioFormat.WAV.value
                )
                audio_id = audio.id
                history_data = {
                    "type": TranslationType.SPEECH.value,
                    "text": trans_text,
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
                content_type="application/json",
            )
