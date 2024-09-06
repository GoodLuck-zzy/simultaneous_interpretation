import json
import logging

from flask import Response
from flask.views import MethodView
from app.services.history.history_service import HistoryService
from app.services.audio.audio_service import AudioService

logger = logging.getLogger(__name__)


class HistoryViews(MethodView):
    def post(self):
        list = HistoryService.list_histories()
        return Response(json.dumps(list), status=200, content_type="application/json")

    def delete(self):
        try:
            HistoryService.delete_all()
            AudioService.clear_all()
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}, ensure_ascii=False),
                status=400,
                content_type="application/json",
            )
        return Response(
            json.dumps({"status": "ok"}),
            200,
            content_type="application/json",
        )
