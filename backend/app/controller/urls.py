from flask import Blueprint
from flask_cors import CORS
from app.controller.views import models_views
from app.controller.views import tts_views


api = Blueprint("demo", __name__, url_prefix="/demo")
CORS(api)

api.add_url_rule(
    "/s2tt_model",
    view_func=models_views.S2TTModelConfig.as_view(name="s2tt model config"),
    methods=["GET"],
)

api.add_url_rule(
    "/tts_model",
    view_func=models_views.TTSModelConfig.as_view(name="tts model config"),
    methods=["GET"],
)

api.add_url_rule(
    "/tts_generate",
    view_func=tts_views.TTSViews.as_view(name="tts only generate"),
    methods=["POST"],
)