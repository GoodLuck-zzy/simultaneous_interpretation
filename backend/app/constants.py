from enum import Enum


class TranslationType(Enum):
    SPEECH = "speech"
    TEXT = "text"


class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    PCM = "pcm"


class Role(Enum):
    CLIENT = "client"
    STAFF = "staff"
