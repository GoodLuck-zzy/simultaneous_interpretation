from app.services.m4t.m4t_model import voice_predictor


class S2TTService:
    @classmethod
    def speech_to_translated_text(
        cls,
        audio_data,
        source_language,
        target_language,
        sample_rate,
        tans_model,
    ):
        text, _ = tans_model.predict(
            input=audio_data,
            task_str="S2TT",
            src_lang=source_language,
            tgt_lang=target_language,
            sample_rate=sample_rate,
        )
        return str(text[0])
