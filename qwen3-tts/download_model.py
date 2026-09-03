"""Download the standard public Qwen3-TTS 1.7B voice-cloning model."""

from pathlib import Path

from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-1.7B-Base"

snapshot_download(
    repo_id=MODEL_ID,
    local_dir=str(MODEL_DIR),
)
print(f"Model download complete: {MODEL_DIR}")
