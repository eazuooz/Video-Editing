"""Freeze the actual delivered edition, not superseded project narration.

This is preparation evidence only. A matching script/ASR does not constitute
picture review, listening, or approval of a new master.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
ROOT = BATCH.parents[2]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def srt(path):
    def seconds(value):
        hh, mm, ss = value.replace(",", ".").split(":")
        return int(hh) * 3600 + int(mm) * 60 + float(ss)
    result = []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        if len(lines) >= 3 and " --> " in lines[1]:
            a, b = lines[1].split(" --> ")
            result.append(dict(start=seconds(a), end=seconds(b), text=" ".join(lines[2:])))
    return result


def collect():
    result = []
    for item in read(BATCH / "batch.json")["items"]:
        project = ROOT / "projects" / item["slug"]
        outputs = item.get("outputs") or item["outputFiles"]
        delivered = Path(outputs["captioned"])
        revision = delivered.parent.name.removeprefix(item["slug"] + "-")
        work = project / "production/local" / revision
        bindings = read(project / "planning/scene-bindings.json")["scenes"]
        if item["id"] == "M21":
            # V7 replaces sixteen spoken numerical passages and changes lengths.
            # Project script/narration.ko.json and edit-v1 are superseded there.
            catalog = read(project / "production/teaching-v7/scene-catalog.json")["scenes"]
            timeline = read(work / "timeline.json")
            replacements = {s["id"]: " ".join(s["lines"]) for s in read(work / "speech/script.ko.json")["scenes"]}
            scenes = []
            for binding in bindings:
                sid = binding["id"]
                cuts = [c for c in timeline if int(c["sid"]) == int(sid)]
                start = min(c["start"] for c in cuts) / 60
                end = max(c["start"] + c["frames"] for c in cuts) / 60
                teaching = next((c for c in catalog if int(c["scene"]) == int(sid) and c["kind"] == "explanation"), {})
                scenes.append(dict(scene=sid, start=start, end=end,
                    speech=replacements.get(sid, binding["speech"]),
                    currentTeaching=teaching,
                    originalGame=binding.get("actualGamePart"),
                    auditStatus="pending-semantic-and-motion-review"))
            queue = None
        else:
            queue = read(work / "queue.json")
            timeline = read(queue["wordAlignment"])
            times = {s["id"]: s for s in timeline["scenes"]}
            scenes = []
            for binding in bindings:
                t = times[binding["id"]]
                scenes.append(dict(scene=binding["id"], start=2+t["startFrame"]/60,
                    end=2+t["endFrame"]/60, speech=binding["speech"],
                    currentTeaching=t.get("shot", binding.get("shot", {})),
                    wordCueEvidence=t.get("cueEvidence",[])+t.get("valueEvidence",[]),
                    originalGame=binding.get("actualGamePart"),
                    auditStatus="pending-semantic-and-motion-review"))
        cues = srt(outputs["ko"])
        for scene in scenes:
            scene["captionEvidence"] = [c for c in cues if c["start"] < scene["end"] and c["end"] > scene["start"]]
        result.append(dict(id=item["id"], slug=item["slug"], baselineRevision=revision,
            baselineOutputs=outputs, narrationPreservation="Use the actually delivered PCM; no tempo change",
            scenes=scenes, baselineHumanReview=item.get("humanReviewed", False),
            newMasterHumanReview=False, allScenesAudited=False))
    save(HERE / "inventory.json", dict(episodes=result, finalReviewReady=False))
    return result


if __name__ == "__main__":
    for episode in collect():
        print(episode["id"], episode["baselineRevision"], len(episode["scenes"]), "actual delivered scene ranges")
