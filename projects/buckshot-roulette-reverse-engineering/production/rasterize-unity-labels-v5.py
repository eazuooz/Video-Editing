"""Deterministic white RGBA labels for the isolated Buckshot Unity scenes.

Adapted from the repository's verified BOTW label-rasterization path. Only glyph
images are written; the installed font binary is read for rendering and provenance,
never copied. Unity retains editable Text values and tints the imported textures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = Path("C:/Windows/Fonts/malgun.ttf")
SCHEMA = "buckshot-label-rgba-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label_key(spec: dict, font_sha: str) -> str:
    value = "\n".join(
        [SCHEMA, font_sha, spec["text"], str(spec["size"]),
         str(spec["width"]), str(spec["height"]), spec["alignment"]]
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text("utf-8-sig"))
    project = Path(__file__).resolve().parents[1]
    allowed = (project / "production/local/unity-v5/label-cache").resolve()
    output = args.output.resolve()
    if output != allowed:
        raise ValueError(f"Label output outside this project's cache: {output}")
    if not args.request.resolve().is_relative_to(allowed):
        raise ValueError("Label request is outside the cache")
    output.mkdir(parents=True, exist_ok=True)
    font_sha = digest(FONT)
    if request["fontSha256"].lower() != font_sha:
        raise ValueError("Installed font changed since Unity prepared the request")
    scale = 2
    fonts: dict[int, ImageFont.FreeTypeFont] = {}
    records = []
    created = 0
    for spec in request["specs"]:
        text = spec["text"]
        if not text:
            raise ValueError("Empty labels must not be rasterized")
        size, width, height = (int(spec[k]) for k in ("size", "width", "height"))
        align = spec["alignment"]
        if not (1 <= size <= 128 and 1 <= width <= 4096 and 1 <= height <= 512):
            raise ValueError(f"Unexpected label dimensions: {spec}")
        if align not in ("left", "center", "right"):
            raise ValueError(f"Unknown alignment: {align}")
        key = label_key(spec, font_sha)
        if key != spec["key"]:
            raise ValueError("Unity/Python label keys disagree")
        target = output / f"{key}.png"
        fonts.setdefault(size, ImageFont.truetype(str(FONT), size * scale))
        font = fonts[size]
        image = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for character in paragraph:
                if line and draw.textlength(line + character, font=font) > width * scale - 4:
                    lines.append(line.rstrip())
                    line = character.lstrip()
                else:
                    line += character
            lines.append(line)
        content = "\n".join(lines)
        bounds = draw.multiline_textbbox((0, 0), content, font=font, spacing=2 * scale, align=align)
        ink_width, ink_height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        if len(lines) > 2 or ink_height > height * scale - 2:
            raise ValueError(f"Actual label does not fit {width}x{height}/{size}: {text!r}")
        if align == "left":
            x = 2 - bounds[0]
        elif align == "right":
            x = width * scale - ink_width - 2 - bounds[0]
        else:
            x = (width * scale - ink_width) / 2 - bounds[0]
        y = (height * scale - ink_height) / 2 - bounds[1]
        draw.multiline_text((x, y), content, font=font, fill=(255, 255, 255, 255), spacing=2 * scale, align=align)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        if target.exists():
            with Image.open(target) as existing:
                if existing.size != image.size or existing.convert("RGBA").tobytes() != image.tobytes():
                    raise ValueError(f"Existing bitmap differs for the same immutable key: {key}")
        else:
            image.save(target)
            created += 1
        records.append({**spec, "path": str(target), "pngSha256": digest(target), "lines": len(lines)})
    receipt = {
        "schema": SCHEMA,
        "mode": request["mode"],
        "fontFile": str(FONT),
        "fontSha256": font_sha,
        "fontFamily": "Malgun Gothic",
        "fontStyle": "regular",
        "fontBinaryCopied": False,
        "whiteTextTintedAtRuntime": True,
        "verticalAlignment": "middle",
        "antialiasScale": scale,
        "stageSourceSha256": request["stageSourceSha256"],
        "generatorSha256": digest(Path(__file__)),
        "requestSha256": digest(args.request),
        "created": created,
        "count": len(records),
        "records": records,
    }
    receipt_path = output / (request["mode"] + "-" + receipt["requestSha256"] + ".receipt.json")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({"receipt": str(receipt_path), "created": created, "count": len(records), "fontSha256": font_sha}))


if __name__ == "__main__":
    main()
