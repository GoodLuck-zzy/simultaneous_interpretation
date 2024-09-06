from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os


class MysqlSetting(BaseModel):
    user: str = os.environ.get("MYSQL_USER", "root")
    password: str = os.environ.get("MYSQL_PASSWORD") or "123456"
    port: int = int(os.environ.get("MYSQL_PORT", 3306))
    database: str = os.environ.get("MYSQL_DB", "si_demo")
    host: str = os.environ.get("MYSQL_HOST", "localhost")
    max_connections: int = os.environ.get("MYSQL_MAX_CONNECTIONS", 20)
    autoconnect: bool = os.environ.get("MYSQL_AUTOCONNECT", False)


class WizTTSSetting(BaseModel):
    tts_url: str = os.environ.get(
        "WIZ_TTS_URL", "http://192.168.33.74:8021/model_service/tts"
    )


class WizASRSetting(BaseModel):
    asr_url: str = os.environ.get(
        "WIZ_ASR_URL", "http://192.168.32.69:9001/asr/customized/transfer"
    )
    asr_video_url: str = os.environ.get(
        "WIZ_ASR_VIDEO_URL", "http://10.0.3.90:9001/asr/media/inspection"
    )


class WizVadSetting(BaseModel):
    vad_url: str = os.environ.get(
        "WIZ_VAD_URL", "http://192.168.32.69:9002/asr/audio_classifier"
    )


class Settings(BaseSettings):
    mysql: MysqlSetting = MysqlSetting()
    wiz_asr: WizASRSetting = WizASRSetting()
    wiz_tts: WizTTSSetting = WizTTSSetting()
    wiz_vad: WizVadSetting = WizVadSetting()

    class Config:
        env_nested_delimiter = "__"


settings = Settings()
