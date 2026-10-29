"""Propose measured anchors, then lock reviewed BOTW edit/capture timing.

This entry point only writes botw-v4 metadata. It never generates voice, renders,
captures Unity, changes older revisions, or treats provisional phase times as final.
"""
from pathlib import Path
import argparse
import copy
import difflib
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
REVISION = "botw-v4"
LOCAL = PROJECT / "production/local" / REVISION
SCRIPT = PROJECT / "script" / REVISION


def read(path):
    return json.loads(path.read_text("utf-8-sig"))


def save(path, value):
    assert path.parent.resolve() == HERE.resolve(), "Metadata outside owned revision"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf-8")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def norm(text):
    return re.sub(r"[^0-9a-z가-힣]", "", text.lower())


def locate(scene, needle):
    words = read(ROOT / scene["wordFile"])["words"]
    chars, times = "", []
    for word in words:
        text = norm(word.get("text", word.get("word", "")))
        stamp = word.get("timestamp", [word.get("start"), word.get("end")])
        if not text:
            continue
        assert stamp[0] is not None, "An actual ASR word time is required"
        chars += text
        times.extend([stamp[0]] * len(text))
    spoken = "".join(norm(p["spokenText"]) for p in scene["paragraphs"])
    anchor = norm(needle)
    at = spoken.find(anchor)
    if at < 0:
        raise ValueError("Anchor absent from locked spoken text: " + needle)
    matcher = difflib.SequenceMatcher(None, spoken, chars, autojunk=False)
    mapping = {}
    for block in matcher.get_matching_blocks():
        mapping.update({block.a + i: block.b + i for i in range(block.size)})
    mapped = [mapping[i] for i in range(at, at + len(anchor)) if i in mapping]
    if len(mapped) < max(3, len(anchor) * .65):
        raise ValueError("Weak measured word anchor: " + needle)
    return round(times[mapped[0]] * 60)


def proposal():
    plan = read(HERE / "production-plan.json")
    timing_path = LOCAL / "voice/source-scene-timings.json"
    timing = read(timing_path)
    assert plan.get("cuts"), "Authored, source-matched cut plan is required"
    rows = []
    for scene in timing["scenes"]:
        cuts = [c for c in plan["cuts"] if c["scene"] == scene["id"]]
        assert cuts, scene["id"]
        starts = [0] + [locate(scene, c["speechAnchor"]) for c in cuts[1:]]
        ends = starts[1:] + [round(scene["duration"] * 60)]
        for cut, start, end in zip(cuts, starts, ends):
            assert 0 <= start < end, (cut["id"], start, end)
            row = copy.deepcopy(cut)
            row.update(localStartFrame=start, localEndFrame=end, frames=end - start,
                       reviewedWithNarration=False, phaseSeconds=None)
            rows.append(row)
    save(HERE / "timing-proposal.json", {
        "revision": REVISION, "timingSource": rel(timing_path),
        "timingSha256": sha(timing_path),
        "status": "measured-anchor-proposal-needs-edit-review",
        "reviewedWithFullNarration": False, "cuts": rows,
    })
    print("Measured proposal saved. Source coverage, cue actions and allocation still require review.")


def lock():
    authored = read(HERE / "timing-lock.json")
    timing_path = LOCAL / "voice/source-scene-timings.json"
    timing = read(timing_path)
    assert authored.get("reviewedWithFullNarration") is True
    assert authored.get("sourceFootageReviewed") is True
    assert authored.get("nativeCueOwnerReleased") is True, "Native preflight owns provisional cues until explicit handoff"
    assert authored["timingSha256"] == sha(timing_path)
    for item in authored["scriptInputs"]:
        assert sha(ROOT / item["path"]) == item["sha256"], "Draft changed after timing review"
    expected_scripts = {rel(SCRIPT / name) for name in [
        "narration.ko.json", "narration.en.json", "narration.spoken-ko.json"]}
    assert expected_scripts.issubset({item["path"] for item in authored["scriptInputs"]})
    sources = read(HERE / "sources.json")
    sourcebank = {source["id"]: source for source in sources["sources"]}
    semantic = {cut["id"]: cut for cut in read(HERE / "unity-teaching-cues.draft.json")["cuts"]}
    original = read(PROJECT / "production/clarity-v3/edit-plan.json")
    body = math.ceil((timing["scenes"][-1]["sourceOrigin"] + timing["scenes"][-1]["duration"]) * 60)
    out = copy.deepcopy(original)
    out.update(revision=REVISION, bodyFrames=body, totalFrames=body + 720,
               scenes=[], cuts=[], outputDir=rel(LOCAL / "edit"), outputStem=PROJECT.name)
    out["captionAliases"] = read(SCRIPT / "caption-aliases.json")
    out["audio"]["sourceReviewPath"] = rel(HERE / "audio-source-review.json")
    out["audio"]["sourceReviewSha256"] = sha(HERE / "audio-source-review.json")
    out["notes"] = [
        "Old clarity-v3 sources, scenes, voice and delivery are preserved.",
        "Full continuous own-voice SampleB take; approved Nimbus BGM and source-specific game audio.",
        "BOTW, Unpacking and A Short Hike; one meaningfully taught Nintendo game out of three.",
        "BOTW field Pro HUD lacks a temperature gauge: actual menu evidence and clearly labelled illustrations remain distinct.",
        "Self-authored Unity is explanation footage; independent sources play at native speed and aspect with no loops.",
    ]
    jobs, cues, cursor = [], [], 120
    render_version = authored.get("renderVersion", "measured-v1")
    assert re.fullmatch(r"[a-z0-9-]+", render_version)
    for scene in timing["scenes"]:
        base = 120 + round(scene["sourceOrigin"] * 60)
        scene_end = 120 + round((scene["sourceOrigin"] + scene["duration"]) * 60)
        if scene == timing["scenes"][-1]:
            scene_end = 120 + body
        out["scenes"].append({"id": scene["id"], "title": scene["title"],
                              "voiceStart": 2 + scene["sourceOrigin"], "startFrame": base, "endFrame": scene_end})
        group = [row for row in authored["cuts"] if row["scene"] == scene["id"]]
        for index, row in enumerate(group):
            assert row["reviewedWithNarration"] and row["frames"] > 0
            start, end = base + row["localStartFrame"], base + row["localEndFrame"]
            if index == len(group) - 1:
                end = scene_end
            assert start == cursor and end > start, (row["id"], start, cursor, end)
            cut = {key: row[key] for key in ["id", "scene", "kind", "normalSpeed", "loop", "playbackSpeed"]}
            assert cut["normalSpeed"] is True and cut["loop"] is False and cut["playbackSpeed"] == 1
            cut.update(startFrame=start, endFrame=end, frames=end - start)
            if row["kind"] == "independent-gameplay":
                source = sourcebank[row["source"]]
                assert source["classification"] == "independent-gameplay" and source.get("referenceLesson") is False
                assert source["nativeFhd"] is True
                assert source["decoded"]["width"] >= 1920 and source["decoded"]["height"] >= 1080
                audio_enabled = source["audio"].get("sourceAudioEnabled")
                assert isinstance(audio_enabled, bool), "Source-specific audio decision required"
                cut.update(source=row["source"], game=source.get("game", row["source"]),
                           sourceFile=source["file"], sourceSha256=source["sha256"], sourceStart=row["sourceStart"],
                           sourceAttribution=f"{source['creator']} | {source['url']}", sourceAudioEnabled=audio_enabled,
                           sourceAudioReviewStatus="source-specific-reviewed", audioRightsReview=rel(HERE / "audio-source-review.json"),
                           onScreenAttributionRequired=False, viewport=[0, 0, 1920, 880], marks=row.get("marks", []))
                limit = row.get("reviewedSourceEnd")
                assert limit is not None and cut["sourceStart"] >= 0
                assert cut["sourceStart"] + cut["frames"] / 60 <= limit + .02, (cut["id"], "outside inspected range")
                assert limit <= float(source["decoded"]["duration"]) + .02
                cut["reviewEvidence"] = row["reviewEvidence"]
            else:
                assert row["kind"] == "explanation"
                phases = row.get("phaseSeconds")
                assert phases and len(phases) == 3 and 0 < phases[0] < phases[1] < phases[2] <= cut["frames"] / 60
                concept = semantic[row["id"]]
                assert row["mode"] == concept["mode"]
                cut.update(purpose=row["mode"], renderedSource=rel(LOCAL / f"render/{render_version}/{row['id']}/unity.mp4"),
                           renderedStartFrame=0, stageClass="D29BotwStage")
                cue = {"id": row["id"], "mode": row["mode"], "title": concept["title"],
                       "phaseSeconds": phases, "speechCueEvidence": row["speechCueEvidence"]}
                if concept.get("variant"):
                    cue["variant"] = concept["variant"]
                if concept.get("canonicalTerm"):
                    cue["canonicalTerm"] = concept["canonicalTerm"]
                    cut["canonicalTerm"] = concept["canonicalTerm"]
                cues.append(cue)
                boundaries = [0] + [round(t * 60) for t in phases] + [cut["frames"] - 1]
                samples = {max(0, min(cut["frames"] - 1, value + offset)) for value in boundaries for offset in [-1, 0, 1]}
                samples.update((a + b) // 2 for a, b in zip(boundaries, boundaries[1:]))
                jobs.append({"slug": PROJECT.name, "cutId": row["id"], "frames": cut["frames"],
                             "stageClass": "D29BotwStage", "sampleFrames": sorted(samples)})
            out["cuts"].append(cut)
            cursor = end
    actual = sum(cut["frames"] for cut in out["cuts"] if cut["kind"] == "independent-gameplay")
    assert abs(actual - round(body * .6)) <= 1, ("Meaningful allocation must meet authorized60:40", actual, body)
    assert cursor == 120 + body
    save(HERE / "edit-plan.json", out)
    save(HERE / "unity-cues.json", {"revision": REVISION, "timingLocked": True,
         "timingSha256": sha(timing_path), "cuts": cues})
    save(HERE / "capture-jobs.json", {"revision": REVISION, "timingLocked": True, "jobs": jobs})
    save(HERE / "timing-lock-receipt.json", {"status": "measured-internal-timing-review-locked",
         "editPlanSha256": sha(HERE / "edit-plan.json"), "unityCuesSha256": sha(HERE / "unity-cues.json"),
         "bodyFrames": body, "gameplayFrames": actual, "share": actual / body, "humanReview": False})
    print("Locked measured edit and native cues; source freeze and resource slot are still required.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--proposal", action="store_true")
    group.add_argument("--lock", action="store_true")
    args = parser.parse_args()
    proposal() if args.proposal else lock()
