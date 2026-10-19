"""Render only the selected intro in one bounded, cooperative GPU batch.

The existing body voice and its successful render remain untouched. Importing
this module performs no jobs. A prior completed intro is reused by file hash.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import uuid

R = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parents[2]
L = P / "production/local/intro-v2"
MANIFEST = P / "production/intro-v2/tts-manifest.json"
LEASE = R / "shared/output/GPU_HANDOFF.json"
REVISION = "zombie-quiet-intro-v2"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_path(value):
    path = Path(value)
    return path if path.is_absolute() else R / path


def guard():
    selected = read(R / "shared/publishing/video-production-control.json")["shortsRecurringAuthorization"]
    if (selected.get("selectedShort") != P.name
            or selected.get("latestSelection", {}).get("selectedRevision") != REVISION):
        raise RuntimeError("This exact intro revision is not selected; preserve all existing work.")
    revision = read(P / "planning/production-plan.json").get("latestRevision")
    if isinstance(revision, dict):
        revision = next((revision[key] for key in ["id", "revision", "selectedRevision"]
                         if revision.get(key)), None)
    if revision != REVISION:
        raise RuntimeError("Inspect and record this intro revision in plan.latestRevision first.")
    manifest = read(MANIFEST)
    if manifest.get("slug") != P.name:
        raise RuntimeError("Intro manifest slug differs.")
    if manifest.get("revision") != REVISION:
        raise RuntimeError("Intro manifest revision differs.")
    script = repository_path(manifest["paths"]["script"])
    required = P / "script/intro-v2/narration.ko.json"
    if script.resolve() != required.resolve():
        raise RuntimeError("This worker renders only script/intro-v2/narration.ko.json.")
    tts = manifest["tts"]
    if tts.get("renderMode") != "scene" or tts.get("maxRenderAttempts") != 1:
        raise RuntimeError("Use one bounded continuous-scene render attempt.")
    output = repository_path(tts["outputDir"])
    old_output = R / "shared/output/narration" / P.name / "zombie-quiet-v1"
    if output.resolve() == old_output.resolve():
        raise RuntimeError("The existing body output directory must remain unchanged.")
    return manifest, script


def main():
    import psutil

    manifest, script = guard()
    tts = manifest["tts"]
    output = repository_path(tts["outputDir"]) / (tts["filenameStem"] + ".wav")
    log = L / "tts-execution.json"
    fingerprints = {"manifestSha256": sha(MANIFEST), "scriptSha256": sha(script)}
    if output.exists():
        prior = read(log) if log.exists() else {}
        if (prior.get("state") == "finished" and prior.get("exitCode") == 0
                and prior.get("outputSha256") == sha(output)
                and all(prior.get(key) == value for key, value in fingerprints.items())):
            print("Reused successful intro voice: " + str(output))
            return
        raise RuntimeError("Preserve and inspect existing intro output; no automatic rerender.")
    if log.exists():
        raise RuntimeError("Prior intro attempt recorded; inspect it before any retry.")
    if LEASE.exists():
        raise RuntimeError("Existing GPU lease preserved; no foreign work stopped.")
    raw = subprocess.check_output([
        "nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu",
        "--format=csv,noheader,nounits",
    ], text=True)
    free, total, utilization = [int(value.strip()) for value in raw.splitlines()[0].split(",")]
    if utilization >= 15 or free < 8500:
        raise RuntimeError(f"GPU unavailable: free={free}MiB/utilization={utilization}%; foreign jobs preserved.")
    clients = subprocess.check_output([
        "nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader",
    ], text=True)
    if any("python" in row.lower() for row in clients.splitlines()):
        raise RuntimeError("Another GPU Python process is active; preserve it.")
    process = psutil.Process()
    token = str(uuid.uuid4())
    record = {
        "schemaVersion": 1, "project": P.name, "revision": REVISION,
        "token": token, "state": "gpu_granted_to_tts", "requestedAt": time.time(),
        "coordinator": {"pid": process.pid, "createTime": process.create_time()},
        "gpuBefore": {"freeMiB": free, "totalMiB": total, "utilization": utilization},
        "allocatorLimitMiB": 7168, "foreignProcessesPaused": [],
        "userEvidence": "User explicitly requested this intro animation; only its new sentence is generated.",
        **fingerprints,
    }
    L.mkdir(parents=True, exist_ok=True)
    LEASE.parent.mkdir(parents=True, exist_ok=True)
    with LEASE.open("x", encoding="utf8") as stream:
        json.dump(record, stream)
    code = 1
    try:
        import torch

        torch.cuda.set_per_process_memory_fraction(
            7168 * 1048576 / torch.cuda.get_device_properties(0).total_memory, 0,
        )
        sys.path.insert(0, str(R / "qwen3-tts"))
        import render_narration as worker

        worker.configure_project(P.name, MANIFEST.relative_to(R).as_posix())
        worker.load_tts_dependencies()
        jobs = worker.load_jobs()
        items = worker.build_render_items(jobs)
        if len(items) != 1:
            raise RuntimeError("This intro must be one continuous scene and one batch.")
        worker.render_chunks(items, 1)
        worker.assemble_outputs(jobs)
        guard()
        if fingerprints != {"manifestSha256": sha(MANIFEST), "scriptSha256": sha(script)}:
            raise RuntimeError("Intro inputs changed during rendering; preserve staging for inspection.")
        record.update(
            peakAllocatedMiB=torch.cuda.max_memory_allocated() / 1048576,
            peakReservedMiB=torch.cuda.max_memory_reserved() / 1048576,
            output=str(output.relative_to(R).as_posix()), outputSha256=sha(output),
        )
        code = 0
    except BaseException as error:
        record["error"] = str(error)
        raise
    finally:
        record.update(state="finished" if code == 0 else "failed", finishedAt=time.time(), exitCode=code)
        try:
            with log.open("x", encoding="utf8", newline="\n") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        finally:
            if LEASE.exists() and read(LEASE).get("token") == token:
                LEASE.unlink()


if __name__ == "__main__":
    main()
