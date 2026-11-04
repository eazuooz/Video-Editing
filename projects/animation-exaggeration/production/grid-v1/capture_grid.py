"""A02-only no-focus Unity requests. Importing this module starts no job.

The nominal profiles are engineering preflights, not speech timing or final QA.
Call freeze/compile only after the integrator finishes all A02 Unity sources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import time
import uuid

H = Path(__file__).resolve().parent
R = H.parents[3]
U = R / "unity/VideoEditing"
C = U / "Assets/VideoScenes/animation-series-v1"
L = U / "Library"
M = H.parent / "local/grid-v1"
STAGE = "AnimationExaggerationStage"
SLUG = "animation-exaggeration"
PROFILE = C / "animation-exaggeration-presentations.json"
MODES = ("normal-and-pause", "size-amplitude", "shoulder-control",
         "paused-pose-context", "linear-overshoot", "shape-overshoot")
PHASE_COUNTS = dict(zip(MODES, (3, 3, 4, 3, 5, 4)))
CLIP = U / ("Assets/ThirdParty/YamyamAssetLibrary/"
            "011-cartoon-city-massive-pack-characters-unity-godot-fbx/"
            "Characters Full/Unity FBX/Animations/FightM_Punch_A.fbx")
BRIDGE_REQUEST = L / "AnimationGridV1.request.json"
BRIDGE_ACK = L / "AnimationGridV1.compiled.json"
ACTIVE_STATES = {"building", "capturing", "rendering", "running", "compiling",
                 "pending", "queued", "processing", "started", "busy", "active"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read(path):
    return json.loads(path.read_text("utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def authorize():
    control = read(R / "shared/publishing/video-production-control.json")
    grant = control["finiteBatchAuthorizations"]["animation-18-20261031"]
    require(grant.get("productionAuthorized") and grant.get("renderAuthorized")
            and "A02" in grant.get("episodeIds", []), "A02 production/render authorization missing")
    require(not grant.get("youtubeAuthorized"), "Re-read changed platform authorization before proceeding")
    local = read(H / "authorization.json")
    require(local.get("episode") == "A02" and local.get("slug") == SLUG
            and local.get("localProductionAuthorized"), "A02 local authorization mismatch")


def idle():
    require(not list(L.glob("*.request")) and not list(L.glob("*.request.json")),
            "Preserve pending bridge requests")
    for path in L.glob("*.status.json"):
        require(read(path).get("status") not in ACTIVE_STATES,
                "Preserve active capture: " + path.name)
    asset_state = L / "YamyamAssetLibrary/state.json"
    require(read(asset_state).get("phase") in ("complete", "failed"),
            "Preserve active asset-library work")
    require(not (L / "YamyamAssetLibrary/request.json").exists(),
            "Preserve pending asset-library request")


def source_files():
    # Both source and imported-asset metadata participate in the fingerprint.
    files = [C / "AnimationLessonStage.cs", C / "AnimationExaggerationStage.cs",
             C / "Editor/AnimationGridCapture.cs", C / "Editor/AnimationExaggerationStageEditor.cs", C / "asset-map.json", PROFILE,
             H / "rasterize_unity_labels.py", H / "capture_grid.py",
             H / "native-nominal-profiles.json", U / "Packages/packages-lock.json",
             U / "Packages/manifest.json", U / "ProjectSettings/ProjectVersion.txt",
             U / "ProjectSettings/GraphicsSettings.asset", U / "ProjectSettings/QualitySettings.asset",
             U / "Assets/Settings/PC_RPAsset.asset", U / "Assets/Settings/PC_Renderer.asset",
             U / "Assets/Settings/Mobile_RPAsset.asset", U / "Assets/Settings/Mobile_Renderer.asset"]
    assets = read(C / "asset-map.json")["assets"]
    selected = [entry for entry in assets if entry.get("key") == "hero"]
    require(len(selected) == 1, "A02 needs exactly one selected hero asset")
    for entry in selected:
        path = (U / entry["path"]).resolve()
        require(path.is_relative_to(U.resolve()), "Selected asset escapes the Unity project")
        files.extend((path, Path(str(path) + ".meta")))
    files.extend((CLIP, Path(str(CLIP) + ".meta")))
    # A saved scene resolves MonoScript and JSON references by these exact GUIDs.
    # Initial import creates them; production freezes must retain them with source bytes.
    files.extend(Path(str(path) + ".meta") for path in list(files)
                 if path.is_relative_to(C) and path.suffix != ".meta"
                 and Path(str(path) + ".meta").is_file())
    files = sorted(set(path.resolve() for path in files), key=lambda path: path.as_posix())
    for path in files:
        require(path.is_file(), "A02 integration source is not ready: " + str(path))
        require(path.is_relative_to(R.resolve()), "Source escapes the workspace")
    return files


def immutable_bytes(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == content, "Immutable source snapshot changed: " + str(path))
        return
    with path.open("xb") as stream:
        stream.write(content)


def freeze():
    """Explicit mutation used by the coordinator after integration, never on import."""
    authorize()
    idle()
    files = source_files()
    payloads = [(path, path.read_bytes()) for path in files]
    records = [{"path": path.relative_to(R).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
               for path, content in payloads]
    fingerprint = hashlib.sha256(json.dumps(records, sort_keys=True).encode("utf-8")).hexdigest()
    local_root = M / "source-snapshots" / fingerprint
    tracked_root = H / "source-snapshots" / fingerprint
    # Full immutable bytes, including vendor prefab/FBX, stay under ignored media.
    # The reviewable source snapshot never redistributes third-party originals.
    for (path, content), record in zip(payloads, records):
        relative = Path(record["path"])
        immutable_bytes(local_root / relative, content)
        if "ThirdParty" not in path.parts:
            immutable_bytes(tracked_root / relative, content)
    for path, record in zip(files, records):
        require(sha(path) == record["sha256"], "Source changed while freezing: " + str(path))
    receipt = {"episode": "A02", "slug": SLUG, "stageClass": STAGE,
               "fingerprint": fingerprint, "files": records,
               "fullSnapshotRoot": local_root.relative_to(R).as_posix(),
               "vendorBytesInTrackedSnapshot": False, "notHumanReview": True}
    encoded = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    immutable_bytes(tracked_root / "manifest.json", encoded)
    immutable_bytes(local_root / "manifest.json", encoded)
    # A01's AnimationGridBuildVersion.cs is never written by this helper.
    target = C / "AnimationExaggerationBuildVersion.cs"
    code = ('namespace Yamyam.AnimationSeries { public static class AnimationExaggerationBuildVersion '
            '{ public static string For(string stage) { return stage=="' + STAGE + '"?"'
            + fingerprint + '":"unknown"; } } }\n')
    idle()
    if not target.exists() or target.read_text("utf-8-sig") != code:
        target.write_text(code, encoding="utf-8")
    write(H / "source-fingerprint.json", receipt)
    return fingerprint


def matching_stage(ack, fingerprint):
    entries = [entry for entry in ack.get("stages", []) if entry.get("stageClass") == STAGE]
    return (len(entries) == 1 and entries[0].get("typeAvailable") is True
            and entries[0].get("fingerprint") == fingerprint)


def compile_sources(fingerprint):
    if BRIDGE_ACK.exists():
        current = read(BRIDGE_ACK)
        if matching_stage(current, fingerprint):
            write(H / "compiled-ack.json", current)
            print("REUSED matching A02 compiled acknowledgement " + fingerprint, flush=True)
            return
    authorize()
    idle()
    nonce = "animation-exaggeration-" + uuid.uuid4().hex
    with (L / "YamyamAssetLibrary/request.json").open("x", encoding="utf-8") as stream:
        json.dump({"command": "probe", "nonce": nonce}, stream)
    print("No-focus A02 refresh requested " + nonce, flush=True)
    deadline = time.monotonic() + 360
    while time.monotonic() < deadline:
        if BRIDGE_ACK.exists():
            current = read(BRIDGE_ACK)
            if matching_stage(current, fingerprint):
                write(H / "compiled-ack.json", current)
                print("COMPILED " + fingerprint, flush=True)
                return
        time.sleep(1)
    raise RuntimeError("No matching A02 compiled acknowledgement; editor and pending requests preserved")


def select_profile(cut, presentation, frames=None):
    book = read(PROFILE)
    require(book.get("schemaVersion") == 1, "Unsupported A02 presentation schema")
    matches = [profile for profile in book.get("presentations", []) if profile.get("id") == presentation]
    require(len(matches) == 1, "Missing or ambiguous A02 presentation: " + presentation)
    profile = matches[0]
    require(profile.get("episode") == "A02" and profile.get("revision") == "grid-v1"
            and profile.get("mode") == cut, "A02 presentation/cut mismatch")
    duration = profile.get("duration", 0)
    require(isinstance(duration, (int, float)) and math.isfinite(duration) and duration > 0,
            "A02 profile needs a positive finite duration")
    measured_frames = round(duration * 60)
    require(abs(duration * 60 - measured_frames) < 0.0001 and 1 <= measured_frames <= 36000,
            "A02 profile duration must be an exact 60fps frame count")
    require(frames is None or frames == measured_frames, "--frames disagrees with the selected profile")
    return profile, measured_frames


def sample_frames(profile, frames, override=None):
    values = ([int(value) for value in override.split(",")] if override is not None
              else profile.get("preflight", {}).get("sampleFrames", []))
    require(values and all(isinstance(value, int) and not isinstance(value, bool) for value in values),
            "Provide explicit integer --samples or a profile preflight sample list")
    samples = sorted(set(values))
    require(12 <= len(samples) <= 1000 and 0 <= samples[0] and samples[-1] < frames,
            "Preflight needs 12–1000 unique in-range action/phase samples")
    return samples


def gpu_guard():
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu",
                                      "--format=csv,noheader,nounits"], text=True)
    free, utilization = map(int, output.strip().splitlines()[0].split(","))
    require(free >= 4096 and utilization <= 85,
            f"Preserve other GPU activity: {free} MiB free, {utilization}% utilization")
    return {"freeMiB": free, "utilizationPercent": utilization}


def request_capture(action, cut, revision, presentation, frames, samples, fingerprint):
    require(action in ("preflight", "render") and cut in MODES, "Unsupported A02 capture")
    require(re.fullmatch(r"[A-Za-z0-9_-]+", revision) is not None, "Invalid output revision")
    require(matching_stage(read(H / "compiled-ack.json"), fingerprint), "Compile the current A02 source first")
    # Check the live acknowledgement too: an old local receipt cannot authorize a new assembly.
    require(matching_stage(read(BRIDGE_ACK), fingerprint), "Live A02 acknowledgement differs; compile first")
    authorize()
    idle()
    gpu = gpu_guard()
    output = M / action / revision / cut
    require(not output.exists(), "Prior output preserved; choose a fresh revision")
    job = {"command": action, "slug": SLUG, "cutId": cut, "stageClass": STAGE,
           "output": output.as_posix(), "expectedFingerprint": fingerprint,
           "frames": frames, "sampleFrames": samples, "presentationId": presentation}
    idle()
    write(output / "request.json", job)
    write(H / "last-capture-request.json", {"job": job, "gpu": gpu, "notHumanReview": True})
    # Exclusive create preserves any request arriving after the last idle check.
    with BRIDGE_REQUEST.open("x", encoding="utf-8") as stream:
        json.dump(job, stream)
    print("REQUESTED " + str(output), flush=True)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        success, failure = output / (action + "-success.json"), output / (action + "-failure.json")
        if success.exists():
            print("COMPLETE " + str(success), flush=True)
            return
        if failure.exists():
            raise RuntimeError(read(failure).get("error", "A02 capture failed"))
        time.sleep(1)
    raise RuntimeError("Capture timed out; preserve pending job and inspect status")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True, choices=("compile", "preflight", "render"))
    parser.add_argument("--cut", choices=MODES, default=MODES[0])
    parser.add_argument("--revision", default="nominal-preflight-v1")
    parser.add_argument("--presentation", help="Defaults to A02-PF-<cut>; must exist in the copied Unity profile")
    parser.add_argument("--frames", type=int, help="Optional exact match to the profile duration at 60fps")
    parser.add_argument("--samples", help="Exact comma-separated preflight frame numbers (at least 12)")
    args = parser.parse_args()
    authorize()
    idle()
    if args.action == "compile":
        compile_sources(freeze())
        return
    presentation = args.presentation or "A02-PF-" + args.cut
    profile, frames = select_profile(args.cut, presentation, args.frames)
    samples = [] if args.action == "render" else sample_frames(profile, frames, args.samples)
    fingerprint = freeze()
    request_capture(args.action, args.cut, args.revision, presentation, frames, samples, fingerprint)


if __name__ == "__main__":
    main()
