"""Create short Korean voice-cloning samples through the official HF demo.

This sends the local reference WAV and the sample text to:
https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS
"""

from pathlib import Path
from shutil import copy2

from gradio_client import Client, handle_file


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
OUTPUT_DIR = ROOT / "shared" / "audio-samples" / "jump-physics"

TEXT = (
    "캐릭터가 점프하는 건 단순해 보이지만, 매 프레임 적용되는 중력이 "
    "점프의 감각을 바꿉니다. 속도 5로 시작해도 중력이 계속 더해지면, "
    "최고점 이후 아래로 점점 빠르게 떨어집니다."
)

TONES = {
    "01-calm.wav": {"exaggeration_input": 0.30, "temperature_input": 0.60, "cfgw_input": 0.65},
    "02-balanced.wav": {"exaggeration_input": 0.50, "temperature_input": 0.70, "cfgw_input": 0.50},
    "03-brisk.wav": {"exaggeration_input": 0.80, "temperature_input": 0.80, "cfgw_input": 0.35},
}


def main() -> None:
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing reference audio: {REFERENCE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = Client("ResembleAI/Chatterbox-Multilingual-TTS")

    for filename, settings in TONES.items():
        generated_path = client.predict(
            text_input=TEXT,
            language_id="ko",
            audio_prompt_path_input=handle_file(REFERENCE),
            seed_num_input=240726,
            api_name="/generate_tts_audio",
            **settings,
        )
        destination = OUTPUT_DIR / filename
        copy2(generated_path, destination)
        print(f"Created {destination}")


if __name__ == "__main__":
    main()
