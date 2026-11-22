"""Recapture Elden Ring episodes 11–36 and assemble the ordered 36-episode PC review."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import time

from PIL import Image, ImageChops, ImageDraw, ImageStat
import psutil

import capture_walkthrough_v8 as capture
import render_walkthrough_v8 as render
from make_approved_voice_v2 import HERE, read, save, sha

IDS = tuple(f"{number:02d}" for number in range(1, 37))
NEW = IDS[10:]
FIRST_TEN = capture.OUT.with_name("pc-review-v9")
OUT = capture.OUT.with_name("pc-review-v10")
WORK = capture.WORK.with_name("elden-ring-development-36-observed-v10")
VERSION = "observed-gameplay-v10"
ANALYSIS = tuple(HERE / f"observations-{part}-v10.json" for part in ("11-19", "20-28", "29-36"))
SCENES = capture.SCENES.with_name("ScenesV10")
WORKER = capture.WORK / "software-capture-worker.json"


def original_media(number):
    return read(render.V6 / number / "verification.json")


def load_observations():
    rows = [item for path in ANALYSIS for item in read(path)["episodes"]]
    assert tuple(item["id"] for item in rows) == NEW
    assets = {}
    for row in rows:
        number = row["id"]
        original = original_media(number)
        assert row["unityApplication"].strip(), number
        assert set(row["guides"]) == {"1", "3"}, number
        assert all(len(steps) == 3 and all(step.strip() for step in steps)
                   for steps in row["guides"].values()), number
        assert [item["index"] for item in row["cuts"]] == [0, 2], number
        for found in row["cuts"]:
            index = found["index"]
            cut = original["cuts"][index]
            source = Path(original["formatSources"][index]["source"])
            assert found["sha256"] == cut["sha256"] and cut["type"] == "gameplay", (number, index)
            assert (found["start"], found["end"]) == (cut["start"], cut["end"]), (number, index)
            assert found["observation"].strip() and cut["rights"].strip()
            if source not in assets:
                source_info = render.film.edit.probe(source)
                stream = source_info["streams"][0]
                assert stream["width"] >= 1920 and stream["height"] >= 1080, source
                assets[source] = (sha(source), float(source_info["format"]["duration"]))
            source_hash, duration = assets[source]
            assert source_hash == found["sha256"] and found["end"] <= duration, (number, index)
            if change := found.get("replacement"):
                assert 0 <= change["start"] < change["end"] <= duration
                assert abs((change["end"] - change["start"]) * 60 - cut["frames"]) < .05
                assert change["observation"].strip()
    return {item["id"]: item for item in rows}


def production_inputs():
    observations = load_observations()
    _, _, rows = capture.pipeline.load_plan()
    rows = {key: cut for key, cut in rows.items() if key[:2] in NEW}
    assert len(rows) == 52
    sources = {path.name: sha(path) for path in ANALYSIS}
    identity = {"unity": capture.source_id(rows, True), "observations": sources,
                "capture": sha(Path(__file__)), "softwareLauncher": sha(Path(capture.__file__))}
    fingerprint = sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    work = WORK / fingerprint[:12]
    capture.pipeline.NATIVE = capture.PROJECT
    capture.pipeline.CAPTURES = work / "captures"
    capture.pipeline.PILOT = work / "pilot"
    return rows, observations, work, fingerprint, sources


def wait_for_editor(timeout_minutes):
    deadline = time.monotonic() + 60 * timeout_minutes
    previous = None
    while True:
        reason = ("another Unity session is active" if capture.editor_active() else
                  "less than 12 GiB of physical memory available" if
                  psutil.virtual_memory().available < 12 * 1024**3 else None)
        if reason is None:
            return
        if reason != previous:
            print(f"Unity software capture waiting: {reason}", flush=True)
            previous = reason
        if time.monotonic() >= deadline:
            raise RuntimeError(f"Unity software renderer unavailable: {reason}")
        time.sleep(15)


def make_contact_sheets(folder, keys, fingerprint):
    for group in range(0, len(keys), 8):
        sheet = Image.new("RGB", (930, 223 * min(8, len(keys) - group)), "#17242a")
        draw = ImageDraw.Draw(sheet)
        for row, key in enumerate(keys[group:group + 8]):
            receipt = read(folder / key / "capture.json")
            assert receipt["fingerprint"] == fingerprint and receipt["pilot"] and receipt["softwareAdapter"]
            paths = sorted((folder / key).glob("frame-*.png"))
            assert len(paths) == 3
            pictures = []
            for index, path in enumerate(paths):
                with Image.open(path) as raw:
                    assert raw.size == capture.pipeline.WINDOW
                    picture = raw.convert("RGB")
                picture.thumbnail((302, 202))
                assert max(ImageStat.Stat(picture).stddev) > 12, key
                pictures.append(picture)
                sheet.paste(picture, (index * 310 + 4, row * 223 + 19))
            assert max(max(ImageStat.Stat(ImageChops.difference(pictures[0], p)).mean)
                       for p in pictures[1:]) > .35, key
            draw.text((7, row * 223 + 3), key, fill="white")
        sheet.save(folder / f"sheet-{group // 8 + 1:02d}.jpg", quality=90)


def capture_observed(rows, work, fingerprint, pilot_only, wait_minutes):
    capture.library.use_main_project()
    guard = capture.gpu_guard()
    worker = guard.SingleWorker(path=WORKER)
    worker.acquire()
    try:
        work.mkdir(parents=True, exist_ok=True)
        wait_for_editor(wait_minutes)
        capture.software_job(worker, work, fingerprint, rows, capture.pipeline.PILOT, True,
                             False, observed_v10=True)
        make_contact_sheets(capture.pipeline.PILOT, tuple(rows), fingerprint)
        if pilot_only:
            print(f"Pilot verified: {capture.pipeline.PILOT}", flush=True)
            return
        wait_for_editor(wait_minutes)
        capture.software_job(worker, work, fingerprint, rows, capture.pipeline.CAPTURES, False,
                             False, observed_v10=True)
        receipts = {key: validated_capture(cut, fingerprint) for key, cut in rows.items()}
        save(work / "capture-receipt.json", {"fingerprint": fingerprint, "cuts": receipts})
        print(f"Captured and checked {len(receipts)} Unity cuts: {work}", flush=True)
    finally:
        worker.close()


def validated_capture(cut, fingerprint):
    capture_record = capture.pipeline.validate_capture(cut, fingerprint)
    assert capture_record["softwareAdapter"] and Path(capture_record["scenePath"]).parent == SCENES
    return capture_record


def await_cut_records(number, rows, fingerprint, follow):
    part = {key: cut for key, cut in rows.items() if key[:2] == number}
    guard = capture.gpu_guard()
    while not all((capture.pipeline.CAPTURES / key / "capture.json").is_file() for key in part):
        if not follow or not WORKER.is_file() or not guard.alive(read(WORKER)):
            raise RuntimeError(f"Capture not ready for episode {number}.")
        time.sleep(4)
    return {key: validated_capture(cut, fingerprint) for key, cut in part.items()}


def verify_media(folder, record, decode):
    frames = sum(cut["frames"] for cut in record["cuts"])
    assert len(record["cuts"]) == 4 or len(record["cuts"]) == 5 and record["cuts"][-1]["frames"] == 600
    assert record["cuts"][0]["frames"] == record["cuts"][1]["frames"]
    assert record["cuts"][2]["frames"] == record["cuts"][3]["frames"]
    assert frames == round(record["seconds"] * 60)
    for name in ("clean", "captioned"):
        identity = record[name]
        path = folder / identity["path"]
        assert sha(path) == identity["sha256"] and identity["frames"] == frames
        if decode:
            stream = render.film.edit.probe(path)["streams"][0]
            assert (stream["width"], stream["height"], stream["avg_frame_rate"], int(stream["nb_frames"])) == (
                1080, 1920, "60/1", frames)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-threads", "2", "-i", str(path),
                            "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
                           capture_output=True, check=True)
    for lang in ("ko", "en"):
        assert sha(folder / f"{lang}.srt") == record["subtitles"][lang]


def verify_new(number, folder, fingerprint):
    record = read(folder / "verification.json")
    assert record["reviewVersion"] == VERSION and record["unityFingerprint"] == fingerprint, number
    assert len(record["cuts"]) == 4 and record["gameplaySeconds"] == record["explanationSeconds"]
    assert record["audio"] == original_media(number)["audio"]
    assert record["subtitles"] == original_media(number)["subtitles"]
    for index in (1, 3):
        piece = record["cuts"][index]
        identity = piece["unity"]
        assert identity["id"] == f"{number}-{index}" and identity["softwareAdapter"]
        assert sha(Path(identity["scenePath"])) == identity["sceneSha256"]
        assert sha(Path(identity["path"])) == identity["sha256"]
        assert piece["frames"] == identity["frames"] and piece["walkthroughGuide"]["labels"]
    verify_media(folder, record, decode=True)
    save(folder / "decode-check.json", {
        "fingerprint": fingerprint, "verificationSha256": sha(folder / "verification.json"),
        "cleanSha256": record["clean"]["sha256"], "captionedSha256": record["captioned"]["sha256"],
    })
    print(f"{number}: both complete masters decoded", flush=True)


def compose(rows, observations, work, fingerprint, follow):
    render.OUT = OUT
    render.VERSION = VERSION
    render.GUIDES.update({f"{n}-{shot}": steps for n, row in observations.items()
                          for shot, steps in row["guides"].items()})
    contract = read(render.film.FORMAT)
    paragraphs = read(render.film.CAPTIONS)["paragraphs"]
    with ThreadPoolExecutor(max_workers=1) as pool:
        checks = []
        for number, row in observations.items():
            captures = await_cut_records(number, rows, fingerprint, follow)
            replacements = {cut["index"]: (cut["replacement"]["start"], cut["replacement"]["observation"])
                            for cut in row["cuts"] if "replacement" in cut}
            folder = render.render_episode(number, rows, captures, contract, paragraphs, work / "composition",
                                            gameplay_windows=replacements)
            checks.append(pool.submit(verify_new, number, folder, fingerprint))
        for check in checks:
            check.result()


class ReviewLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.media = []
        self.videos = []
        self.scenes = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value and value.endswith((".mp4", ".srt")):
                self.media.append(value)
                if tag == "video":
                    self.videos.append(value)
            if key == "href" and value and value.endswith(".unity"):
                self.scenes.append(value)


def card_for(page, number):
    card = re.search(rf'<article id="ep{number}">.*?</article>', page, re.DOTALL)
    assert card, number
    return card.group()


def revised_card(page, number, row, record):
    card = card_for(page, number)
    card = card.replace(f"../pc-review-v6/{number}/", f"{number}/")
    note = "<p>" + escape(row["unityApplication"]) + "</p>"
    card = card.replace("</h2>", "</h2>" + note, 1)
    details = ['<details><summary>시연 장면과 편집 가능한 Unity 씬</summary>']
    frame = 0
    for index, cut in enumerate(record["cuts"]):
        if index in (1, 3):
            guide = cut["walkthroughGuide"]
            details.append("<ol>")
            for mark, line in zip(guide["phaseFrames"], guide["labels"]):
                details.append(f'<li><button data-position="{(mark + frame)/60:.6f}">재생</button> {escape(line)}</li>')
            scene = escape(Path(cut["unity"]["scenePath"]).as_uri(), quote=True)
            details.append(f'</ol><p><a href="{scene}">Unity 씬</a></p>')
        frame += cut["frames"]
    details.append("</details>")
    card, count = re.subn(r"<details><summary>시연 단계와 장면으로 이동</summary>.*?</details>",
                          lambda _: "".join(details), card, count=1, flags=re.DOTALL)
    assert count == 1, number
    original = original_media(number)
    observations = ['<details><summary>실제 플레이에서 확인한 동작과 시야</summary><ul>']
    for shot in row["cuts"]:
        selected = shot.get("replacement", shot)
        index = shot["index"]
        url = escape(original["cuts"][index]["url"], quote=True)
        text = escape(selected["observation"])
        observations.append(f'<li>{selected["start"]:g}~{selected["end"]:g}초 · {text} <a href="{url}">플레이 출처</a></li>')
    observations.append("</ul></details>")
    return card.replace("</article>", "".join(observations) + "</article>")


def combine_review(observations, work, fingerprint, sources):
    first = read(FIRST_TEN / "manifest.json")
    first_proof = read(HERE / "review-receipt-v9.json")
    assert sha(FIRST_TEN / "index.html") == first["reviewPageSha256"] == first_proof["reviewPageSha256"]
    assert sha(FIRST_TEN / "manifest.json") == first_proof["manifestSha256"]
    assert tuple(first["episodes"]) == IDS[:10] and first_proof["fullMasterDecodes"] == 20
    source = (FIRST_TEN / "index.html").read_text(encoding="utf-8")
    prior = (render.V7 / "index.html").read_text(encoding="utf-8")
    captures = read(work / "capture-receipt.json")
    assert captures["fingerprint"] == fingerprint and len(captures["cuts"]) == 52
    records, cards, proof = {}, [], []
    for number in IDS:
        if number not in observations:
            entry = first["episodes"][number]
            folder = FIRST_TEN / entry["localFolder"]
            record = entry["record"]
            assert record == read(folder / "verification.json")
            verify_media(folder, record, decode=False)
            card = re.sub(r'(href|src)="((?:\d\d(?:-final)?/|09-walkthrough-sample\.mp4)[^"]*)"',
                          r'\1="../pc-review-v9/\2"', card_for(source, number))
        else:
            folder = OUT / number
            record = read(folder / "verification.json")
            decoded = read(folder / "decode-check.json")
            assert decoded["fingerprint"] == fingerprint
            assert decoded["verificationSha256"] == sha(folder / "verification.json")
            assert decoded["cleanSha256"] == record["clean"]["sha256"]
            assert decoded["captionedSha256"] == record["captioned"]["sha256"]
            verify_media(folder, record, decode=False)
            card = revised_card(prior, number, observations[number], record)
        cards.append(card)
        records[number] = {"localFolder": folder.as_posix(), "record": record}
        proof.append({"id": number, "durationSeconds": record["seconds"],
                      "reviewFolder": folder.as_posix(), "verificationSha256": sha(folder / "verification.json"),
                      "cleanSha256": record["clean"]["sha256"], "captionedSha256": record["captioned"]["sha256"],
                      "subtitles": record["subtitles"],
                      "unityScenes": [record["cuts"][i]["unity"]["scenePath"] for i in (1, 3)]})
    header = source.split("<nav", 1)[0]
    header = re.sub(r"<title>.*?</title>", "<title>엘든 링 36편 PC 검수</title>", header)
    header = re.sub(r"<h1>.*?</h1>", "<h1>엘든 링 36편 PC 검수</h1>", header)
    footer = source.split("</main>", 1)[1]
    nav = '<nav aria-label="편 번호">' + " ".join(f'<a href="#ep{n}">{n}</a>' for n in IDS) + "</nav>"
    document = header + nav + "<main>" + "".join(cards) + "</main>" + footer
    assert tuple(re.findall(r'<article id="ep(\d\d)">', document)) == IDS
    links = ReviewLinks()
    links.feed(document)
    assert len(links.videos) == 36 and len(set(links.media)) == 145 and len(links.scenes) == 72
    for value in links.media:
        assert (OUT / value).is_file(), value
    page = OUT / "index.html"
    draft = page.with_suffix(".tmp")
    draft.write_text(document, encoding="utf-8")
    draft.replace(page)
    manifest = OUT / "manifest.json"
    save(manifest, {"reviewVersion": VERSION, "episodes": records, "observations": observations,
                    "reviewPageSha256": sha(page)})
    summary = {"reviewVersion": VERSION, "episodeCount": 36, "preservedFirstTen": 10,
               "newUnityCuts": 52, "observedGameplayCuts": 52, "newMastersDecoded": 52,
               "totalSeconds": sum(item["durationSeconds"] for item in proof),
               "reviewPage": page.as_posix(), "reviewPageSha256": sha(page), "manifestSha256": sha(manifest),
               "unityFingerprint": fingerprint, "analysisSources": sources, "episodes": proof,
               "humanReview": "pending", "publicationAuthorized": False}
    save(OUT / "audit.json", summary)
    save(HERE / "review-receipt-v10.json", summary)
    print(f"36 local review videos verified: {page}", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("status", "pilot", "capture", "compose", "review"))
    parser.add_argument("--wait-minutes", type=int, default=180)
    parser.add_argument("--follow", action="store_true")
    args = parser.parse_args()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    rows, observations, work, fingerprint, sources = production_inputs()
    if args.stage == "status":
        print(json.dumps({"episodes": len(observations), "cuts": len(rows), "fingerprint": fingerprint,
                          "editorBusy": capture.editor_active(), "work": str(work)}, ensure_ascii=False))
    elif args.stage in ("pilot", "capture"):
        capture_observed(rows, work, fingerprint, args.stage == "pilot", args.wait_minutes)
    elif args.stage == "compose":
        compose(rows, observations, work, fingerprint, args.follow)
    else:
        combine_review(observations, work, fingerprint, sources)


if __name__ == "__main__":
    main()
