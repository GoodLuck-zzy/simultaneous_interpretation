import torch
from seamless_communication.inference import Translator


class M4TModel:
    def __init__(
        self,
        model_name="seamlessM4T_large",
        vocoder_name="vocoder_36langs",
        checkpoint_path="/root/zzy/app/models/MenuSifu_ID_S2S_v1_9.pt",
    ) -> None:
        self.translator = Translator(
            model_name,
            vocoder_name,
            torch.device("cuda:0"),
            dtype=torch.float16,
        )
        self._load_checkpoint(
            self.translator.model,
            checkpoint_path,
            device=torch.device("cpu"),
        )

    def _select_keys(self, target_state_dict, source_state_dict, prefix):
        select_state_dict = {
            key.replace(prefix, ""): value
            for key, value in source_state_dict.items()
            if key.startswith(prefix)
        }
        target_state_dict.load_state_dict(select_state_dict)

    def _load_checkpoint(self, model, path, device=torch.device("cpu")):
        saved_model = torch.load(path, map_location=device)["model"]
        self._select_keys(
            model.speech_encoder_frontend,
            saved_model,
            "module.model.speech_encoder_frontend.",
        )
        self._select_keys(
            model.speech_encoder, saved_model, "module.model.speech_encoder."
        )
        self._select_keys(
            model.text_decoder_frontend,
            saved_model,
            "module.model.text_decoder_frontend.",
        )
        self._select_keys(model.text_decoder, saved_model, "module.model.text_decoder.")
        self._select_keys(model.final_proj, saved_model, "module.model.final_proj.")
        self._select_keys(
            model.text_encoder_frontend,
            saved_model,
            "module.model.text_encoder_frontend.",
        )
        self._select_keys(model.t2u_model, saved_model, "module.model.t2u_model.")


voice_predictor = M4TModel()
