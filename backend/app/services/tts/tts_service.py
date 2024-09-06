import io
import json
import requests
import numpy as np
import soundfile as sf

from app.settings import settings


class TTSProcessor:
    language_map = {
        "eng": "Jenny",
        "ind": "Alifan",
    }

    def __init__(
        self, voice, volume=45, speech_rate=55, format="wav", sample_rate=16000
    ) -> None:
        self.voice = self.language_map[voice]
        self.volume = volume
        self.speech_rate = speech_rate
        self.format = format
        self.sample_rate = sample_rate
        self.tts_url = settings.wiz_tts.tts_url

    def bytes_to_numpy(self, audio_bytes):
        with io.BytesIO(audio_bytes) as audio_buffer:
            data, sample_rate = sf.read(audio_buffer)
        return data, sample_rate

    def text_to_speech(self, text):
        payload = {
            "format": self.format,
            "sample_rate": self.sample_rate,
            "speech_rate": self.speech_rate,
            "text": text,
            "text_type": "DEFAULT",
            "voice": self.voice,
            "volume": self.volume,
        }
        try:
            response = requests.post(self.tts_url, data=json.dumps(payload), timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
            return None, None
        if response.status_code == 200:
            np_data, sample_rate = self.bytes_to_numpy(response.content)
            return np_data, sample_rate
        else:
            print(f"Some error occured. Request return {response.status_code}")
            return None, None
