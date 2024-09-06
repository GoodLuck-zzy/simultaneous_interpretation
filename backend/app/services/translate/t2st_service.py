from app.services.m4t.m4t_model import voice_predictor


class T2STService:
    @classmethod
    def text_to_speech_translated(
        cls,
        text,
        source_language,
        target_language,
        tans_model
    ):
        text, out_audios = tans_model.predict(
            input=text,
            task_str="T2ST",
            src_lang=source_language,
            tgt_lang=target_language,
        )
        out_wav = out_audios.audio_wavs[0].cpu().detach().numpy()
        return str(text[0]), out_wav, 16000
