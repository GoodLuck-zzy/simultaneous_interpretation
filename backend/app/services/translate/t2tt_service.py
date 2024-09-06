class T2TTService:
    @classmethod
    def text_to_text_translated(
        cls,
        text,
        source_language,
        target_language,
        tans_model,
    ):
        text, _ = tans_model.translator.predict(
            input=text,
            task_str="T2TT",
            src_lang=source_language,
            tgt_lang=target_language,
        )
        return str(text[0])
