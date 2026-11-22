"""Compose and verify the 01–10 Elden Ring walkthrough for local PC review."""
import argparse
from copy import deepcopy
from html import escape
import math
from pathlib import Path
import re
import shutil
import time

from PIL import Image, ImageDraw
import psutil

import capture_walkthrough_v8 as capture
import render_established_format_v6 as film
from make_approved_voice_v2 import HERE, read, save, sha

V6 = capture.OUT.with_name("pc-review-v6")
V7 = capture.OUT.with_name("pc-review-v7")
OUT = capture.OUT
PRIOR_BATCH = capture.OUT
VERSION = "walkthrough-v8"
GUIDES = {
    "01-1": ("어느 칸에 있나", "캐릭터와 가까운 칸을 불러오기", "먼 칸은 비워 두기"),
    "01-3": ("이동 시작", "캐릭터를 따라 로딩 범위 이동", "새로 가까워진 칸을 불러오기"),
    "02-1": ("청록 원에서 출발", "안개 사이로 탑에 접근", "노란 원이 탑 입구"),
    "02-3": ("카메라 쪽 청록 원에서 출발", "가까운 안개는 여러 지점에서 읽기", "먼 곳은 간단히 계산하고 탑 앞에 도착"),
    "03-1": ("같은 얼굴에 색을 칠하기", "오른쪽에 법선 방향 더하기", "빛을 움직여 명암 비교"),
    "03-3": ("법선은 표면에 수직인 방향", "법선 맵이 빛을 계산할 방향을 바꿈", "윤곽은 같고 흉터의 명암만 달라짐"),
    "04-1": ("먼 성을 보고 출발", "길에서 중간 표식 발견", "가까운 입구를 보고 방향 선택"),
    "04-3": ("멀리 보이는 큰 목표", "가까운 입구가 새로 보임", "화면에 들어온 표식으로 갈림길 선택"),
    "05-1": ("작은 나무와 큰 나무를 섞어 배치", "앞의 큰 나무가 먼 구조물을 가림", "같은 위치에서 먼 윤곽 비교"),
    "05-3": ("앞의 큰 나무로 시야가 막힘", "낮은 나무 사이로 먼 윤곽이 드러남", "시선이 먼 목표까지 이어짐"),
    "06-1": ("기존 벽과 바위로 시험 필드 조립", "같은 길로 이동하며 규모 확인", "규모를 정한 뒤 표면 디테일 추가"),
    "06-3": ("기존 에셋으로 필요한 제작량부터 계산", "벽과 바위의 크기, 위치를 유지", "정해진 범위에만 새 디테일 제작"),
    "07-1": ("높이맵은 격자점의 높이를 저장", "같은 격자 안에서 지면이 오르내림", "폴리곤 메시는 단차 위치도 조정"),
    "07-3": ("같은 지형에서 두 방식 비교", "메시의 점을 직접 옮겨 단차 위치 변경", "원하는 곳에 발이 닿는 높이를 맞춤"),
    "08-1": ("텍스처 한 줄에 한 순간의 위치 기록", "시간에 맞는 줄을 골라 읽기", "점의 위치가 변하면서 형태 재생"),
    "08-3": ("점의 위치와 방향을 함께 확인", "저장된 순간으로 표면 형태 재생", "실제 라이커드 전투는 영상 끝에서 확인"),
    "09-1": ("낮고 좁은 돌 통로에서 출발", "발이 닿는 경사를 따라 위로 이동", "문을 지나 높은 뜰과 먼 풍경이 열림"),
    "09-3": ("캐릭터 뒤에서 이동 경로를 따라감", "경사와 문을 지나면서 시야 변화", "테라스에서 옆길로 방향 전환"),
    "10-1": ("발을 딛고 두 팔을 들어 시전 준비", "효과 지점이 빠르면 지팡이보다 먼저 발사", "팔을 내리며 자세 회복"),
    "10-3": ("같은 시전 자세로 준비", "지팡이가 올라온 순간에 효과 발사", "손과 몸이 원래 자세로 돌아옴"),
}
PHASES = (.31, .66)
PLAY_WINDOWS = {
    "05": (497, "낮은 풀밭 너머에 아치의 먼 윤곽이 보임. 열린 들판을 걷다가 말에 올라 이어서 이동."),
    "09": (6, "좁은 석조 통로에서 금빛 관문을 지나 밝은 성곽으로 나옴. 중간 소환 안내가 보임."),
}
EXPLANATIONS = {
    "02": "청록색 출발점에서 걷기 시작해 안개가 낀 길을 지나 노란색 탑 입구에 도착합니다.",
    "03": "같은 얼굴로 색과 법선을 비교합니다. 아래에 색·적용 범위·법선 방향을 따로 표시했습니다.",
    "05": "같은 시점에서 큰 나무와 작은 나무의 배치를 바꿨을 때 먼 구조물이 얼마나 가리는지 비교합니다.",
    "06": "이전 작품의 리소스로 시험용 필드를 조립해 넓이와 제작량을 먼저 가늠했습니다. 같은 입체 구조에서 표면 디테일을 추가하기 전후를 보여 줍니다.",
    "07": "초기엔 높이맵을 검토했습니다. 플레이에 필요한 단차의 높이와 위치를 맞추기 위해 폴리곤 메시의 점과 면을 직접 편집했습니다.",
    "08": "영상 마지막에 라이커드가 검을 들어 몸을 틀고 휘두르는 실제 전투 10초를 붙였습니다.",
    "09": "캐릭터가 돌 통로에서 경사를 밟아 올라가고 관문을 지나면 높은 뜰과 옆길이 열립니다.",
    "10": "발을 딛고, 관절을 움직여 지팡이를 들고, 효과를 발사한 뒤 자세를 회복합니다.",
}


def write_list(file, parts):
    file.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    return file


def labeled_plate(painter, label, phase, file):
    picture = painter.base(label)
    draw = ImageDraw.Draw(picture)
    draw.text((492, 1410), phase, font=painter.label, anchor="mm", fill="#f5f5f5")
    picture.save(file)


def render_cut(painter, timing, capture_record, target):
    key = timing["id"]
    work = target.parent
    first, last = timing["speechStartFrame"], timing["speechEndFrame"]
    starts = [round(first + (last - first) * s) for s in PHASES]
    if key[:2] in {"05", "06"}:
        starts[0] = round((first + last) / 2)
    files = [work / f"{key}-plate-{i}.png" for i in range(3)]
    for i, (label, phase) in enumerate(zip(GUIDES[key], ("처음 상태", "바뀌는 과정", "보이는 결과"))):
        labeled_plate(painter, label, phase, files[i])
    inputs = []
    for file in files:
        inputs.extend(("-loop", 1, "-framerate", 60, "-i", file))
    x, y, w, h = film.rectangles(capture.pipeline.WINDOW)
    video = Path(capture_record["path"])
    assert sha(video) == capture_record["sha256"]
    phase_a, phase_b = (f"{s / 60:.8f}" for s in starts)
    plate = (f"[0:v][1:v]overlay=enable='gte(t,{phase_a})'[a];"
             f"[a][2:v]overlay=enable='gte(t,{phase_b})'[plate];")
    if key[:2] == "03":
        # The swatches and headings sit over the native picture rather than behind it.
        labels = Image.new("RGBA", (1080, 1920))
        draw = ImageDraw.Draw(labels)
        font = painter.label.font_variant(size=30)
        for x0, y0, text in ((241, y + 31, "색만"), (743, y + 31, "색 + 법선"),
                             (216, y + h - 37, "색 텍스처"), (492, y + h - 37, "적용 범위"),
                             (768, y + h - 37, "법선 방향")):
            box = draw.textbbox((x0, y0), text, font=font, anchor="mm")
            draw.rounded_rectangle((box[0] - 12, box[1] - 5, box[2] + 12, box[3] + 5),
                                   radius=8, fill=(13, 25, 34, 233))
            draw.text((x0, y0), text, font=font, anchor="mm", fill="white")
        guide = work / f"{key}-face-labels.png"
        labels.save(guide)
    else:
        guide = None
    scene = (plate + f"[3:v]scale={w}:{h}:flags=lanczos,format=rgba,setsar=1[body];"
             f"[plate][body]overlay={x}:{y}:shortest=1[picture]")
    extra = []
    video_layer = "[picture]"
    if guide:
        extra = ["-loop", 1, "-framerate", 60, "-i", guide]
        scene += ";[picture][4:v]overlay=0:0:shortest=1[guided]"
        video_layer = "[guided]"
    cat = Image.new("RGBA", (1080, 1920))
    painter.reaction(cat, "realize")
    reaction = work / f"{key}-reaction.png"
    cat.save(reaction)
    reaction_input = 5 if guide else 4
    stop = min(timing["frames"] / 60, starts[1] / 60 + 2)
    scene += f";{video_layer}[{reaction_input}:v]overlay=enable='between(t,{phase_b},{stop:.8f})':shortest=1[out]"
    film.edit.ffmpeg(*inputs, "-i", video, *extra, "-filter_complex_threads", 2, "-filter_complex", scene,
                    "-loop", 1, "-framerate", 60, "-i", reaction,
                    "-map", "[out]", "-an", "-frames:v", timing["frames"], "-c:v", "libx264",
                    "-threads", 4, "-preset", "ultrafast", "-crf", 19, "-pix_fmt", "yuv420p", target)
    stream = film.edit.probe(target)["streams"][0]
    assert (stream["width"], stream["height"], int(stream["nb_frames"])) == (1080, 1920, timing["frames"])
    return {"labels": list(GUIDES[key]), "phaseFrames": [0, *starts], "bodyRect": [x, y, w, h]}


def audit_native(record, capture_map, number, assets):
    for index in (1, 3):
        entry = capture_map[f"{number}-{index}"]
        assert Path(entry["scenePath"]).is_file() and sha(Path(entry["scenePath"])) == entry["sceneSha256"]
        roles = entry["libraryRoles"]
        assert roles and set(roles) <= set(assets)
        record["cuts"][index].update(unity=entry | {"assetRecords": [assets[role] for role in roles]},
            demonstration=entry["path"], sha256=entry["sha256"], picture="walkthrough-v8")


def alternate_play(number, record, painter, contract, work):
    index = 2
    start, observed = PLAY_WINDOWS[number]
    cut = record["cuts"][index]
    original = record["formatSources"][index]
    source = Path(original["source"])
    assert cut["type"] == "gameplay" and sha(source) == cut["sha256"] == original["sourceSha256"]
    cut.update(start=start, end=start + cut["frames"] / 60, observed=observed,
               picture="observed-same-source-window-v8")
    record["formatSources"][index] = film.make_cut(
        {"id": number}, index, cut, source, cut["size"], painter, contract, work)
    return work / f"{index}-clean.mp4"


def check_playback(record, assembled, previous, parts, replacement):
    actual = film.native.packet_fingerprints(assembled)
    earlier = film.native.packet_fingerprints(previous)
    assert len(actual) == len(earlier) == sum(cut["frames"] for cut in record["cuts"])
    cursor = 0
    for i, cut in enumerate(record["cuts"]):
        stop = cursor + cut["frames"]
        expected = film.native.packet_fingerprints(parts[i]) if replacement and i == 2 else earlier[cursor:stop]
        if i in (0, 2) and actual[cursor:stop] != expected:
            source, first = (parts[i], 0) if replacement and i == 2 else (previous, cursor)
            assert film.native.decoded_range(assembled, cursor, cut["frames"]) == (
                film.native.decoded_range(source, first, cut["frames"]))
        cursor = stop


def render_episode(number, rows, captures, contract, paragraphs, scratch):
    source = V6 / number
    base = read(source / "verification.json")
    record = deepcopy(base)
    destination = OUT / number
    if number == "08":
        destination = scratch / "08-body"
    destination.mkdir(parents=True, exist_ok=True)
    receipt = destination / "verification.json"
    if receipt.is_file():
        saved = read(receipt)
        assert saved["unityFingerprint"] == captures[f"{number}-1"]["fingerprint"]
        assert all(sha(destination / saved[k]["path"]) == saved[k]["sha256"] for k in ("clean", "captioned"))
        return destination
    work = scratch / number
    work.mkdir(parents=True, exist_ok=True)
    painter = film.compositor(contract, number)
    prior = source / "clean.mp4"
    assert sha(prior) == base["clean"]["sha256"]
    parts = [source / f"{index}-clean.mp4" for index in range(4)]
    audit_native(record, captures, number, capture.library.selected_assets())
    for index in (1, 3):
        key = f"{number}-{index}"
        clip = work / f"{index}-clean.mp4"
        guide = render_cut(painter, rows[key], captures[key], clip)
        record["cuts"][index]["walkthroughGuide"] = guide
        scene = captures[key]
        record["formatSources"][index] = {
            "source": scene["path"], "sourceSha256": scene["sha256"], "sourceStart": 0,
            "sourceSpeed": 1, "originalAspectPreserved": True, "reaction": "realize",
            "phaseStarts": guide["phaseFrames"], "bodyRect": guide["bodyRect"],
            "originalTemplate": contract["sourceModules"]["bodyComposer"],
        }
        parts[index] = clip
    record["unityFingerprint"] = captures[f"{number}-1"]["fingerprint"]
    if number in PLAY_WINDOWS:
        parts[2] = alternate_play(number, record, painter, contract, work)
    audio = prior
    english = None
    if number == "07":
        from localized_terrain_v8 import localized_terrain_v8
        paragraphs, audio, english = localized_terrain_v8(record, paragraphs, work)
    frames = sum(cut["frames"] for cut in record["cuts"])
    clean = destination / "clean.mp4"
    film.edit.ffmpeg("-f", "concat", "-safe", 0, "-i", write_list(work / "clean.ffconcat", parts), "-i", audio,
                    "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart", clean)
    assert film.native.track_sha(clean, "a") == film.native.track_sha(audio, "a")
    record["clean"] = film.edit.validate(clean, frames)
    subtitle_input, cues = film.caption_track(number, painter, paragraphs, frames, work)
    captioned = destination / "captioned.mp4"
    film.edit.ffmpeg("-reinit_filter", 0, "-threads", 2, "-i", clean, "-f", "concat", "-safe", 0,
                    "-i", subtitle_input, "-filter_complex_threads", 2, "-filter_complex",
                    "[0:v][1:v]overlay=0:1470:eof_action=pass:shortest=1[out]",
                    "-map", "[out]", "-map", "0:a:0", "-c:v", "libx264", "-threads", 4, "-preset", "ultrafast",
                    "-crf", 19, "-c:a", "copy", "-frames:v", frames, "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", captioned)
    record["captioned"] = film.edit.validate(captioned, frames)
    assert film.native.track_sha(captioned, "a") == film.native.track_sha(clean, "a")
    record["captionPixelReview"] = film.caption_pixels(captioned, cues, work)
    check_playback(record, clean, prior, parts, number in PLAY_WINDOWS)
    shutil.copyfile(work / "ko.srt", destination / "ko.srt")
    if english is None:
        shutil.copyfile(source / "en.srt", destination / "en.srt")
        assert sha(destination / "ko.srt") == base["subtitles"]["ko"]
    else:
        (destination / "en.srt").write_text(english, encoding="utf-8")
    record["subtitles"] = {lang: sha(destination / f"{lang}.srt") for lang in ("ko", "en")}
    record.update(reviewStatus="pending", reviewVersion=VERSION, scope="native")
    save(receipt, record)
    print(f"{number}: {destination} ({frames / 60:.2f}s)", flush=True)
    return destination


def review_page():
    source = (V7 / "index.html").read_text(encoding="utf-8")
    header, start, articles = source.partition("<main>")
    assert start
    footer = articles.split("</main>", 1)[1]
    index = {}
    fragments = []
    for number in capture.IDS:
        match = re.search(rf'<article id="ep{number}">.*?</article>', articles, re.DOTALL)
        assert match
        card = match.group()
        folder = OUT / ("08-final" if number == "08" and (OUT / "08-final/verification.json").is_file() else number)
        result = None
        if (folder / "verification.json").is_file():
            result = read(folder / "verification.json")
        if result:
            for flavor in ("clean", "captioned"):
                assert sha(folder / f"{flavor}.mp4") == result[flavor]["sha256"]
            for lang in ("ko", "en"):
                assert sha(folder / f"{lang}.srt") == result["subtitles"][lang]
            clip_folder = folder.name
            card = re.sub(rf'(src|href)="(?:\.\./pc-review-v6/)?{number}/', rf'\1="{clip_folder}/', card)
            if number in PLAY_WINDOWS and result["cuts"][2]["picture"] == "observed-same-source-window-v8":
                before = read(V6 / number / "verification.json")["cuts"][2]["observed"]
                card = card.replace(escape(before), escape(result["cuts"][2]["observed"]), 1)
        elif number == "02":
            card = re.sub(r'(src|href)="02/', r'\1="../pc-review-v7/02/', card)
        native = result and result.get("scope") == "native"
        note = ("새 Unity 시연과 편집본 검수 대기" if native else
                "라이커드 실전 10초 반영" if result and number == "08" else "이전 영상 · 새 Unity 시연 촬영 대기")
        if native or (result and number == "08"):
            scene_details = []
            position = 0
            for i, piece in enumerate(result["cuts"]):
                if i in (1, 3) and piece.get("walkthroughGuide"):
                    guide = piece["walkthroughGuide"]
                    lines = "".join(f'<li><button data-position="{(position + f)/60:.6f}">재생</button> '
                                    f'{escape(label)}</li>' for f, label in zip(guide["phaseFrames"], guide["labels"]))
                    scene = Path(piece["unity"]["scenePath"]).as_uri()
                    scene_details.append(f'<ol>{lines}</ol><p><a href="{scene}">편집 가능한 Unity 씬</a></p>')
                position += piece["frames"]
            if number == "08":
                scene_details.append('<p><button data-position="44">라이커드 실전 10초 재생</button></p>')
            if scene_details:
                card = re.sub(r"<details><summary>시연 단계와 장면으로 이동</summary>.*?</details>",
                              "<details><summary>시연 장면으로 이동</summary>" + "".join(scene_details) + "</details>",
                              card, count=1, flags=re.DOTALL)
        explanation = EXPLANATIONS.get(number, "")
        card = card.replace("</h2>", f"</h2><p><strong>{note}</strong></p>" +
                            (f"<p>{escape(explanation)}</p>" if explanation else ""), 1)
        if number == "08" and result:
            card = re.sub(r"<p>22초 실제 플레이 \+ 22초 Unity 시연</p>",
                          "<p>본문 44초 · 실제 전투 부록 10초</p>", card)
        if number == "09" and (OUT / "09-walkthrough-sample.mp4").is_file():
            card = card.replace("</h2>", '</h2><p><a href="09-walkthrough-sample.mp4">Unity 이동 시연 샘플</a></p>', 1)
        index[number] = {"status": note, "localFolder": folder.name if result else None, "record": result}
        fragments.append(card)
    header = re.sub(r"<title>[^<]*</title>", "<title>엘든 링 01~10편 PC 검수</title>", header)
    header = re.sub(r"<h1>[^<]*</h1>", "<h1>엘든 링 01~10편 PC 검수</h1>", header)
    header = header.replace("실제 플레이 50% · 원리 설명 50%", "본문 실제 플레이 50% · Unity 설명 50% · 08 실제 전투 부록 10초")
    header = re.sub(r'<nav[^>]*>.*?</nav>', "", header, flags=re.DOTALL)
    nav = '<nav aria-label="편 번호">' + " ".join(f'<a href="#ep{n}">{n}</a>' for n in capture.IDS) + "</nav>"
    OUT.mkdir(parents=True, exist_ok=True)
    page = header + nav + "<main>" + "".join(fragments) + "</main>" + footer
    for link in re.findall(r'(?:href|src)="([^"]+\.(?:mp4|srt))"', page):
        assert (OUT / link).is_file(), link
    assert re.findall(r'<article id="ep(\d\d)">', page) == capture.IDS
    temporary = OUT / "index.html.tmp"
    temporary.write_text(page, encoding="utf-8")
    temporary.replace(OUT / "index.html")
    save(OUT / "manifest.json", {"reviewVersion": VERSION, "episodes": index,
         "gameplayObservationsSha256": sha(HERE / "gameplay-observations-v8.json"),
         "reviewPageSha256": sha(OUT / "index.html")})


def capture_records(number, rows, fingerprint, await_captures):
    selected = {key: cut for key, cut in rows.items() if key.startswith(number + "-")}
    guard = capture.gpu_guard()
    worker_path = capture.WORK / "software-capture-worker.json"
    while True:
        if all((capture.pipeline.CAPTURES / key / "capture.json").is_file() for key in selected):
            return {key: capture.pipeline.validate_capture(cut, fingerprint) for key, cut in selected.items()}
        if not await_captures or not worker_path.is_file() or not guard.alive(read(worker_path)):
            raise RuntimeError(f"Unity capture has not completed for episode {number}.")
        time.sleep(3)


def preserve_non_actor_episode(number):
    local = "08-final" if number == "08" else number
    source = PRIOR_BATCH / local
    record = read(source / "verification.json")
    assert record["scope"] == "native" and record["reviewVersion"] == "walkthrough-v8"
    destination = OUT / local
    destination.mkdir(parents=True, exist_ok=True)
    for name, expected in [(record[k]["path"], record[k]["sha256"]) for k in ("clean", "captioned")] + [
                           (f"{lang}.srt", record["subtitles"][lang]) for lang in ("ko", "en")]:
        assert sha(source / name) == expected
        if not (destination / name).is_file():
            shutil.copyfile(source / name, destination / name)
        assert sha(destination / name) == expected
    save(destination / "verification.json", record | {"reviewVersion": VERSION, "mediaReusedFrom": "walkthrough-v8"})


def main():
    global OUT, VERSION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--software", action="store_true")
    parser.add_argument("--page-only", action="store_true")
    parser.add_argument("--await-captures", action="store_true")
    parser.add_argument("--verified-rig", action="store_true")
    args = parser.parse_args()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    if args.verified_rig:
        OUT = PRIOR_BATCH.with_name("pc-review-v9")
        VERSION = "walkthrough-v9"
    if args.page_only:
        review_page()
        return
    _, _, rows = capture.selection()
    if args.verified_rig:
        rows = {key: cut for key, cut in rows.items() if key[:2] in capture.RIG_EPISODES}
    fingerprint = capture.source_id(rows, args.software)
    work = capture.configure(args.software, fingerprint, args.verified_rig)
    contract = read(film.FORMAT)
    paragraphs = read(film.CAPTIONS)["paragraphs"]
    scratch = work / "composition"
    if args.await_captures and not args.software:
        parser.error("--await-captures is available for the software capture worker")
    ordered = ("03", "07", "08", "09", "10", "01", "02", "04", "05", "06") if args.verified_rig else capture.IDS
    for number in ordered:
        if args.verified_rig and number not in capture.RIG_EPISODES:
            preserve_non_actor_episode(number)
            review_page()
            continue
        captures = capture_records(number, rows, fingerprint, args.await_captures)
        folder = render_episode(number, rows, captures, contract, paragraphs, scratch)
        if number == "08" and not (OUT / "08-final/verification.json").is_file():
            from rebase_rykard_tail_v8 import append_verified_tail
            append_verified_tail(folder, OUT / "08-final")
        if number == "09":
            sample = Path(captures["09-3"]["path"])
            shutil.copyfile(sample, OUT / "09-walkthrough-sample.mp4")
            assert sha(OUT / "09-walkthrough-sample.mp4") == captures["09-3"]["sha256"]
        review_page()


if __name__ == "__main__":
    main()
