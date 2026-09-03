"""Build readable project SRT files from measured narration timings."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def repo_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    path.relative_to(ROOT.resolve())
    return path


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1_000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def wrapped_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def split_caption(text: str, width: int, max_lines: int = 2) -> list[str]:
    """Split a narration line into balanced captions no taller than max_lines."""
    words = text.split()
    if not words:
        return [""]

    greedy: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(wrapped_lines(candidate, width)) > max_lines:
            greedy.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        greedy.append(" ".join(current))

    chunk_count = len(greedy)
    if chunk_count == 1:
        return greedy

    # Repartition the same words so the final cue is not left as one very short
    # word. Dynamic programming minimizes deviation from equal reading weight.
    prefix = [0]
    for word in words:
        prefix.append(prefix[-1] + weight(word))
    target = prefix[-1] / chunk_count
    infinity = float("inf")
    scores = [[infinity] * (len(words) + 1) for _ in range(chunk_count + 1)]
    previous = [[-1] * (len(words) + 1) for _ in range(chunk_count + 1)]
    scores[0][0] = 0.0

    for used in range(1, chunk_count + 1):
        for end in range(used, len(words) + 1):
            for start in range(used - 1, end):
                if scores[used - 1][start] == infinity:
                    continue
                candidate = " ".join(words[start:end])
                if len(wrapped_lines(candidate, width)) > max_lines:
                    continue
                segment_weight = prefix[end] - prefix[start]
                punctuation_bonus = (
                    -(target**2) * 0.5
                    if candidate.endswith((",", ";", ".", "?", "!"))
                    else 0
                )
                score = (
                    scores[used - 1][start]
                    + (segment_weight - target) ** 2
                    + punctuation_bonus
                )
                if score < scores[used][end]:
                    scores[used][end] = score
                    previous[used][end] = start

    if previous[chunk_count][len(words)] < 0:
        return greedy

    chunks: list[str] = []
    end = len(words)
    for used in range(chunk_count, 0, -1):
        start = previous[used][end]
        chunks.append(" ".join(words[start:end]))
        end = start
    chunks.reverse()
    return chunks


def weight(text: str) -> int:
    return max(1, len("".join(text.split())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    manifest_path = ROOT / "projects" / args.project / "project.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir = repo_path(manifest["tts"]["outputDir"])
    stem = manifest["tts"]["filenameStem"]
    timing = json.loads((output_dir / f"{stem}.timing.json").read_text(encoding="utf-8"))

    translation_path = ROOT / "projects" / args.project / "script" / f"narration.{args.language}.json"
    translation = json.loads(translation_path.read_text(encoding="utf-8"))
    translated_lines = [line for scene in translation["scenes"] for line in scene["lines"]]
    entries = timing["entries"]
    if len(translated_lines) != len(entries):
        raise ValueError(
            f"Translation has {len(translated_lines)} lines, timing has {len(entries)} entries"
        )

    language_settings = {
        "ko": {"output_key": "captionsKo", "width": 32},
        "en": {"output_key": "captionsEn", "width": 46},
    }
    settings = language_settings.get(
        args.language,
        {"output_key": None, "width": 42},
    )
    output_key = settings["output_key"]
    output_path = (
        repo_path(manifest["paths"][output_key])
        if output_key and manifest["paths"].get(output_key)
        else output_dir / f"{stem}.{args.language}.srt"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cues: list[tuple[float, float, str]] = []
    for entry, caption_text in zip(entries, translated_lines):
        chunks = split_caption(caption_text, int(settings["width"]))
        weights = [weight(chunk) for chunk in chunks]
        total_weight = sum(weights)
        entry_start = float(entry["start"])
        entry_end = float(entry["end"])
        span = entry_end - entry_start
        elapsed_weight = 0

        for chunk_index, (chunk, chunk_weight) in enumerate(zip(chunks, weights)):
            chunk_start = entry_start + span * elapsed_weight / total_weight
            elapsed_weight += chunk_weight
            chunk_end = (
                entry_end
                if chunk_index == len(chunks) - 1
                else entry_start + span * elapsed_weight / total_weight
            )
            wrapped = "\n".join(wrapped_lines(chunk, int(settings["width"])))
            cues.append((chunk_start, chunk_end, wrapped))

    blocks = []
    for index, (cue_start, cue_end, wrapped) in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{timestamp(cue_start)} --> "
            f"{timestamp(cue_end)}\n{wrapped}"
        )
    output_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"Created {output_path} ({len(blocks)} entries)")


if __name__ == "__main__":
    main()
