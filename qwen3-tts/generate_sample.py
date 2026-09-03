"""Generate a project-aware local voice-cloning approval sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


ROOT = Path(__file__).resolve().parents[1]


def repo_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    path.relative_to(ROOT.resolve())
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument(
        "--scene",
        help="Narration scene id to use; defaults to the first scene",
    )
    parser.add_argument("--text", help="Optional text override")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest_path = ROOT / "projects" / args.project / "project.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("slug") != args.project:
        raise ValueError("Manifest slug does not match --project")

    tts = manifest["tts"]
    reference = repo_path(tts["reference"])
    reference_text_path = repo_path(tts["referenceText"])
    model_dir = repo_path(tts["model"])
    script_path = repo_path(manifest["paths"]["script"])
    output = (
        args.output.resolve()
        if args.output is not None
        else ROOT
        / "shared"
        / "audio-samples"
        / f"{args.project}-qwen3-1.7b-approval-sample.wav"
    )

    script = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = script["scenes"]
    selected = scenes[0] if args.scene is None else next(
        scene for scene in scenes if str(scene["id"]) == args.scene
    )
    text = args.text or " ".join(
        line.strip() for line in selected["lines"] if line.strip()
    )

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for local Qwen3-TTS inference.")
    for path, label in (
        (reference, "Reference audio"),
        (reference_text_path, "Reference transcript"),
        (model_dir, "Model"),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label} not found: {path}")

    output.parent.mkdir(parents=True, exist_ok=True)
    model = Qwen3TTSModel.from_pretrained(
        str(model_dir),
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    voice_prompt = model.create_voice_clone_prompt(
        ref_audio=str(reference),
        ref_text=reference_text_path.read_text(encoding="utf-8").strip(),
        x_vector_only_mode=False,
    )
    wavs, sample_rate = model.generate_voice_clone(
        text=text,
        language=str(tts.get("language", "Korean")),
        voice_clone_prompt=voice_prompt,
        non_streaming_mode=True,
        max_new_tokens=min(int(tts.get("maxNewTokens", 1024)), 512),
    )
    sf.write(output, wavs[0], sample_rate)
    print(f"Scene: {selected['id']} — {selected['title']}")
    print(f"Created {output}")


if __name__ == "__main__":
    main()
