"""Generate three local, Korean voice-cloned narration samples.

The reference recording stays on this PC.  Chatterbox downloads model weights on
its first run, then generates all output locally on the CUDA GPU.
"""

from __future__ import annotations

from pathlib import Path

import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
OUTPUT_DIR = ROOT / "shared" / "audio-samples" / "jump-physics"

TEXT = (
    "캐릭터가 점프하는 것은 매우 단순한 액션처럼 보이지만, "
    "여기에도 여러 가지 고려해야 할 점이 있습니다.\n\n"
    "처음에 위쪽으로 속도 5를 준 뒤, 공중에 있는 동안 매 프레임마다 "
    "1만큼의 낙하 가속도를 적용한다고 해 봅시다.\n\n"
    "속도는 5에서 4, 3, 2처럼 줄어들고, 0이 된 뒤에는 "
    "아래쪽으로 점점 빠르게 떨어집니다."
)

# Higher exaggeration generally delivers a more energetic, faster read.
TONES = {
    "01-calm.wav": {"exaggeration": 0.35, "cfg_weight": 0.55},
    "02-balanced.wav": {"exaggeration": 0.50, "cfg_weight": 0.50},
    "03-brisk.wav": {"exaggeration": 0.70, "cfg_weight": 0.35},
}


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for this local generation workflow.")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Reference audio not found: {REFERENCE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")

    for filename, settings in TONES.items():
        wav = model.generate(
            TEXT,
            language_id="ko",
            audio_prompt_path=str(REFERENCE),
            temperature=0.75,
            **settings,
        )
        destination = OUTPUT_DIR / filename
        ta.save(destination, wav, model.sr)
        print(f"Created {destination}")


if __name__ == "__main__":
    main()
