"""Stage the final Unity build for a static host with a per-file size limit."""

import argparse
import hashlib
import json
from pathlib import Path
from shutil import copy2, copytree


PART_BYTES = 22 * 1024 * 1024
DATA_FILE = "webgl.data.unityweb"


def stage_web_build(source: Path, destination: Path) -> None:
    config_path = source / "build-config.js"
    config = json.loads(config_path.read_text(encoding="utf-8").removeprefix("const LOFI_BUILD=").strip().removesuffix(";"))
    unity_data = source / "Build" / DATA_FILE
    with unity_data.open("rb") as original:
        data_sha256 = hashlib.file_digest(original, "sha256").hexdigest()
    build_key = data_sha256[:16]

    copytree(source, destination, ignore=lambda path, names: {DATA_FILE} if Path(path) == unity_data.parent else set())
    build_dir = destination / "Build"
    parts = []
    with unity_data.open("rb") as original:
        for index, data in enumerate(iter(lambda: original.read(PART_BYTES), b"")):
            name = f"room-data-{build_key}-{index:02}.bin"
            (build_dir / name).write_bytes(data)
            parts.append({"url": f"Build/{name}", "bytes": len(data)})
    assert sum(part["bytes"] for part in parts) == unity_data.stat().st_size
    del config["config"]["dataUrl"]
    config["dataParts"] = parts
    (destination / config_path.name).write_text("const LOFI_BUILD=" + json.dumps(config) + ";\n", encoding="utf-8")

    room_js = destination / "room.js"
    room = room_js.read_text(encoding="utf-8")
    marker = "const script=document.createElement('script');"
    original_ui, separator, _ = room.partition(marker)
    if not separator:
        raise ValueError("Unable to find the Unity boot code in the input build")
    boot = Path(__file__).with_name("public-web-bootstrap.js")
    room_js.write_text(original_ui + boot.read_text(encoding="utf-8"), encoding="utf-8")

    page = destination / "index.html"
    html = page.read_text(encoding="utf-8")
    for asset in ("room.js", "build-config.js"):
        start = html.index(f'src="{asset}?')
        end = html.index('"', start + len('src="'))
        cache_key = hashlib.sha256((destination / asset).read_bytes()).hexdigest()[:16]
        html = html[:start] + f'src="{asset}?v={cache_key}' + html[end:]
    page.write_text(html, encoding="utf-8")

    credits = destination / "credits.html"
    credits.write_text(
        credits.read_text(encoding="utf-8").replace(
            "현 버전은 로컬 검수용입니다.", "이 버전은 브라우저에서 바로 실행할 수 있습니다."
        ),
        encoding="utf-8",
    )
    print(json.dumps({"dataSha256": data_sha256, "partCount": len(parts), "parts": parts}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    stage_web_build(args.source.resolve(), args.destination.resolve())
