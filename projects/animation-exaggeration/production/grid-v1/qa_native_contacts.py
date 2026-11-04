"""CPU-only A02 still QA from actual preflight PNGs and their diagnostics.

One actual script caption unit per mode is repeated for layout inspection only.
This does not claim speech alignment, final encoded captions, or human listening.
Example: python qa_native_contacts.py --capture-root <preflight/revision>
         --modes normal-and-pause --output <local/grid-v1/qa/fresh-revision>
Use --dry-run to validate inputs without creating artifacts.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import math

from PIL import Image, ImageDraw, ImageFont

H = Path(__file__).resolve().parent
R = H.parents[3]
M = H.parent / "local/grid-v1"
CAPTIONS = H / "caption-units.json"
CAPTION_SELECTION = {
    "normal-and-pause": ("01-p02", 0),
    "size-amplitude": ("02-p02", 2),
    "shoulder-control": ("03-p03", 2),
    "paused-pose-context": ("04-p02", 2),
    "linear-overshoot": ("05-p02", 5),
    "shape-overshoot": ("05-p03", 3),
}
QA_LABEL = "nominal timing, actual script caption text"
FONT = Path("C:/Windows/Fonts/NotoSansKR-VF.ttf")
if not FONT.is_file():
    FONT = Path("C:/Windows/Fonts/malgun.ttf")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text("utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {"path": str(path.resolve()), "sha256": sha(path)}


def font_at(size, weight=500):
    font = ImageFont.truetype(str(FONT), size)
    try:
        axes = font.get_variation_axes()
    except (AttributeError, OSError):
        return font
    if axes:
        values = []
        for axis in axes:
            name = axis.get("name", b"")
            if isinstance(name, bytes):
                name = name.decode("utf-8", "replace")
            values.append(weight if "weight" in name.lower() else axis["default"])
        font.set_variation_by_axes(values)
    return font


def wrap_caption(text, font):
    require(text and "\n" not in text, "Select one unchanged authored clause, not a rewritten caption")
    lines, line = [], ""
    for word in text.split(" "):
        candidate = (line + " " + word).strip()
        if line and font.getlength(candidate) > 1570:
            lines.append(line)
            line = word
        else:
            line = candidate
    lines.append(line)
    require(len(lines) <= 2 and max(font.getlength(line) for line in lines) <= 1570,
            "Actual caption does not fit fixed48px/1570px; do not shrink or truncate")
    return lines


def caption_geometry(text, font):
    lines = wrap_caption(text, font)
    width = math.ceil(max(font.getlength(line) for line in lines)) + 44
    height = len(lines) * 62 + 22
    x, y = round(960 - width / 2), round(970 - height / 2)
    bounds = [x - 3, y - 3, x + width + 17, y + height + 17]
    require(bounds[0] >= 0 and bounds[1] >= 0 and bounds[2] <= 1920 and bounds[3] <= 1080,
            "Fixed caption box including shadow leaves the frame")
    return {"lines": lines, "x": x, "y": y, "width": width, "height": height,
            "completeBounds": bounds, "center": [960, 970], "fontPixels": 48,
            "lineHeight": 62, "padding": [22, 11], "shadowOffset": [14, 14]}


def captioned_frame(source, geometry, font):
    require(source.size == (1920, 1080), "Input must be the actual1920x1080 capture")
    image = source.convert("RGB").copy()
    draw = ImageDraw.Draw(image)
    x, y, width, height = (geometry[key] for key in ("x", "y", "width", "height"))
    draw.rectangle((x + 14, y + 14, x + width + 14, y + height + 14), fill="#073c32")
    draw.rectangle((x - 3, y - 3, x + width + 3, y + height + 3), fill="#161b18")
    draw.rectangle((x, y, x + width, y + height), fill="#ffffff")
    for index, line in enumerate(geometry["lines"]):
        draw.text((960, y + 42 + index * 62), line, font=font, anchor="mm", fill="#080b09")
    return image


def diagnostic_lines(diagnostic, frame):
    lines = [f"f{frame:05d} | phase {diagnostic['phase']} | t={diagnostic['time']:.4f}s"]
    if diagnostic.get("clipLength", 0) > 0:
        lines.append(f"clip {diagnostic['clipSeconds']:.5f}/{diagnostic['clipLength']:.5f}s")
        sizes = diagnostic.get("orthographicSizes", [])
        lines.append("ortho: " + ", ".join(f"{value:.5f}" for value in sizes)
                     + f" | actual RT: {diagnostic.get('createdPanelTextures')}")
    elif diagnostic["mode"] == "linear-overshoot":
        lines.append(f"metres B/O: {diagnostic['baselineMetres']:.5f}/{diagnostic['overshootMetres']:.5f}")
    elif diagnostic["mode"] == "shape-overshoot":
        lines.append(f"radius B/O: {diagnostic['baselineRadius']:.5f}/{diagnostic['overshootRadius']:.5f}")
    for arm in diagnostic.get("arms", []):
        lines.append(f"{arm['side']}: endpoint error {arm['endpointError']:.6g}")
    return lines


def collect(capture_root, modes):
    captions = read(CAPTIONS)
    require(captions.get("slug") == "animation-exaggeration", "Caption source is not A02")
    for source in captions.get("scriptInputs", []):
        require(sha(R / source["path"]) == source["sha256"],
                "Actual caption source changed since its clause binding: " + source["path"])
    records, mode_inputs = [], []
    for mode in modes:
        directory = capture_root / mode
        request_path, success_path = directory / "request.json", directory / "preflight-success.json"
        request, success = read(request_path), read(success_path)
        require(request.get("stageClass") == "AnimationExaggerationStage"
                and request.get("slug") == "animation-exaggeration" and request.get("cutId") == mode,
                "Unexpected preflight identity: " + mode)
        fingerprint = request["expectedFingerprint"]
        require(success.get("status") == "complete" and success.get("compiledSourceFingerprint") == fingerprint
                and success.get("completed") == len(request["sampleFrames"]),
                "Preflight is incomplete or source identity differs: " + mode)
        reopen_path = directory / "scene-reopen-evidence.json"
        reopen = read(reopen_path)
        require(reopen.get("sourceFingerprint") == fingerprint, "Reopen evidence fingerprint differs")
        paragraph, unit_index = CAPTION_SELECTION[mode]
        unit = captions["paragraphs"][paragraph]["captionUnits"][unit_index]
        require(unit.get("ko") and unit.get("en"), "Selected actual paired caption is missing")
        mode_inputs.append({"mode": mode, "request": artifact(request_path), "success": artifact(success_path),
                            "reopenEvidence": artifact(reopen_path), "reopenObserved": reopen,
                            "captionParagraph": paragraph, "captionUnitIndex": unit_index,
                            "captionUnit": unit, "sourceFingerprint": fingerprint})
        for frame in request["sampleFrames"]:
            image_path = directory / f"frame-{frame:05d}.png"
            diagnostic_path = directory / f"a02-{frame:05d}.json"
            diagnostic = read(diagnostic_path)
            require(diagnostic.get("mode") == mode and diagnostic.get("sourceFingerprint") == fingerprint
                    and diagnostic.get("profileId") == request.get("presentationId"),
                    "Frame diagnostic identity differs: " + str(diagnostic_path))
            require(abs(diagnostic["time"] - frame / 60) < .002, "Frame diagnostic time differs")
            with Image.open(image_path) as image:
                require(image.size == (1920, 1080), "Actual capture is not FHD: " + str(image_path))
                image.verify()
            records.append({"mode": mode, "frame": frame, "sourceImage": artifact(image_path),
                            "diagnosticFile": artifact(diagnostic_path), "diagnostic": diagnostic,
                            "captionParagraph": paragraph, "captionUnitIndex": unit_index,
                            "captionText": unit["ko"], "captionTextEnglish": unit["en"]})
    return records, mode_inputs


def contact_page(records, output, name):
    columns, cell_width, cell_height, gap, top = 3, 375, 327, 14, 66
    rows = math.ceil(len(records) / columns)
    sheet = Image.new("RGB", (columns * cell_width + (columns + 1) * gap,
                              top + rows * (cell_height + gap)), "#101214")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 9), QA_LABEL, font=font_at(22), fill="#e8cf83")
    draw.text((gap, 39), "Actual capture pixels + declared caption geometry. Still QA only; no listening claim.",
              font=font_at(14), fill="#f5f5f5")
    for index, record in enumerate(records):
        x, y = gap + index % columns * (cell_width + gap), top + index // columns * (cell_height + gap)
        draw.text((x, y), record["mode"], font=font_at(14), fill="#e8cf83")
        with Image.open(record["mobile375"]["path"]) as image:
            sheet.paste(image, (x, y + 24))
        for line_index, line in enumerate(diagnostic_lines(record["diagnostic"], record["frame"])):
            draw.text((x, y + 242 + line_index * 16), line, font=font_at(12), fill="#f5f5f5")
    destination = output / name
    sheet.save(destination)
    return artifact(destination)


def generate(records, mode_inputs, output):
    require(not output.exists(), "Prior QA artifacts preserved; choose a fresh output directory")
    output.mkdir(parents=True)
    font = font_at(48)
    for record in records:
        mode, frame = record["mode"], record["frame"]
        geometry = caption_geometry(record["captionText"], font)
        for subdir in ("caption-layout-fhd", "mobile-375"):
            (output / subdir / mode).mkdir(parents=True, exist_ok=True)
        full = output / "caption-layout-fhd" / mode / f"frame-{frame:05d}.png"
        mobile = output / "mobile-375" / mode / f"frame-{frame:05d}.png"
        with Image.open(record["sourceImage"]["path"]) as source:
            image = captioned_frame(source, geometry, font)
            image.save(full)
            image.resize((375, 211), Image.Resampling.LANCZOS).save(mobile)
        record.update({"captionGeometry": geometry, "captionLayoutFhd": artifact(full),
                       "mobile375": artifact(mobile)})
    sheets = []
    for mode in CAPTION_SELECTION:
        selected = [record for record in records if record["mode"] == mode]
        for start in range(0, len(selected), 12):
            sheets.append(contact_page(selected[start:start + 12], output,
                                       f"{mode}-contact-{start // 12 + 1:02d}.png"))
    result = {"label": QA_LABEL, "episode": "A02", "kind": "actual-native-capture-still-layout-QA",
              "captionSource": artifact(CAPTIONS), "helper": artifact(Path(__file__)),
              "font": artifact(FONT), "modeInputs": mode_inputs, "frames": records, "contacts": sheets,
              "captionRasterizer": "Pillow geometry preview; final libass encoded pixels are not claimed",
              "mobileTransform": "Actual full FHD PNG + one unchanged clause at960,970/48px ->375x211 Lanczos",
              "nominalTiming": True, "speechAlignmentVerified": False, "humanListeningPerformed": False,
              "humanReview": False, "movingPlaybackVerified": False,
              "limitations": "Sparse still frames cannot certify motion, all-frame occlusion, speech pace, final caption timing or audio."}
    (output / "qa-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page = ['<!doctype html><meta charset="utf-8"><title>A02 native still QA</title>',
            '<style>body{background:#101214;color:#f5f5f5;font-family:sans-serif;margin:24px}img{max-width:100%}a{color:#86cfa3}</style>',
            '<h1>' + html.escape(QA_LABEL) + '</h1>',
            '<p>실제 캡처 PNG와 진단을 연결한 정지 화면 검수입니다. 자막은 실제 대본의 한 절이며 발화 시간은 연결하지 않았습니다. 사람 청취·움직임·최종 자막 검수는 포함하지 않습니다.</p>',
            '<p><a href="qa-manifest.json">Sources, hashes and actual diagnostic values</a></p>']
    for sheet in sheets:
        filename = Path(sheet["path"]).name
        page.append('<p><a href="' + html.escape(filename) + '"><img src="' + html.escape(filename) + '"></a></p>')
    (output / "index.html").write_text("\n".join(page) + "\n", encoding="utf-8")
    return {"output": str(output), "frames": len(records), "contactPages": len(sheets),
            "manifest": str(output / "qa-manifest.json"), "humanListeningPerformed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-root", required=True, type=Path)
    parser.add_argument("--modes", nargs="+", choices=tuple(CAPTION_SELECTION), default=list(CAPTION_SELECTION))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    capture_root = args.capture_root.resolve()
    require(capture_root.is_relative_to((M / "preflight").resolve()), "Read only A02 preflight media")
    records, modes = collect(capture_root, list(dict.fromkeys(args.modes)))
    for mode in modes:
        caption_geometry(mode["captionUnit"]["ko"], font_at(48))
    if args.dry_run:
        print(json.dumps({"validated": True, "modes": [mode["mode"] for mode in modes],
                          "actualFrames": len(records), "writes": 0, "humanListeningPerformed": False}))
        return
    require(args.output is not None, "Choose an explicit fresh --output under A02 local/grid-v1/qa")
    output = args.output.resolve()
    require(output.is_relative_to((M / "qa").resolve()) and output != (M / "qa").resolve(),
            "Write only a fresh directory under A02 local/grid-v1/qa")
    print(json.dumps(generate(records, modes, output), ensure_ascii=False))


if __name__ == "__main__":
    main()
