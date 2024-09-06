class TTSModel:
    models = [
        {
            "name": "tts_model",
            "value": "ttsmodel1",
        },
        {
            "name": "tts_other_model",
            "value": "ttsmodel2",
        },
    ]

    languages = [
        {"name": "EN", "value": "eng"},
        {"name": "IN", "value": "ind"},
    ]

    @classmethod
    def get_tts_models(cls):
        return [model["name"] for model in cls.models]

    @classmethod
    def get_tts_languages(cls):
        return [lang["name"] for lang in cls.languages]
