"""Prepare an eight-kind, current-timing visual layout diagnostic; never render.

--dry-run validates current D21v3 inputs without writing. --prepare writes only
eight preflight-{kind}.tsx modules, preflight-project.ts, a clipped/retimed copy
of the current KO ASS, and local/v3/preflight-spec.json. Each section is the
middle <=120 frames of the longest actual explanation cut for that kind.

This is a silent layout diagnostic, not new narration or whole-video approval.
The shorter lesson duration can change duration-relative animation speeds; it
does not claim decoded-pixel equivalence to cropping the production render.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = ROOT / "projects/player-customization"
LOCAL = PROJECT / "production/local/reference-preserving-v3"
EDIT = LOCAL / "edit"
MC = ROOT / "motion-canvas/src/projects/player-customization/revision-v3"
PLAN = HERE / "edit-plan.json"
LAYOUT = EDIT / "caption-layout.json"
ASS = EDIT / "captions.ko.ass"
SPEC = LOCAL / "preflight-spec.json"
SAMPLE_ASS = LOCAL / "preflight/captions.ko.ass"
SLUG, REVISION, FPS = "player-customization", "reference-preserving-v3", 60
KINDS = ("overview", "effects", "tradeoffs", "find", "auto", "test", "appearance", "conclusion")
COUNTS = dict(zip(KINDS, (3, 5, 5, 5, 4, 5, 4, 4)))
GAMES = {"Splatoon Raiders", "The Legend of Zelda: Breath of the Wild", "Animal Crossing: New Horizons"}
MARKER = "// Generated D21v3 silent visual preflight; never a production module.\n"
ASS_FORMAT = "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def document(path):
    return json.loads(read(path))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()


def receipt(path):
    path = Path(path)
    return dict(path=rel(path), sha256=sha(path), bytes=path.stat().st_size)


def scope(path, owner):
    path = Path(path).resolve()
    path.relative_to(Path(owner).resolve())
    return path


def guard():
    """Only read global selection; a sibling production is never resumed."""
    auth_path = scope(HERE / "authorization.json", HERE)
    control_path = ROOT / "shared/publishing/video-production-control.json"
    auth, control = document(auth_path), document(control_path)
    require((auth.get("slug"), auth.get("revision")) == (SLUG, REVISION), "Wrong D21 authorization")
    require(auth.get("fullProductionAuthorized") is True and auth.get("automaticNextVideo") is False,
            "Current one-video production authorization is required")
    require(set(auth.get("selectedGameTitles", [])) == GAMES, "Current selected titles changed")
    return dict(authorization=receipt(auth_path), control=receipt(control_path),
                globalSelectionObservedOnly=control.get("selectedVideo"), foreignStateWritten=False)


def ass_time(value):
    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2})\.(\d{2})", value.strip())
    require(match is not None, "ASS times must use the current centisecond format")
    h, m, s, cs = map(int, match.groups())
    require(m < 60 and s < 60, "Invalid ASS time")
    return Fraction(((h * 60 + m) * 60 + s) * 100 + cs, 100)


def centiseconds(value):
    """Nonnegative nearest-centisecond, half up; geometry/text are untouched."""
    value = Fraction(value)
    require(value >= 0, "Negative diagnostic caption time")
    n, d = value.numerator * 100, value.denominator
    return (2 * n + d) // (2 * d)


def ass_stamp(value):
    n = centiseconds(value)
    return f"{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}"


def parse_ass(original):
    """Keep the complete original prefix verbatim, including styles/geometry."""
    lines = original.splitlines(keepends=True)
    first = next((i for i, line in enumerate(lines) if line.startswith("Dialogue:")), None)
    require(first is not None, "Current ASS has no Dialogue")
    header = "".join(lines[:first])
    require("PlayResX: 1920" in header and "PlayResY: 1080" in header
            and ASS_FORMAT in header, "Unexpected ASS resolution/event-field order")
    events = []
    for line in lines[first:]:
        if not line.strip():
            continue
        require(line.startswith("Dialogue: "), "Unexpected non-Dialogue content after ASS header")
        fields = line.rstrip("\r\n")[len("Dialogue: "):].split(",", 9)
        require(len(fields) == 10, "Malformed current ASS Dialogue")
        start, end = ass_time(fields[1]), ass_time(fields[2])
        require(end > start, "Nonpositive current ASS event")
        events.append(dict(fields=fields, start=start, end=end))
    return header, events


def validate_captions(layout, header, events, plan):
    require(layout.get("style") == "boxed-white-forest-v1"
            and layout.get("fixedCenter") == [960, 970]
            and layout.get("fontSize") == 48 and layout.get("maxLines") == 2,
            "Use the current fixed-position48px/two-line caption layout")
    rows = layout.get("rows")
    require(isinstance(rows, list) and rows, "Current caption layout is empty")
    grouped = {}
    for event in events:
        grouped.setdefault((event["start"], event["end"]), []).append(event["fields"])
    expected_keys = set()
    previous_end = Fraction(0)
    for row in rows:
        start, end = Fraction(str(row["start"])), Fraction(str(row["end"]))
        require(start >= previous_end and end > start
                and 2 <= start < end <= Fraction(plan["brandingFrames"] + plan["bodyFrames"], FPS),
                "Caption row ordering/body clock differs from current plan")
        previous_end = end
        key = (Fraction(centiseconds(start), 100), Fraction(centiseconds(end), 100))
        require(key not in expected_keys, "Duplicate caption interval")
        expected_keys.add(key)
        fields = grouped.get(key, [])
        expected = row.get("lines", row["ko"].split("\n"))
        require(1 <= len(expected) <= 2 and row["ko"].split("\n") == expected,
                f"Caption text/line layout differs: cue{row['cue']}")
        text = [re.sub(r"\{[^}]*\}", "", f[9]) for f in fields if f[0] == "2"]
        require(text == expected and len(fields) == len(expected) + 2
                and sorted(f[0] for f in fields) == ["0", "1"] + ["2"] * len(expected),
                f"Current ASS and caption-layout disagree: cue{row['cue']}")
        require(row.get("scene") in {f"{i:02}" for i in range(1, 9)}, "Foreign caption scene")
    require(set(grouped) == expected_keys, "ASS contains missing or foreign layout intervals")
    return rows


def choose_sections(plan):
    sections, cursor = [], 0
    by_scene = {s["id"]: s for s in plan["scenes"]}
    require(list(by_scene) == [f"{i:02}" for i in range(1, 9)], "Current eight-scene order required")
    for index, kind in enumerate(KINDS, 1):
        matches = [cut for cut in plan["cuts"] if cut.get("kind") == "explanation"
                   and cut.get("visual") == kind and cut.get("scene") == f"{index:02}"]
        require(matches, f"No actual explanation cut for {kind}; do not fabricate a timing")
        cut = min(matches, key=lambda c: (-int(c["frames"]), int(c["startFrame"])))
        start, end, frames = (cut[k] for k in ("startFrame", "endFrame", "frames"))
        require(all(isinstance(v, int) for v in (start, end, frames))
                and end - start == frames and frames > 0, f"Invalid cut frames: {cut['id']}")
        take = min(120, frames)
        offset = (frames - take) // 2
        lo, hi = start + offset, start + offset + take
        cues = cut.get("cues")
        require(isinstance(cues, list) and len(cues) == COUNTS[kind]
                and all(isinstance(v, (int, float)) and math.isfinite(v) for v in cues),
                f"Missing current measured paragraph cues: {cut['id']}")
        row = by_scene[cut["scene"]]
        expected = [float(t) - (start / FPS - float(row["voiceStart"]))
                    for t in row["paragraphStarts"]]
        require(len(expected) == len(cues) and all(abs(a-b) < 1e-7 for a, b in zip(cues, expected)),
                f"Cut cues and measured scene clock disagree: {cut['id']}")
        require(isinstance(cut.get("credit"), str) and cut["credit"], f"Current credit missing: {cut['id']}")
        shifted = [float(t) - offset / FPS for t in cues]  # Negative starts intentionally retained.
        sections.append(dict(kind=kind, scene=cut["scene"], cutId=cut["id"],
            productionCutStartFrame=start, productionCutEndFrame=end,
            globalStartFrame=lo, globalEndFrame=hi, sampleOffsetWithinCutFrames=offset,
            sampleStartFrame=cursor, sampleEndFrame=cursor+take, frames=take,
            productionCues=cues, shiftedCues=shifted, credit=cut["credit"],
            payload=dict(duration=(take-.75)/FPS, cues=shifted, credit=cut["credit"]),
            selectionRule="Longest actual explanation cut of this kind; earliest tie; centered <=120-frame window"))
        cursor += take
    require(cursor <= 960, "Eight-kind preflight may not exceed16seconds")
    return sections, cursor


def clipped_captions(header, events, sections, rows):
    dialogues, mapping = [], []
    for section in sections:
        lo, hi = Fraction(section["globalStartFrame"], FPS), Fraction(section["globalEndFrame"], FPS)
        offset = Fraction(section["sampleStartFrame"], FPS)
        section["captionRows"] = [dict(cue=row["cue"], paragraph=row["paragraph"], ko=row["ko"],
            originalStart=row["start"], originalEnd=row["end"])
            for row in rows if Fraction(str(row["start"])) < hi and Fraction(str(row["end"])) > lo]
        for ordinal, event in enumerate(events):
            start, end = max(lo, event["start"]), min(hi, event["end"])
            if end <= start:
                continue
            fields = list(event["fields"])
            fields[1], fields[2] = ass_stamp(offset+start-lo), ass_stamp(offset+end-lo)
            dropped = fields[1] == fields[2]
            if not dropped:
                dialogues.append("Dialogue: " + ",".join(fields) + "\n")
            mapping.append(dict(kind=section["kind"], originalDialogueIndex=ordinal,
                layer=fields[0], originalStart=str(event["start"]), originalEnd=str(event["end"]),
                sampleStart=fields[1], sampleEnd=fields[2],
                clippedAtStart=event["start"] < lo, clippedAtEnd=event["end"] > hi,
                unchangedNonTimeFields=True, droppedOnlyAfterCentisecondCollapse=dropped))
    return header + "".join(dialogues), mapping


def prepare_state():
    auth = guard()
    for path, owner in ((PLAN, HERE), (LAYOUT, EDIT), (ASS, EDIT), (MC / "visuals.tsx", MC)):
        scope(path, owner)
        require(path.is_file(), f"Current input is not ready: {rel(path)}")
    plan, layout = document(PLAN), document(LAYOUT)
    require((plan.get("slug"), plan.get("revision")) == (SLUG, REVISION), "Foreign/stale edit plan")
    require((plan.get("width"), plan.get("height"), plan.get("fps")) == (1920, 1080, FPS)
            and plan.get("brandingFrames") == 120 and plan.get("outroFrames") == 600,
            "Expected current FHD60/2s-branding/10s-membership clock")
    require(scope(ROOT / plan["outputDir"], LOCAL) == EDIT.resolve(), "Foreign edit output directory")
    title_path, source_path, asset_path = (HERE / n for n in ("title-selection.json", "source-selection.json", "visual-assets.json"))
    require(set(document(title_path).get("selectedTitles", [])) == GAMES, "Title selection changed")
    inputs = [receipt(path) for path in (PLAN, LAYOUT, ASS, title_path, source_path, asset_path,
                                        MC / "visuals.tsx", Path(__file__))]
    pinned = {row["path"]: row["sha256"] for row in plan.get("inputs", [])}
    require(pinned.get(rel(source_path)) == sha(source_path), "Edit plan does not pin current source selection")
    assets = document(asset_path)
    require((assets.get("slug"), assets.get("revision")) == (SLUG, REVISION)
            and len(assets.get("assets", [])) == 8, "Current prepared eight-still registry required")
    for asset in assets["assets"]:
        served = scope(ROOT / asset["rendererImage"], ROOT / "output/player-customization/preproduction-assets-v3")
        require(sha(served) == asset["sha256"], f"Renderer still changed: {asset['id']}")
        inputs.append(receipt(served))
    # Read bytes to avoid newline/BOM normalization of the retained ASS header.
    header, events = parse_ass(ASS.read_bytes().decode("utf-8"))
    rows = validate_captions(layout, header, events, plan)
    sections, frames = choose_sections(plan)
    captions, mapping = clipped_captions(header, events, sections, rows)
    files, imports = {}, []
    for i, section in enumerate(sections):
        name = "preflight-" + section["kind"]
        files[MC / (name + ".tsx")] = (MARKER + "import {makeScene2D} from '@motion-canvas/2d';\n"
            "import {lesson} from './visuals';\n"
            "export default makeScene2D(function*(view){yield* lesson(view,"
            + json.dumps(section["kind"]) + "," + json.dumps(section["payload"], ensure_ascii=False)
            + ");});\n")
        imports.append(f"import s{i} from './{name}?scene';")
        section["module"] = rel(MC / (name + ".tsx"))
    files[MC / "preflight-project.ts"] = (MARKER + "import {makeProject} from '@motion-canvas/core';\n"
        + "\n".join(imports) + "\nexport default makeProject({scenes:["
        + ",".join(f"s{i}" for i in range(len(sections))) + "]});\n")
    files[SAMPLE_ASS] = captions
    allowed = {MC / ("preflight-" + kind + ".tsx") for kind in KINDS} | {MC / "preflight-project.ts", SAMPLE_ASS}
    require(set(files) == allowed, "Output allowlist changed")
    for path in files:
        scope(path, MC if path.parent == MC else LOCAL / "preflight")
        require(path.resolve() not in {scope(ROOT / item["path"], ROOT) for item in inputs}, "Output aliases an input")
    signature = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    return dict(auth=auth, inputs=inputs, sections=sections, frames=frames, files=files,
                signature=signature, captionEventMapping=mapping,
                assHeaderSha256=hashlib.sha256(header.encode("utf-8")).hexdigest())


def prepare(state):
    for item in state["inputs"]:
        require(sha(ROOT / item["path"]) == item["sha256"], "Input changed during preflight preparation")
    require(guard()["authorization"]["sha256"] == state["auth"]["authorization"]["sha256"], "Authorization changed")
    scope(SPEC, LOCAL)
    for path, content in state["files"].items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != content.encode("utf-8"):
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(content)
    result = dict(schemaVersion=1, slug=SLUG, revision=REVISION,
        updatedAt=datetime.now(timezone.utc).isoformat(), status="prepared-silent-layout-diagnostic; not rendered",
        inputSignature=state["signature"], inputs=state["inputs"], authorization=state["auth"],
        fps=FPS, width=1920, height=1080, totalFrames=state["frames"], durationSeconds=state["frames"]/FPS,
        sections=state["sections"], preparedOutputs=[receipt(path) for path in state["files"]],
        captionEventMapping=state["captionEventMapping"], originalAssHeaderSha256=state["assHeaderSha256"],
        captionRule="Original ASS header, layers, complete non-time fields, box geometry and Korean text preserved; interval intersection, shift and centisecond rounding only.",
        cueRule="Original production-cut cues minus the within-cut sample offset; negative cues retained.",
        project="/src/projects/player-customization/revision-v3/preflight-project.ts",
        frameConvention="Each lesson endpoint=(sectionFrames-.75)/60, matching current production convention; actual rendered frame count still requires verification.",
        audio=dict(enabled=False, newNarration=False, sourcePcmTouched=False),
        diagnosticLimits=["Eight short layout excerpts only; no whole-video or full-cue approval.",
            "Shorter lesson duration changes duration-relative motionScale; not decoded-pixel-equivalent production crops.",
            "Cuts/captions may start or end within a sentence; the original ASS and narration are unchanged."],
        actual1080PixelReview="pending", mobile375PixelReview="pending", movingWholeCutSynchronization="pending",
        renderedFrameVerification="pending", humanListening="not performed; this diagnostic has no audio",
        wholeMovieApproved=False, mediaJobsStarted=0, productionModulesModified=False,
        originalCaptionFilesModified=False, foreignFilesOrProcessesChanged=False)
    SPEC.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dict(status=result["status"], receipt=receipt(SPEC), frames=state["frames"],
                seconds=state["frames"]/FPS, mediaJobsStarted=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Validate current inputs; no writes or media jobs")
    mode.add_argument("--prepare", action="store_true", help="Write only scoped diagnostic TSX/project/ASS/spec files; never render")
    args = parser.parse_args()
    try:
        state = prepare_state()
        result = prepare(state) if args.prepare else dict(status="dry-run; no writes or media jobs",
            inputSignature=state["signature"], frames=state["frames"], sections=[dict(kind=s["kind"], cut=s["cutId"],
                globalStartFrame=s["globalStartFrame"], globalEndFrame=s["globalEndFrame"], frames=s["frames"])
                for s in state["sections"]])
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"D21 visual preflight not prepared: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
