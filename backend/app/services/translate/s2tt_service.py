class S2TTService:
    @classmethod
    def speech_to_translated_text(
        cls,
        audio_file,
        source_language,
        target_language,
        tans_model,
    ):
        text, _ = tans_model.translator.predict(
            input=audio_file,
            task_str="S2TT",
            src_lang=source_language,
            tgt_lang=target_language,
        )
        return str(text[0])
