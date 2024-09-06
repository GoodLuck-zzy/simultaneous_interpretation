import torch


class T2STService:
    @classmethod
    def text_to_speech_translated(
        cls, text, source_language, target_language, tans_model
    ):
        text, out_audios = tans_model.translator.predict(
            input=text,
            task_str="T2ST",
            src_lang=source_language,
            tgt_lang=target_language,
        )
        out_torch = out_audios.audio_wavs[0][0].to(torch.float32).cpu()
        return str(text[0]), out_torch, out_audios.sample_rate
