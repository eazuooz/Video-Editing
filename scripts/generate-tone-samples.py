"""Generate Korean TTS pacing samples for the Jump Physics video.

Requires: pip install edge-tts
Outputs: shared/audio-samples/*.mp3
"""

import asyncio
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "shared" / "audio-samples"
VOICE = "ko-KR-SunHiNeural"

SCRIPT = (
    "캐릭터가 점프하는 것은 매우 단순한 액션처럼 보이지만, "
    "여기에도 여러 가지 고려해야 할 점이 있습니다.\n\n"
    "처음에 위쪽으로 속도 5를 준 뒤, 공중에 있는 동안 매 프레임마다 "
    "1만큼의 낙하 가속도를 적용한다고 해 봅시다.\n\n"
    "속도는 5에서 4, 3, 2처럼 줄어들고, 0이 된 뒤에는 "
    "아래쪽으로 점점 빠르게 떨어집니다."
)

SAMPLES = {
    "01-calm.mp3": "-15%",
    "02-balanced.mp3": "+0%",
    "03-brisk.mp3": "+15%",
}


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, rate in SAMPLES.items():
        communicator = edge_tts.Communicate(SCRIPT, VOICE, rate=rate)
        await communicator.save(OUTPUT_DIR / filename)
        print(f"Generated {filename} ({rate})")


if __name__ == "__main__":
    asyncio.run(main())
