"""Create a timing draft from the measured balanced voice sample."""

from __future__ import annotations

import json
from pathlib import Path

import soundfile as sf

from render_narration_and_srt import format_timestamp, wrap_caption


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "projects" / "jump-physics" / "script" / "narration.ko.json"
SAMPLE_PATH = ROOT / "shared" / "audio-samples" / "jump-physics" / "02-balanced.wav"
OUTPUT_PATH = ROOT / "shared" / "output" / "narration" / "jump-physics-balanced-draft.srt"
SAMPLE_TEXT = (
    "캐릭터가 점프하는 건 단순해 보이지만, 매 프레임 적용되는 중력이 "
    "점프의 감각을 바꿉니다. 속도 5로 시작해도 중력이 계속 더해지면, "
    "최고점 이후 아래로 점점 빠르게 떨어집니다."
)
GAP_SECONDS = 0.22


def spoken_chars(text: str) -> int:
    return len(text.replace(" ", "").replace("\n", ""))


def main() -> None:
    script = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    sample_info = sf.info(SAMPLE_PATH)
    seconds_per_char = sample_info.duration / spoken_chars(SAMPLE_TEXT)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cursor = 0.0
    index = 1
    with OUTPUT_PATH.open("w", encoding="utf-8") as srt:
        for scene in script["scenes"]:
            for line in scene["lines"]:
                duration = spoken_chars(line) * seconds_per_char
                srt.write(
                    f"{index}\n{format_timestamp(cursor)} --> "
                    f"{format_timestamp(cursor + duration)}\n{wrap_caption(line)}\n\n"
                )
                cursor += duration + GAP_SECONDS
                index += 1

    print(f"Created {OUTPUT_PATH}")
    print(f"Estimated narration length: {cursor:.1f}s")


if __name__ == "__main__":
    main()
