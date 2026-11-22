"""Capture the 20 walkthrough scenes from the shared VideoEditing Unity project."""
import argparse
from functools import partial
import hashlib
import json
import os
import subprocess
from pathlib import Path
import shutil

import psutil

import make_library_unity_revision_v4 as library
import make_unity_revision_v3 as pipeline
from make_approved_voice_v2 import DEFAULT_OUTPUT, read, resource_guard, save, sha

WORK = Path("D:/YamyamProduction/elden-ring-development-36-walkthrough-v8")
OUT = DEFAULT_OUTPUT.with_name("pc-review-v8")
PROJECT = library.PROJECT
SCENES = library.SCENE_ROOT / "ScenesV8"
PILOTS = {"02-1", "03-3", "05-1", "06-1", "09-3", "10-1"}
IDS = [f"{i:02d}" for i in range(1, 11)]
RIG_EPISODES = {"01", "02", "04", "05", "06", "09", "10"}
RIG_PILOTS = {"09-3", "10-1"}


def selection():
    plan, labels, all_cuts = pipeline.load_plan()
    rows = {key: value for key, value in all_cuts.items() if key[:2] in IDS}
    assert len(rows) == 20 and len(PILOTS & rows.keys()) == 6
    return plan[:10], {episode: labels[episode] for episode in IDS}, rows


def source_id(rows, software):
    scripts = {p.relative_to(PROJECT).as_posix(): sha(p) for p in library.SCENE_ROOT.rglob("*")
               if p.is_file() and p.suffix in (".cs", ".shader")}
    inputs = dict(cuts=rows, scripts=scripts, assetPlan=sha(library.ASSET_PLAN), software=software)
    for name in ("ProjectVersion.txt", "GraphicsSettings.asset", "QualitySettings.asset"):
        inputs[name] = sha(PROJECT / "ProjectSettings" / name)
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()


def configure(software, fingerprint, verified_rig=False):
    mode = "software" if software else "hardware"
    work = WORK / f"{mode}-{fingerprint[:12]}"
    pipeline.NATIVE = PROJECT
    pipeline.WORK = work
    pipeline.CAPTURES = work / "captures"
    pipeline.PILOT = work / "pilot"
    pipeline.STATE = work / "progress.json"
    pipeline.OUTPUT = OUT
    pipeline.EXPECTED_PILOTS = RIG_PILOTS if verified_rig else PILOTS
    pipeline.scoped_guard = gpu_guard
    pipeline.stage_project = library.use_main_project
    pipeline.native_job = partial(library.capture_in_project, work=work, walkthrough=True)
    return work


def gpu_guard():
    guard = resource_guard()
    guard.OWNER = "elden-ring-development-36-walkthrough-v8"
    guard.PROTOCOL = "elden-ring-main-unity-walkthrough-v8"
    return guard


def editor_active(project=None):
    target = project.resolve() if project else None
    for process in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            if (process.info["name"] or "").lower() != "unity.exe":
                continue
            args = process.info["cmdline"] or []
            if "unity hub" in (process.info["exe"] or "").lower() and "serve" in args:
                continue
            if target:
                flags = [arg.lower() for arg in args]
                if "-projectpath" in flags and (i := flags.index("-projectpath") + 1) < len(args):
                    other = Path(args[i])
                    if other.is_absolute():
                        other = other.resolve()
                        if not target.is_relative_to(other) and not other.is_relative_to(target):
                            continue
            return True
        except psutil.NoSuchProcess:
            continue
        except (psutil.AccessDenied, OSError):
            return True
    return ((target or PROJECT) / "Temp/UnityLockfile").exists()


def software_job(worker, work, fp, rows, folder, pilot, verified_rig, *, observed_v10=False):
    if all((folder / key / "capture.json").is_file() and
           read(folder / key / "capture.json")["fingerprint"] == fp for key in rows):
        return
    if editor_active(PROJECT if observed_v10 else None):
        raise RuntimeError("Another Unity editor is using the project or running a capture.")
    if psutil.virtual_memory().available < 12 * 1024**3:
        raise RuntimeError("Insufficient system memory to capture with the software renderer.")
    folder.mkdir(parents=True, exist_ok=True)
    job = work / ("pilot-job.json" if pilot else "capture-job.json")
    save(job, dict(output=str(folder), ffmpeg=shutil.which("ffmpeg"), fingerprint=fp, project=str(PROJECT),
                   pilot=pilot, walkthroughV8=not observed_v10, requireSoftwareAdapter=True,
                   verifiedRig=verified_rig, observedV10=observed_v10,
                   cuts=list(rows.values()), assets=list(library.selected_assets().values())))
    command = [str(pipeline.EDITOR), "-batchmode", "-force-d3d11", "-force-driver-type-warp",
               "-job-worker-count", "3", "-projectPath", str(PROJECT), "-executeMethod",
               "Yamyam.EldenRingLibraryLessons.LibraryCapture.Run", "-eldenFingerprint", fp,
               "-logFile", str(folder / "unity.log")]
    guard = gpu_guard()
    with subprocess.Popen(command, creationflags=guard.CREATE | subprocess.BELOW_NORMAL_PRIORITY_CLASS,
                          env={**os.environ, "YAMYAM_ELDEN_LIBRARY_JOB": str(job)}) as child:
        worker.update(child=guard.identity(child.pid))
        try:
            process = psutil.Process(child.pid)
            process.cpu_affinity(process.cpu_affinity()[-4:])
        except psutil.NoSuchProcess:
            pass
        if child.wait():
            raise RuntimeError(f"Software Unity capture failed. See {folder / 'unity.log'}.")
        worker.update(child=None)
    for key in rows:
        proof = read(folder / key / "capture.json")
        assert proof["softwareAdapter"] and "Basic Render Driver" in proof["adapter"], key


def capture_software(work, fp, rows, pilot_only, verified_rig):
    guard = gpu_guard()
    worker = guard.SingleWorker(path=WORK / "software-capture-worker.json")
    worker.acquire()
    try:
        pilot = {key: rows[key] for key in rows if key in pipeline.EXPECTED_PILOTS}
        software_job(worker, work, fp, pilot, pipeline.PILOT, True, verified_rig)
        pipeline.inspect_pilot(pilot, fp)
        if not pilot_only:
            software_job(worker, work, fp, rows, pipeline.CAPTURES, False, verified_rig)
    finally:
        worker.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--software", action="store_true")
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--verified-rig", action="store_true")
    parser.add_argument("--wait-minutes", type=int, default=140)
    args = parser.parse_args()
    if (args.pilot_only or args.verified_rig) and not args.software:
        parser.error("--pilot-only and --verified-rig require --software")
    _, _, rows = selection()
    library.use_main_project()
    if args.verified_rig:
        scope = ("09", "10", "01", "02", "04", "05", "06")
        rows = {f"{number}-{shot}": rows[f"{number}-{shot}"] for number in scope for shot in (1, 3)}
    fp = source_id(rows, args.software)
    work = configure(args.software, fp, args.verified_rig)
    if not args.execute:
        print(json.dumps(dict(fingerprint=fp, episodes=IDS, scenes=len(rows), software=args.software,
                              editorActive=editor_active(), gpuWait=gpu_guard().busy_reason())))
        return
    work.mkdir(parents=True, exist_ok=True)
    if args.software:
        capture_software(work, fp, rows, args.pilot_only, args.verified_rig)
    else:
        pipeline.capture(rows, fp, args.wait_minutes)
    if args.pilot_only:
        print(pipeline.PILOT / "contact-sheet.jpg")
        return
    records = [pipeline.validate_capture(cut, fp) for cut in rows.values()]
    expected_scenes = SCENES.with_name("ScenesV8Rig") if args.verified_rig else SCENES
    for record in records:
        assert Path(record["scenePath"]).parent == expected_scenes
        if args.software:
            assert record["softwareAdapter"]
    save(work / "capture-receipt.json", dict(fingerprint=fp, software=args.software, cuts=records))
    print(work / "capture-receipt.json")


if __name__ == "__main__":
    main()
