import json
import requests
from app.settings import settings
from app.constants import OutputFormat
from app.utils.audio_utils import bytes_to_torch


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

    def text_to_speech(self, text, model="TTS_WIZ", output=OutputFormat.TORCH.value):
        if model == "TTS_WIZ":
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
                response = requests.post(
                    self.tts_url, data=json.dumps(payload), timeout=5
                )
            except requests.exceptions.RequestException as e:
                print(f"Error: {str(e)}")
                return None, None
            if response.status_code == 200:
                if output == OutputFormat.TORCH.value:
                    torch_data, sample_rate = bytes_to_torch(response.content)
                    return torch_data, sample_rate
                elif output == OutputFormat.BYTE.value:
                    return response.content, self.sample_rate
            else:
                print(f"Some error occured. Request return {response.status_code}")
                return None, None
        else:
            return None, None
