"""Hash the saved BOTW scene immediately after a completed full capture.

No Unity calls, media changes, or mutation of the native request/success files.
An existing receipt is checked, never replaced or silently backfilled on reuse.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
LOCAL = ROOT / "projects/kind-to-beginners/production/local/botw-v4"
UNITY = ROOT / "unity/VideoEditing"
SLUG = "kind-to-beginners"
STAGE = "D29BotwStage"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_path(value):
    p = Path(value)
    p = p if p.is_absolute() else ROOT / p
    require(p.resolve().is_relative_to(ROOT.resolve()), "Path escapes physical D workspace")
    return p.resolve()


def rel(path):
    return local_path(path).relative_to(ROOT.resolve()).as_posix()


def payload(request_path, success_path):
    request_path, success_path = local_path(request_path), local_path(success_path)
    folder = request_path.parent
    require(folder.is_relative_to(LOCAL.resolve() / "render"), "Only full render folders accepted")
    tail = folder.relative_to(LOCAL.resolve()).parts
    require(len(tail) == 3 and tail[0] == "render", "Expected render/revision/cut")
    revision, cid = tail[1:]
    require(re.fullmatch(r"[A-Za-z0-9_-]+", revision) is not None, "Invalid render revision")
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", cid) is not None, "Invalid cut ID")
    require(request_path.name == "request.json" and success_path == folder / "render-success.json", "Receipt paths mismatch")
    req, done = read(request_path), read(success_path)
    require(req["command"] == "render" and req["stageClass"] == STAGE, "Wrong capture class/phase")
    require(req["slug"] == done["slug"] == SLUG and req["cutId"] == done["cutId"] == cid, "Wrong capture identity")
    require(done["status"] == "complete" and not done.get("error"), "Capture incomplete")
    require(done["completed"] == done["frames"] == req["frames"], "Capture frame mismatch")
    require(done["compiledSourceFingerprint"] == req["expectedFingerprint"], "Capture fingerprint mismatch")
    require(local_path(req["output"]) == local_path(done["output"]) == folder, "Capture output mismatch")
    require(done["renderRequest"] == "RenderPipeline.StandardRequest (full camera stack)", "Unexpected render path")
    expected_scene = f"Assets/VideoScenes/{SLUG}/botw-v4/RenderRevisions/{revision}/{cid}.unity"
    require(done["scene"] == expected_scene, "Scene is not this full render revision's saved cut")
    scene = local_path(UNITY / expected_scene)
    meta = local_path(str(scene) + ".meta")
    stamp_path = local_path(str(scene) + ".capture-source.json")
    stamp = read(stamp_path)
    require(stamp == {"slug": SLUG, "cutId": cid, "stageClass": STAGE,
                     "fingerprint": req["expectedFingerprint"], "frames": req["frames"]}, "Saved scene stamp mismatch")
    return {"schemaVersion": 1, "slug": SLUG, "revision": "botw-v4", "cutId": cid,
            "renderRevision": revision, "stageClass": STAGE, "frames": req["frames"],
            "compiledFingerprint": req["expectedFingerprint"], "stageAssemblyMvid": done["stageAssemblyMvid"],
            "request": rel(request_path), "requestSha256": sha(request_path),
            "successReceipt": rel(success_path), "successSha256": sha(success_path),
            "scene": rel(scene), "sceneSha256": sha(scene),
            "sceneMeta": rel(meta), "sceneMetaSha256": sha(meta),
            "sceneStamp": rel(stamp_path), "sceneStampSha256": sha(stamp_path)}


def persist(request_path, success_path):
    record = payload(request_path, success_path)
    record.update(capturedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  provenance="Coordinator hashed saved scene after native full-capture success; no receipt or scene altered.")
    target = local_path(request_path).parent / "scene-evidence.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return record


def verify(request_path, success_path):
    target = local_path(request_path).parent / "scene-evidence.json"
    require(target.is_file(), "Missing capture-time saved-scene evidence; do not silently backfill")
    expected, actual = payload(request_path, success_path), read(target)
    require(all(actual.get(k) == v for k, v in expected.items()), "Saved scene bytes or capture receipt changed after evidence")
    require(bool(actual.get("capturedAt")) and actual.get("provenance", "").startswith("Coordinator hashed"), "Scene evidence provenance missing")
    return actual
