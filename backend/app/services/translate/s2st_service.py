class S2STService:
    @classmethod
    def speech_to_speech_translated(
        cls,
        audio_data,
        source_language,
        target_language,
        sample_rate,
        tans_model,
    ):
        text, out_audios = tans_model.predict(
            input=audio_data,
            task_str="S2ST",
            src_lang=source_language,
            tgt_lang=target_language,
            sample_rate=sample_rate,
        )
        out_wav = out_audios.audio_wavs[0].cpu().detach().numpy()
        return str(text[0]), out_wav
