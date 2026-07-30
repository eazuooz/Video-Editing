"""Generate a local Qwen3-TTS voice-cloning sample from the user's reference WAV."""

from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
OUTPUT = ROOT / "shared" / "audio-samples" / "qwen3-jump-physics-balanced.wav"
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"

TEXT = (
    "캐릭터가 점프하는 건 단순해 보이지만, 매 프레임 적용되는 중력이 "
    "점프의 감각을 바꿉니다. 속도 5로 시작해도 중력이 계속 더해지면, "
    "최고점 이후 아래로 점점 빠르게 떨어집니다."
)


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for local Qwen3-TTS inference.")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Reference audio not found: {REFERENCE}")
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_DIR}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_DIR),
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    wavs, sample_rate = model.generate_voice_clone(
        text=TEXT,
        language="Korean",
        ref_audio=str(REFERENCE),
        x_vector_only_mode=True,
        non_streaming_mode=True,
    )
    sf.write(OUTPUT, wavs[0], sample_rate)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
