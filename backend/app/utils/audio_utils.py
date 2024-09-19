import io
import torchaudio


def bytes_to_torch(audio_bytes):
    audio_buf = io.BytesIO(audio_bytes)
    waveform, sample_rate = torchaudio.load(audio_buf)
    return waveform, sample_rate
