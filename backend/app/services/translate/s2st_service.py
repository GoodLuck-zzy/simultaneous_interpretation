import torch


class S2STService:
    @classmethod
    def speech_to_speech_translated(
        cls,
        audio_file,
        source_language,
        target_language,
        tans_model,
    ):
        text, out_audios = tans_model.translator.predict(
            input=audio_file,
            task_str="S2ST",
            src_lang=source_language,
            tgt_lang=target_language,
        )
        out_torch = out_audios.audio_wavs[0][0].to(torch.float32).cpu()
        return str(text[0]), out_torch, out_audios.sample_rate
