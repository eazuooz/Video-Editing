"""Finish the approved-format revision while preserving captions across color metadata changes."""
from pathlib import Path

import render_established_format_v6 as film

original_ffmpeg = film.edit.ffmpeg


def encode_with_continuous_captions(*args):
    if any(str(value).endswith("caption-overlays.ffconcat") for value in args):
        return original_ffmpeg("-reinit_filter", 0, *args)
    return original_ffmpeg(*args)


if __name__ == "__main__":
    film.edit.ffmpeg = encode_with_continuous_captions
    film.main()
    pilot = "--pilot" in __import__("sys").argv
    output = film.WORK / "pilot" if pilot else film.OUT
    audit = film.read(output / "audit.json")
    audit["captionContinuityFix"] = {
        "path": str(Path(__file__).resolve()),
        "sha256": film.sha(Path(__file__)),
        "inputColorMetadataTransition": "Preserve the subtitle overlay timeline when the main input changes color metadata.",
        "verification": "Per-cue encoded pixel checks and whole-word boundary frame checks",
    }
    film.save(output / "audit.json", audit)
