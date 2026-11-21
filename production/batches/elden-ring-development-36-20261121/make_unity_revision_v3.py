"""Capture the 72 Unity explanation cuts and deliver the exact 36-video PC revision."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid

from PIL import Image, ImageChops, ImageDraw, ImageStat

import build_pc_review as edit
from finalize_approved_review_v2 import ReviewLinks, track_sha
from make_approved_voice_v2 import DEFAULT_OUTPUT, HERE, ROOT, pinned_plan, read, resource_guard, save, sha

PRIOR = DEFAULT_OUTPUT
OUTPUT = PRIOR.with_name("pc-review-v3")
WORK = Path("D:/YamyamProduction/elden-ring-development-36-unity-v3")
NATIVE = WORK / "UnityProject"
SOURCE = HERE / "unity-v3"
CAPTURES = WORK / "captures"
PILOT = WORK / "pilot"
STATE = WORK / "progress-v3.json"
EDITOR = Path("C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe")
EXPECTED_PILOTS = {"01-1", "02-3", "03-3", "07-3", "26-3", "29-3"}
WINDOW = (950, 650)


def source_files():
    return sorted(path for path in SOURCE.rglob("*") if path.is_file() and
                  path.suffix in {".cs", ".shader", ".json", ".txt", ".meta", ".unity"})


def load_plan():
    plan = pinned_plan()
    lessons = read(HERE / "unity-lessons-v3.json")
    baseline = read(HERE / "review-receipt-v2.json")
    audit = read(PRIOR / "audit.json")
    assert baseline["manifestSha256"] == audit["manifestSha256"] == sha(PRIOR / "manifest.json")
    assert baseline["reviewPageSha256"] == audit["reviewPageSha256"] == sha(PRIOR / "index.html")
    assert set(lessons) == {e["id"] for e in plan}
    rows = {}
    for episode in plan:
        number = episode["id"]
        earlier = read(PRIOR / number / "verification.json")
        assert len(lessons[number]) == 2
        position = 0
        for index, cut in enumerate(earlier["cuts"]):
            assert cut["type"] == ("explanation" if index in (1, 3) else "gameplay")
            if index in (1, 3):
                a, b = cut["subtitleFrames"]
                rows[f"{number}-{index}"] = dict(id=f"{number}-{index}", episode=int(number), shot=index,
                                                  frames=cut["frames"], speechStartFrame=a-position,
                                                  speechEndFrame=b-position)
                assert 0 <= a-position < b-position < cut["frames"]
                assert earlier["cuts"][index-1]["frames"] == cut["frames"]
            position += cut["frames"]
    assert len(rows) == 72 and sum(c["frames"] for c in rows.values()) * 2 == 95880
    return plan, lessons, rows


def fingerprint(rows):
    import hashlib

    inputs = {p.relative_to(SOURCE).as_posix(): sha(p) for p in source_files()}
    assert len(inputs) >= 9
    inputs["original-timings"] = rows
    inputs["lesson-labels"] = sha(HERE / "unity-lessons-v3.json")
    return hashlib.sha256(json.dumps(inputs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def scoped_guard():
    guard = resource_guard()
    guard.OWNER = "elden-ring-development-36-unity-v3"
    guard.PROTOCOL = "elden-ring-unity-principle-capture-v3"
    return guard


def stage_project():
    NATIVE.mkdir(parents=True, exist_ok=True)
    (NATIVE / "ELDEN_RING_PRINCIPLES_CAPTURE").touch()
    for source in source_files():
        target = NATIVE / source.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or source.read_bytes() != target.read_bytes():
            shutil.copy2(source, target)


def native_job(guard, worker, lease, fp, rows, folder, pilot):
    folder.mkdir(parents=True, exist_ok=True)
    job = WORK / ("pilot-job.json" if pilot else "capture-job.json")
    save(job, dict(output=str(folder), ffmpeg=shutil.which("ffmpeg"), fingerprint=fp,
                   pilot=pilot, cuts=list(rows.values())))
    current = read(guard.LEASE)
    assert guard.ours(current) and current["token"] == lease
    current.update(phase="launching", child=None, output=str(folder))
    guard.save(guard.LEASE, current)
    command = [str(EDITOR), "-batchmode", "-force-d3d11", "-job-worker-count", "2",
               "-projectPath", str(NATIVE), "-executeMethod", "Yamyam.EldenRingLessons.PrincipleCapture.Run",
               "-eldenFingerprint", fp, "-eldenOutput", str(folder), "-logFile", str(folder / "unity.log")]
    child = subprocess.Popen(command, creationflags=guard.CREATE,
                             env={**os.environ, "YAMYAM_ELDEN_PRINCIPLE_JOB": str(job)})
    child_id = guard.identity(child.pid)
    worker.update(child=child_id)
    current.update(phase="running", child=child_id)
    guard.save(guard.LEASE, current)
    work_state("pilot-capturing" if pilot else "unity-capturing", fp, child=child_id)
    if child.wait():
        raise RuntimeError(f"Unity capture failed. Editor log: {folder / 'unity.log'}")
    worker.update(child=None)
    current.update(phase="reserved", child=None)
    guard.save(guard.LEASE, current)


def work_state(status, fp, **extra):
    save(STATE, dict(status=status, fingerprint=fp, scope="Elden Ring development episodes 01–36",
                     capturedCuts=len(list(CAPTURES.glob("??-?/capture.json"))),
                     reviewDeliverables=len(list(OUTPUT.glob("??/verification.json"))), **extra))


def inspect_pilot(rows, fp):
    sheet = Image.new("RGB", (960, 6 * 232), (12, 23, 32))
    draw = ImageDraw.Draw(sheet)
    for index, key in enumerate(rows):
        local = PILOT / key
        proof = read(local / "capture.json")
        assert proof["fingerprint"] == fp and proof["pilot"]
        files = sorted(local.glob("frame-*.png"))
        assert len(files) == 3
        pictures = [Image.open(image).convert("RGB") for image in files]
        assert all(p.size == WINDOW and max(ImageStat.Stat(p).stddev) > 18 for p in pictures)
        assert max(ImageStat.Stat(ImageChops.difference(pictures[0], p)).mean[0] for p in pictures[1:]) > .7
        for col, picture in enumerate(pictures):
            picture.thumbnail((306, 206))
            sheet.paste(picture, (12 + col * 316, 20 + index * 232))
        draw.text((12, 5 + index * 232), f"{key} · Unity", fill="white")
    sheet.save(PILOT / "contact-sheet.jpg", quality=92)


def capture(rows, fp, wait_minutes):
    guard = scoped_guard()
    worker = guard.SingleWorker(path=WORK / "capture-worker.json")
    worker.acquire()
    lease = None
    try:
        stage_project()
        known = {worker.previous.get("leaseToken")} if worker.previous else set()
        if known:
            guard.recover_own_lease(known)
        deadline = time.monotonic() + wait_minutes * 60
        last_reason = None
        while lease is None:
            reason = guard.busy_reason()
            if reason != last_reason:
                print(f"Unity resource check: {reason or 'ready'}", flush=True)
                last_reason = reason
            work_state("waiting-for-graphics", fp, reason=reason)
            if reason is None:
                token = uuid.uuid4().hex
                current = dict(protocol=guard.PROTOCOL, owner=guard.OWNER, token=token, **guard.identity(),
                               phase="reserved", fingerprint=fp, output=str(CAPTURES), child=None)
                try:
                    with guard.LEASE.open("x", encoding="utf-8") as handle:
                        json.dump(current, handle)
                except FileExistsError:
                    pass
                else:
                    lease = token
                    worker.update(leaseToken=token)
                    break
            if time.monotonic() >= deadline:
                raise RuntimeError(f"The Unity capture window has not opened: {reason}")
            time.sleep(15)
        if reason := guard.busy_reason(lease):
            raise RuntimeError(f"Unity resources changed after reservation: {reason}")
        sample = {key: cut for key, cut in rows.items() if key in EXPECTED_PILOTS}
        native_job(guard, worker, lease, fp, sample, PILOT, True)
        inspect_pilot(sample, fp)
        if reason := guard.busy_reason(lease):
            raise RuntimeError(f"Unity resources changed before the full capture: {reason}")
        native_job(guard, worker, lease, fp, rows, CAPTURES, False)
    finally:
        if lease and guard.LEASE.exists():
            record = read(guard.LEASE)
            if guard.ours(record) and record["token"] == lease and not guard.alive(record.get("child")):
                guard.LEASE.unlink()
        worker.close()


def validate_capture(cut, fp):
    folder = CAPTURES / cut["id"]
    record = read(folder / "capture.json")
    movie = folder / "unity.mp4"
    scene = NATIVE / record["scene"]
    assert record["fingerprint"] == fp and record["id"] == cut["id"] and not record["pilot"]
    assert (record["width"], record["height"], record["fps"], record["frames"]) == (*WINDOW, 60, cut["frames"])
    assert scene.is_file() and movie.is_file() and record["backend"] == "Direct3D11"
    assert "Principle camera" in scene.read_text(encoding="utf-8")
    stream = edit.probe(movie)["streams"][0]
    assert (int(stream["nb_frames"]), stream["avg_frame_rate"], stream["width"], stream["height"]) == (
        cut["frames"], "60/1", *WINDOW)
    first, last = cut["speechStartFrame"], cut["speechEndFrame"]
    middle = (first + last) // 2
    raw = edit.run("ffmpeg", "-v", "error", "-i", movie,
                   "-vf", f"select=eq(n\\,{first})+eq(n\\,{middle})+eq(n\\,{last}),scale=160:110",
                   "-fps_mode", "passthrough", "-c:v", "rawvideo", "-pix_fmt", "rgb24", "-f", "rawvideo", "-")
    stride = 160 * 110 * 3
    assert len(raw) == stride * 3
    earlier, during, later = (Image.frombytes("RGB", (160, 110), raw[n*stride:(n+1)*stride]) for n in range(3))
    motion = max(max(ImageStat.Stat(ImageChops.difference(earlier, picture)).mean) for picture in (during, later))
    assert motion > .5, f"The Unity lesson has insufficient state changes: {cut['id']} ({motion:.3f})"
    return record | {"path": str(movie), "sha256": sha(movie), "sceneSha256": sha(scene),
                     "scenePath": str(scene), "motionEvidence": round(motion, 4)}


def explanation(episode, cut, demo, with_captions, label, destination):
    clip = Path(demo["path"])
    plate = destination.with_suffix(".png")
    shot = int(cut["id"][-1])
    edit.card(episode, shot, None, clip, with_captions, plate)
    with Image.open(plate) as source:
        art = source.convert("RGB")
    draw = ImageDraw.Draw(art)
    draw.rectangle((60, 399, 1019, 455), fill=edit.BG)
    draw.text((65, 409), "Unity 원리 시연 · 자체 제작", font=edit.font(34), fill=edit.TEAL)
    for n, line in enumerate(edit.wrap(draw, label, edit.font(43), 933)):
        draw.text((66, 1165 + 55*n), line, font=edit.font(43), fill=edit.TEXT)
    art.save(plate)
    filters = ("[0:v]format=yuv420p[plate];[1:v]setsar=1[unity];"
               "[plate][unity]overlay=x=65:y=468:shortest=1[out]")
    edit.ffmpeg("-loop", 1, "-framerate", 60, "-i", plate, "-i", clip,
                "-filter_complex_threads", 2, "-filter_complex", filters, "-map", "[out]", "-an",
                "-frames:v", cut["frames"], "-c:v", "libx264", "-threads", 4, "-preset", "ultrafast",
                "-crf", 19, "-pix_fmt", "yuv420p", destination)


def packet_fingerprints(path):
    entries = json.loads(edit.run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
                                  "-show_data_hash", "SHA256", "-show_entries", "packet=data_hash", "-of", "json", path))
    return [packet["data_hash"] for packet in entries["packets"]]


def decoded_range(path, start, frames):
    return edit.run("ffmpeg", "-v", "error", "-ss", f"{start / 60:.6f}", "-i", path,
                    "-map", "0:v:0", "-frames:v", frames, "-f", "hash", "-hash", "sha256", "-")


def compose(episode, labels, plan, demos, fp):
    number = episode["id"]
    folder = OUTPUT / number
    folder.mkdir(parents=True, exist_ok=True)
    prior = PRIOR / number
    record = read(prior / "verification.json")
    proof = folder / "verification.json"
    if proof.exists():
        saved = read(proof)
        assert saved["unityFingerprint"] == fp
        assert all(sha(folder / saved[k]["path"]) == saved[k]["sha256"] for k in ("clean", "captioned"))
        return saved
    frames = sum(c["frames"] for c in record["cuts"])
    for flavor in ("clean", "captioned"):
        before = prior / f"{flavor}.mp4"
        assert sha(before) == record[flavor]["sha256"]
        cuts = (prior / f"{flavor}.txt").read_text(encoding="utf-8").splitlines()
        assert len(cuts) == 4
        assert all(re.fullmatch(r"file '[^']+'", line) for line in cuts)
        for index, label in zip((1, 3), labels, strict=True):
            key = f"{number}-{index}"
            shot = folder / f"{index}-{flavor}.mp4"
            explanation(episode, plan[key], demos[key], flavor == "captioned", label, shot)
            cuts[index] = f"file '{shot.as_posix()}'"
        listing = folder / f"{flavor}.txt"
        listing.write_text("\n".join(cuts) + "\n", encoding="utf-8")
        movie = folder / f"{flavor}.mp4"
        edit.ffmpeg("-f", "concat", "-safe", 0, "-i", listing, "-i", before,
                    "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart", movie)
        preserved_audio = track_sha(movie, "a") == track_sha(before, "a")
        assert preserved_audio
        prior_packets, actual_packets = packet_fingerprints(before), packet_fingerprints(movie)
        assert len(prior_packets) == len(actual_packets) == frames
        position = 0
        for cut in record["cuts"]:
            end = position + cut["frames"]
            if cut["type"] == "gameplay" and prior_packets[position:end] != actual_packets[position:end]:
                assert decoded_range(before, position, cut["frames"]) == decoded_range(movie, position, cut["frames"])
            position = end
        record[flavor] = edit.validate(movie, frames)
    for language in ("ko", "en"):
        filename = f"{language}.srt"
        assert sha(prior / filename) == record["subtitles"][language]
        shutil.copy2(prior / filename, folder / filename)
        assert sha(folder / filename) == record["subtitles"][language]
    for child in (1, 3):
        key = f"{number}-{child}"
        record["cuts"][child].update(demonstration=demos[key]["path"], sha256=demos[key]["sha256"],
                                     unity=demos[key], picture="native-unity-principle-v3")
    record.update(unityFingerprint=fp, previousVoiceAndMusicPreserved=True, previousGameplayPreserved=True)
    save(proof, record)
    print(f"{number}: two Unity cuts; {record['gameplaySeconds']:g}s + {record['explanationSeconds']:g}s", flush=True)
    return record


def finish(plan, lessons, rows, fp):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    demos = {key: validate_capture(cut, fp) for key, cut in rows.items()}
    results = []
    for episode in plan:
        number = episode["id"]
        results.append(compose(episode, lessons[number], rows, demos, fp))
        work_state("compositing", fp)
    assert len(results) == 36 and all(r["gameplaySeconds"] == r["explanationSeconds"] for r in results)
    edit.review_page(OUTPUT, approved_voice=True, native_unity=True)
    page = OUTPUT / "index.html"
    links = ReviewLinks(OUTPUT)
    links.feed(page.read_text(encoding="utf-8"))
    assert links.media == [f"{episode['id']}/captioned.mp4" for episode in plan]
    result = dict(reviewVersion="unity-principles-v3", count=36, nativeExplanationCuts=72,
                  gameplayCutsPreserved=72, audioTracksPreserved=72, previousReview=str(PRIOR / "index.html"),
                  reviewPage=page.as_posix(), reviewPageSha256=sha(page), manifestSha256=sha(OUTPUT / "manifest.json"),
                  unityFingerprint=fp, totalSeconds=sum(r["seconds"] for r in results), humanReview="pending",
                  results=[dict(id=episode["id"], seconds=result["seconds"], captioned=result["captioned"],
                                clean=result["clean"], captions=result["subtitles"],
                                cuts=[demos[f"{episode['id']}-{cut}"] for cut in (1, 3)])
                           for episode, result in zip(plan, results, strict=True)])
    save(OUTPUT / "audit.json", result)
    work_state("complete-local-pc-review", fp, reviewPage=str(page))
    print(f"Verified 36 Unity revision videos in {page}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--finish-only", action="store_true")
    parser.add_argument("--wait-minutes", type=int, default=150)
    args = parser.parse_args()
    plan, lessons, rows = load_plan()
    fp = fingerprint(rows)
    if not args.execute and not args.finish_only:
        print(json.dumps(dict(episodes=len(plan), explanationCuts=len(rows), fingerprint=fp,
                              resourceWait=scoped_guard().busy_reason()), ensure_ascii=False))
        return
    WORK.mkdir(parents=True, exist_ok=True)
    try:
        if not args.finish_only:
            if len(list(CAPTURES.glob("??-?/capture.json"))) != len(rows):
                capture(rows, fp, args.wait_minutes)
        finish(plan, lessons, rows, fp)
    except Exception as error:
        work_state("incomplete", fp, reason=str(error))
        raise


if __name__ == "__main__":
    main()
