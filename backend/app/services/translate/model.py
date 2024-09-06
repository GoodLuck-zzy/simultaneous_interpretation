from app.services.m4t.m4t_model import voice_predictor


class TranslationModel:
    models = [
        {
            "name": "M4T-0830V1",
            "value": voice_predictor,
        },
    ]

    languages = [
        {"name": "EN", "value": "eng"},
        {"name": "IN", "value": "ind"},
    ]

    @classmethod
    def get_translation_models(cls):
        return [model["name"] for model in cls.models]

    @classmethod
    def get_translation_languages(cls):
        return [lang["name"] for lang in cls.languages]

    @classmethod
    def get_language_value(cls, name):
        for item in cls.languages:
            if name == item["name"]:
                return item["value"]
        return None

    @classmethod
    def get_translate_model_value(cls, name):
        for item in cls.models:
            if name == item["name"]:
                return item["value"]
        return None
