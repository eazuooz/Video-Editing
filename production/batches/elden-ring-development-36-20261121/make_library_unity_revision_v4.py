"""Render only the selected Elden Ring cuts from the actual VideoEditing Unity project."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import make_unity_revision_v3 as pipeline
from make_approved_voice_v2 import DEFAULT_OUTPUT, HERE, ROOT, read, resource_guard, save, sha

PROJECT = ROOT / "unity/VideoEditing"
SCENE_ROOT = PROJECT / "Assets/VideoScenes/EldenRingDevelopment36/AssetLibraryV4"
WORK = Path("D:/YamyamProduction/elden-ring-development-36-library-v4")
OUT = DEFAULT_OUTPUT.with_name("pc-review-v4")
ASSET_PLAN = HERE / "asset-plan-v4.json"
PILOT_ONLY = False


def selected_assets():
    assets = read(ASSET_PLAN)["assetRecords"]
    assert len(assets) == 18 and len({a["role"] for a in assets}) == len(assets)
    for asset in assets:
        path = PROJECT / asset["assetPath"]
        meta = path.with_suffix(path.suffix + ".meta")
        assert path.resolve().is_relative_to((PROJECT / "Assets/ThirdParty/YamyamAssetLibrary").resolve())
        assert sha(path) == asset["assetSha256"] and sha(meta) == asset["metaSha256"]
        assert f"guid: {asset['guid']}" in meta.read_text(encoding="utf-8-sig")
    return {a["role"]: a for a in assets}


def source_id(rows):
    scripts = {p.relative_to(PROJECT).as_posix(): sha(p) for p in SCENE_ROOT.rglob("*")
               if p.is_file() and p.suffix in (".cs", ".shader") and not p.stem.endswith("V8")
               and not p.stem.startswith("EldenRingObserved")}
    assert len(scripts) == 8
    inputs = dict(cuts=rows, scripts=scripts, assetPlan=sha(ASSET_PLAN),
                  editor=sha(PROJECT / "ProjectSettings/ProjectVersion.txt"),
                  graphics=sha(PROJECT / "ProjectSettings/GraphicsSettings.asset"),
                  quality=sha(PROJECT / "ProjectSettings/QualitySettings.asset"))
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode("utf-8")).hexdigest()


def scoped_guard():
    guard = resource_guard()
    guard.OWNER = "elden-ring-development-36-library-v4"
    guard.PROTOCOL = "elden-ring-main-unity-library-capture-v4"
    return guard


def use_main_project():
    assert SCENE_ROOT.is_dir() and (PROJECT / "Assets/ThirdParty/YamyamAssetLibrary").is_dir()
    selected_assets()


def capture_in_project(guard, worker, lease, fp, rows, folder, pilot, *, work=None, walkthrough=False):
    if PILOT_ONLY and not pilot:
        return
    if pilot and all((folder / key / "capture.json").is_file() and
                     read(folder / key / "capture.json")["fingerprint"] == fp for key in rows):
        return
    folder.mkdir(parents=True, exist_ok=True)
    job = (work or WORK) / ("pilot-job.json" if pilot else "capture-job.json")
    save(job, dict(output=str(folder), ffmpeg=shutil.which("ffmpeg"), fingerprint=fp, project=str(PROJECT),
                   pilot=pilot, walkthroughV8=walkthrough, cuts=list(rows.values()),
                   assets=list(selected_assets().values())))
    current = read(guard.LEASE)
    assert guard.ours(current) and current["token"] == lease
    current.update(phase="launching", child=None, output=str(folder))
    guard.save(guard.LEASE, current)
    command = [str(pipeline.EDITOR), "-batchmode", "-force-d3d11", "-job-worker-count", "4",
               "-projectPath", str(PROJECT), "-executeMethod", "Yamyam.EldenRingLibraryLessons.LibraryCapture.Run",
               "-eldenFingerprint", fp, "-eldenOutput", str(folder), "-logFile", str(folder / "unity.log")]
    child = subprocess.Popen(command, creationflags=guard.CREATE,
                             env={**os.environ, "YAMYAM_ELDEN_LIBRARY_JOB": str(job)})
    child_id = guard.identity(child.pid)
    worker.update(child=child_id)
    current.update(phase="running", child=child_id)
    guard.save(guard.LEASE, current)
    pipeline.work_state("main-project-pilot" if pilot else "main-project-capturing", fp, child=child_id)
    if child.wait():
        raise RuntimeError(f"Unity capture failed. Editor log: {folder / 'unity.log'}")
    worker.update(child=None)
    current.update(phase="reserved", child=None)
    guard.save(guard.LEASE, current)


def configure():
    pipeline.NATIVE = PROJECT
    pipeline.WORK = WORK
    pipeline.CAPTURES = WORK / "captures"
    pipeline.PILOT = WORK / "pilot"
    pipeline.STATE = WORK / "progress-v4.json"
    pipeline.OUTPUT = OUT
    pipeline.scoped_guard = scoped_guard
    pipeline.stage_project = use_main_project
    pipeline.native_job = capture_in_project
    pipeline.EXPECTED_PILOTS = {"12-1", "14-3", "15-1", "15-3", "26-3", "29-3"}


def finish(plan, labels, rows, fp, assets):
    OUT.mkdir(parents=True, exist_ok=True)
    captures = {key: pipeline.validate_capture(cut, fp) for key, cut in rows.items()}
    for key, capture in captures.items():
        assert Path(capture["scenePath"]).resolve().is_relative_to(SCENE_ROOT.resolve())
        roles = capture["libraryRoles"]
        assert roles and len(roles) == len(set(roles)) and set(roles) <= set(assets), key
        scene = Path(capture["scenePath"]).read_text(encoding="utf-8")
        assert all(assets[role]["guid"] in scene for role in roles), key
        capture["assetRecords"] = [assets[role] for role in roles]
        capture["sharedAssetPaths"] = [assets[role]["assetPath"] for role in roles]
    results = []
    for episode in plan:
        number = episode["id"]
        report = pipeline.compose(episode, labels[number], rows, captures, fp)
        assert report["gameplaySeconds"] == report["explanationSeconds"]
        verification = OUT / number / "verification.json"
        if any(report["cuts"][index]["picture"] != "native-unity-library-v4" for index in (1, 3)):
            for index in (1, 3):
                report["cuts"][index]["picture"] = "native-unity-library-v4"
            save(verification, report)
        results.append(dict(id=number, seconds=report["seconds"], captioned=report["captioned"],
                            clean=report["clean"], captions=report["subtitles"],
                            cuts=[captures[f"{number}-{index}"] for index in (1, 3)]))
        pipeline.work_state("compositing", fp)
    assert len(results) == 36 and len(captures) == 72
    pipeline.edit.review_page(OUT, approved_voice=True, native_unity=True, asset_library=True)
    page = OUT / "index.html"
    links = pipeline.ReviewLinks(OUT)
    links.feed(page.read_text(encoding="utf-8"))
    assert links.media == [f"{episode['id']}/captioned.mp4" for episode in plan]
    proof = dict(reviewVersion="unity-shared-assets-v4", count=36, assetLibraryCuts=72, gameplayCutsPreserved=72,
                 audioTracksPreserved=72, unityProject=PROJECT.as_posix(), unityFingerprint=fp,
                 assetPlanSha256=sha(ASSET_PLAN), totalSeconds=sum(r["seconds"] for r in results),
                 reviewPage=page.as_posix(), reviewPageSha256=sha(page), manifestSha256=sha(OUT / "manifest.json"),
                 humanReview="pending", results=results)
    save(OUT / "audit.json", proof)
    pipeline.work_state("complete-local-pc-review", fp, reviewPage=str(page))
    print(f"Verified 36 VideoEditing shared-asset videos: {page}", flush=True)


def main():
    global PILOT_ONLY
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--finish-only", action="store_true")
    parser.add_argument("--wait-minutes", type=int, default=140)
    args = parser.parse_args()
    PILOT_ONLY = args.pilot_only
    configure()
    plan, labels, rows = pipeline.load_plan()
    assets = selected_assets()
    fp = source_id(rows)
    if not args.execute and not args.finish_only and not args.pilot_only:
        print(json.dumps(dict(project=str(PROJECT), episodes=len(plan), cuts=len(rows),
                              sharedAssets=len(assets), fingerprint=fp, resourceWait=scoped_guard().busy_reason()),
                         ensure_ascii=False))
        return
    WORK.mkdir(parents=True, exist_ok=True)
    try:
        if not args.finish_only and len(list(pipeline.CAPTURES.glob("??-?/capture.json"))) != len(rows):
            pipeline.capture(rows, fp, args.wait_minutes)
        if PILOT_ONLY:
            pipeline.work_state("pilot-ready", fp, preview=str(pipeline.PILOT / "contact-sheet.jpg"))
            return
        finish(plan, labels, rows, fp, assets)
    except Exception as error:
        pipeline.work_state("incomplete", fp, reason=str(error))
        raise


if __name__ == "__main__":
    main()
