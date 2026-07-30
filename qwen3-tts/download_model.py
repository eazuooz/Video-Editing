"""Download the public Qwen3-TTS base model through ModelScope."""

from pathlib import Path

from modelscope import snapshot_download


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"

snapshot_download(
    "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    local_dir=str(MODEL_DIR),
)
print(f"Model download complete: {MODEL_DIR}")
