"""Transcribe local reference or rendered audio for narration QA.

Qwen3-TTS can clone from an audio-only speaker vector, but supplying the exact
reference transcript preserves more of the speaker's prosody and timbre.  This
helper keeps that preparation and final read-back step local and repeatable.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional UTF-8 text file for the transcript",
    )
    parser.add_argument(
        "--model",
        default="openai/whisper-large-v3-turbo",
        help="Hugging Face Whisper model id",
    )
    parser.add_argument("--language", default="korean")
    args = parser.parse_args()

    audio = args.audio.resolve()
    if not audio.exists():
        raise FileNotFoundError(audio)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        args.model,
        dtype=dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    ).to(device)
    processor = AutoProcessor.from_pretrained(args.model)
    transcriber = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        dtype=dtype,
        device=device,
    )
    result = transcriber(
        str(audio),
        generate_kwargs={"language": args.language, "task": "transcribe"},
        return_timestamps=True,
    )
    transcript = str(result["text"]).strip()
    print(transcript)
    if args.output is not None:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(transcript + "\n", encoding="utf-8")
        print(f"Created {output}")


if __name__ == "__main__":
    main()
