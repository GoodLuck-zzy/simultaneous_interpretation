import json
import webrtcvad
import requests
import logging
from app.settings import settings

logger = logging.getLogger(__name__)


class VadService:
    vad = webrtcvad.Vad(1)

    @classmethod
    def is_speech_by_webrtc(cls, frame, rate):
        return cls.vad.is_speech(frame, rate)

    @classmethod
    def is_speech_with_wiz_vad(cls, audio_format, sample_rate, data):
        if len(data) % 2 != 0:
            data += b"\x00"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/octet-stream",
        }
        params = {"format": audio_format, "sample_rate": sample_rate}
        response = requests.post(
            settings.wiz_vad.vad_url,
            params=params,
            headers=headers,
            data=data,
            timeout=2,
        )
        if response.status_code == 200:
            return json.loads(response.text).get("is_speech", False)
        logger.error("request wiz vad failed.")
        return False
