"""Verify and bind only exact measured BOTW full captures.

Default/--dry-run performs read-only metadata and container checks. --apply is an
explicit later coordinator action; it changes only this revision's metadata.
No render, decode pass, TTS, scene write, or media modification is performed.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
from freeze_sources import records_for, fingerprint
from native_scene_evidence import local_path, require, verify as verify_scene

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
LOCAL = PROJECT / "production/local/botw-v4"
UNITY = ROOT / "unity/VideoEditing"
SLUG, REVISION, STAGE = "kind-to-beginners", "botw-v4", "D29BotwStage"
STAGE_PATH = "unity/VideoEditing/Assets/VideoScenes/design-d29-botw-v4/D29BotwStage.cs"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rel(path):
    return local_path(path).relative_to(ROOT.resolve()).as_posix()


def indexed(rows, key):
    values = [row[key] for row in rows]
    require(len(values) == len(set(values)), "Duplicate IDs in " + key)
    return dict(zip(values, rows))


def stable(recorded):
    for path, digest in recorded.items():
        require(sha(path) == digest, "Input changed during binding: " + rel(path))


def check():
    tracked = {}

    def checked(path):
        p = local_path(path)
        data = read(p)
        tracked[p] = sha(p)
        return data

    auth = checked(HERE / "authorization.json")
    require(auth["slug"] == SLUG and auth["revision"] == REVISION and auth["localProductionAuthorized"] is True,
            "Selected BOTW local production authorization missing")
    jobs_path, cues_path = HERE / "capture-jobs.json", HERE / "unity-cues.json"
    jobs_doc, cues_doc = checked(jobs_path), checked(cues_path)
    require(jobs_doc.get("timingLocked") is True and cues_doc.get("timingLocked") is True,
            "Measured speech timing is not locked; provisional preflights cannot be bound")
    require(jobs_doc.get("revision") == cues_doc.get("revision") == REVISION, "Wrong timing revision")
    plan_path = HERE / "edit-plan.json"
    plan, production = checked(plan_path), checked(HERE / "production-plan.json")
    require(plan.get("slug") == SLUG and plan.get("revision") == REVISION, "Wrong edit identity")
    require((plan["width"], plan["height"], plan["fps"]) == (1920, 1080, 60), "Wrong master format")
    require(local_path(plan["outputDir"]) == LOCAL.resolve() / "edit", "Edit output is not the isolated D revision")
    timing_receipt = checked(HERE / "timing-lock-receipt.json")
    timing = checked(HERE / "timing-lock.json")
    require(timing.get("reviewedWithFullNarration") is True and timing.get("sourceFootageReviewed") is True
            and timing.get("nativeCueOwnerReleased") is True, "Measured editorial timing review is missing")
    original_plan = HERE / "edit-plan.before-native-binding.json"
    base_path = original_plan if original_plan.exists() else plan_path
    baseline = checked(base_path)
    require(sha(base_path) == timing_receipt["editPlanSha256"], "Edit differs from measured timing lock")
    require(sha(cues_path) == timing_receipt["unityCuesSha256"], "Cue timings changed after lock")
    timing_source = LOCAL / "voice/source-scene-timings.json"
    tracked[timing_source] = sha(timing_source)
    require(tracked[timing_source] == timing["timingSha256"] == cues_doc["timingSha256"], "Voice timing source changed")
    for item in timing["scriptInputs"]:
        p = local_path(item["path"])
        require(p.is_relative_to((PROJECT / "script/botw-v4").resolve()), "Foreign script input")
        tracked[p] = sha(p)
        require(tracked[p] == item["sha256"], "Script changed after measured timing lock")
    frozen_path = HERE / "botw-code-fingerprint.json"
    frozen, ack = checked(frozen_path), checked(HERE / "native-compiled-ack.json")
    records = records_for(STAGE)
    fp = fingerprint(records)
    require(frozen["fingerprints"][STAGE] == fp and frozen["filesByStage"][STAGE] == records,
            "Current stage, source, assets or cue/job bytes differ from freeze")
    require(sha(local_path(frozen["generatedBuildVersion"])) == frozen["generatedBuildVersionSha256"],
            "Generated build-version source changed")
    stage_record = next(row for row in records if row["path"] == STAGE_PATH)
    compiled = [r for r in ack["stages"] if r["stageClass"] == STAGE]
    require(ack["status"] == "compiled" and len(compiled) == 1 and compiled[0]["typeAvailable"] is True
            and compiled[0]["fingerprint"] == fp, "No compiled acknowledgement for this exact source")
    mvid = compiled[0]["assemblyMvid"]
    jobs, cues = indexed(jobs_doc["jobs"], "cutId"), indexed(cues_doc["cuts"], "id")
    all_cuts = indexed(baseline["cuts"], "id")
    explanations = {cid: c for cid, c in all_cuts.items() if c["kind"] == "explanation"}
    require(explanations and set(explanations) == set(jobs) == set(cues), "Edit, cue and capture-job sets differ")
    result, captures = copy.deepcopy(baseline), []
    for cut in result["cuts"]:
        if cut["kind"] != "explanation":
            continue
        cid = cut["id"]
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", cid) is not None, "Invalid cut ID")
        job, cue = jobs[cid], cues[cid]
        require(job["slug"] == SLUG and job["stageClass"] == cut["stageClass"] == STAGE
                and job["frames"] == cut["frames"], "Capture job mismatch for " + cid)
        require(cut["endFrame"] - cut["startFrame"] == cut["frames"], "Cut frame range mismatch")
        require(cue["mode"] == cut["purpose"], "Cue mechanism differs from edit")
        phases = cue["phaseSeconds"]
        require(len(phases) == 3 and 0 < phases[0] < phases[1] < phases[2] <= cut["frames"] / 60,
                "Cue phases are not measured local cut times")
        movie = local_path(cut["renderedSource"])
        require(movie.is_relative_to(LOCAL.resolve() / "render") and movie.name == "unity.mp4", "Wrong native movie scope")
        tail = movie.relative_to(LOCAL.resolve()).parts
        require(len(tail) == 4 and tail[2] == cid, "Native file must be render/revision/cut/unity.mp4")
        folder = movie.parent
        req_path, done_path = folder / "request.json", folder / "render-success.json"
        require(not (folder / "render-failure.json").exists(), "Failure receipt exists for " + cid)
        req, done = checked(req_path), checked(done_path)
        require(req["stageClass"] == STAGE and req["expectedFingerprint"] == fp, "Wrong stage fingerprint")
        require(req["jobsFile"] == rel(jobs_path) and req["jobsSha256"] == sha(jobs_path), "Capture used different measured jobs")
        require(req["sourceFiles"] == records, "Capture did not use current exact frozen inputs")
        raw = {key: req[key] for key in ["slug", "cutId", "stageClass", "frames", "command", "expectedFingerprint", "output", "sampleFrames"]}
        expected_input = hashlib.sha256(json.dumps({"request": raw, "job": job, "files": records}, sort_keys=True).encode()).hexdigest()
        require(req["inputHash"] == expected_input, "Capture request input hash mismatch")
        require(done["stageAssemblyMvid"] == mvid and done["unity"] == ack["unityVersion"], "Capture used different compiled assembly/editor")
        evidence = verify_scene(req_path, done_path)
        evidence_path = folder / "scene-evidence.json"
        tracked[evidence_path] = sha(evidence_path)
        for path_key, digest_key in [("scene", "sceneSha256"), ("sceneMeta", "sceneMetaSha256"), ("sceneStamp", "sceneStampSha256")]:
            tracked[local_path(evidence[path_key])] = evidence[digest_key]
        require(evidence["compiledFingerprint"] == fp and evidence["frames"] == cut["frames"], "Saved scene evidence mismatch")
        stream_doc = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(movie)], text=True))
        streams = stream_doc["streams"]
        require(len(streams) == 1 and streams[0]["codec_type"] == "video", "Unity movie must have one silent video stream")
        v = streams[0]
        require((v["width"], v["height"]) == (1920, 1080) and Fraction(v["avg_frame_rate"]) == 60
                and int(v["nb_frames"]) == cut["frames"] and abs(float(v["duration"]) - cut["frames"] / 60) < 1/60,
                "Unity native container format/length mismatch")
        movie_sha = sha(movie)
        record = {"cutId": cid, "frames": cut["frames"], "compiledFingerprint": fp,
                  "stageClass": STAGE, "stageSourceSha256": stage_record["sha256"], "stageAssemblyMvid": mvid,
                  "movie": rel(movie), "movieSha256": movie_sha,
                  "request": rel(req_path), "requestSha256": sha(req_path),
                  "successReceipt": rel(done_path), "successSha256": sha(done_path),
                  "scene": evidence["scene"], "sceneSha256": evidence["sceneSha256"],
                  "sceneMeta": evidence["sceneMeta"], "sceneMetaSha256": evidence["sceneMetaSha256"],
                  "sceneStamp": evidence["sceneStamp"], "sceneStampSha256": evidence["sceneStampSha256"],
                  "sceneEvidence": rel(evidence_path), "sceneEvidenceSha256": sha(evidence_path),
                  "sourceFiles": records, "containerMetadataVerified": True,
                  "fullDecode": "pending final compositor validation", "nativeMovingPixels": "separate full-capture pixel review required"}
        captures.append(record)
        cut.update(renderedSource=rel(movie), renderedStartFrame=0, renderedSourceSha256=movie_sha, nativeCapture=record)
    require(plan == baseline or plan == result, "Existing edit has foreign changes or a different binding; preserve and review")
    require(fingerprint(records_for(STAGE)) == fp, "Source changed while captures were checked")
    stable(tracked)
    return result, production, captures, tracked, {"compiledFingerprint": fp, "stageSourceSha256": stage_record["sha256"],
          "compiledAck": rel(HERE / "native-compiled-ack.json"), "compiledAckSha256": sha(HERE / "native-compiled-ack.json"),
          "jobsSha256": sha(jobs_path), "cuesSha256": sha(cues_path), "fingerprintRecordSha256": sha(frozen_path),
          "timingLockReceiptSha256": sha(HERE / "timing-lock-receipt.json")}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def apply(plan, production, captures, tracked, proof):
    library = UNITY / "Library"
    require(not list(library.glob("*.request.json")) and not list(library.glob("*.request")), "Pending native work must finish before binding")
    status_path = library / "DesignBotwV4.status.json"
    if status_path.exists():
        require(read(status_path).get("status") not in ("building", "capturing"), "Active native capture must finish before binding")
    binding_path = HERE / "native-binding.json"
    if binding_path.exists():
        old = read(binding_path)
        require(old["editPlanSha256"] == sha(HERE / "edit-plan.json") and old["captures"] == captures,
                "A different native binding already exists; preserve it")
        print(json.dumps({"status": "already-bound-and-reverified", "writesPerformed": False}))
        return
    timing = indexed(read(HERE / "timing-lock.json")["cuts"], "id")
    combined = []
    for cut in plan["cuts"]:
        taught = {k: v for k, v in timing[cut["id"]].items() if k not in ["provisionalDurationSeconds", "timingState", "annotations"]}
        taught.update(cut)
        taught.update(timingState="locked-to-measured-continuous-narration", annotations=cut.get("marks", []))
        combined.append(taught)
    production["cuts"] = combined
    production["status"] = "measured-native-captures-bound-final-assembly-pending"
    production["unity"].update(savedScenePaths=[r["scene"] for r in captures], compiledFingerprint=proof["compiledFingerprint"],
        sceneSaveStatus=f"{len(captures)} saved scene/meta/stamp hashes verified against capture-time evidence; native-binding.json")
    body = sum(c["frames"] for c in plan["cuts"])
    actual = sum(c["frames"] for c in plan["cuts"] if c["kind"] == "independent-gameplay")
    require(body == plan["bodyFrames"] and abs(actual - round(body * .6)) <= 1, "Measured body ratio mismatch")
    production["bodyRatio"].update(measured=True, measuredBodyFrames=body, measuredActualFrames=actual, measuredActualShare=actual/body)
    plan_bytes = encoded(plan)
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    production["finalEditPlan"] = {"path": rel(HERE / "edit-plan.json"), "sha256": plan_sha}
    production["quality"]["technicalReview"] = "Exact compiled native captures and saved-scene bytes verified; final moving pixels, full decode and mixed audio remain separate QA."
    binding = {"status": "all-native-receipts-scenes-and-container-metadata-bound", "revision": REVISION,
               "at": datetime.datetime.now(datetime.timezone.utc).isoformat(), **proof,
               "editPlanSha256": plan_sha, "captures": captures, "savedScenePaths": [r["scene"] for r in captures],
               "fullDecode": "pending final assembly verification", "humanWholeReview": "pending", "mediaModified": False}
    stable(tracked)
    for name in ["edit-plan", "production-plan"]:
        current, backup = HERE / (name + ".json"), HERE / (name + ".before-native-binding.json")
        if not backup.exists():
            with backup.open("xb") as stream:
                stream.write(current.read_bytes())
    # Only these two owned JSON files are replaced, after all checks and backups.
    for name, content in [("edit-plan.json", plan_bytes), ("production-plan.json", encoded(production))]:
        target = HERE / name
        require(sha(target) == tracked[target.resolve()], "Concurrent metadata edit; stop")
        temp = HERE / (name + ".binding-" + uuid.uuid4().hex)
        with temp.open("xb") as stream:
            stream.write(content)
        os.replace(temp, target)
    with binding_path.open("xb") as stream:
        stream.write(encoded(binding))
    print(json.dumps({"status": binding["status"], "captures": len(captures), "editPlanSha256": plan_sha, "mediaModified": False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        values = check()
    except (FileNotFoundError, KeyError, ValueError, AssertionError) as exc:
        if args.apply:
            raise
        print(json.dumps({"status": "not-ready", "writesPerformed": False, "blocker": str(exc)}, ensure_ascii=False))
        return
    if args.apply:
        apply(*values)
    else:
        print(json.dumps({"status": "ready-to-bind", "captures": len(values[2]), "writesPerformed": False, **values[-1]}))


if __name__ == "__main__":
    main()
