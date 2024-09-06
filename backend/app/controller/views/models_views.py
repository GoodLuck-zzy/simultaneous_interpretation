import json
import logging

from flask import Response
from flask.views import MethodView
from app.services.tts.tts_model import TTSModel
from app.services.translate.model import TranslationModel

logger = logging.getLogger(__name__)


class S2TTModelConfig(MethodView):
    def get(self):
        try:
            models = TranslationModel.get_translation_models()
            languages = TranslationModel.get_translation_languages()
            res = {"models": models, "languages": languages}
        except Exception:
            return Response(
                json.dumps(
                    {"error": "model or language is invalid"}, ensure_ascii=False
                ),
                status=400,
                content_type='application/json"',
            )
        return Response(json.dumps(res), status=200, content_type="application/json")


class TTSModelConfig(MethodView):
    def get(self):
        try:
            models = TTSModel.get_tts_models()
            languages = TTSModel.get_tts_languages()
            res = {"models": models, "languages": languages}
        except Exception:
            return Response(
                json.dumps(
                    {"error": "model or language is invalid"}, ensure_ascii=False
                ),
                status=400,
                content_type='application/json"',
            )
        return Response(json.dumps(res), status=200, content_type="application/json")
