import argparse
from dataclasses import dataclass
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / "projects/shorts-elden-ring-screen-space-decals/elden-ring-development-research.md"
MUSIC = ROOT / "shared/assets/music/incompetech/Wholesome.mp3"
PLAN = json.loads((HERE / "episodes-v1.json").read_text(encoding="utf-8"))
FPS = 60
WIDTH, HEIGHT = 1080, 1920
BG, CARD, TEXT = "#10171b", "#19262b", "#fff8ea"
SOFT, GOLD, TEAL, LINE = "#bbced0", "#ffd68a", "#81e2d5", "#385355"
FONT = Path("C:/Windows/Fonts/malgun.ttf")
BOLD = FONT.with_name("malgunbd.ttf")
ATTRIBUTION = "Wholesome · Kevin MacLeod · incompetech.com · CC BY 4.0 · 길이·페이드·음량 조정"
PAIR_REVIEW = Path("C:/Users/1/Videos/YamyamProduction/elden-ring-shorts-pair/review-v2")
SOURCE_ARCHIVE = Path("D:/YamyamProduction/elden-ring-development-36/source-holding")
MATCHED_DEMOS = {
    "07": ("terrain-visual-01.mp4", "terrain-visual-07.mp4"),
    "29": ("decals-visual-03.mp4", "decals-visual-07.mp4"),
}
SOURCE_ROWS = {
    int(num): (name, url)
    for num, name, url in re.findall(r"^\| (\d+) \| .*? \| .*? \| \[(.*?)\]\((https?://[^)]+)\) \|$",
                                    RESEARCH.read_text(encoding="utf-8"), re.M)
}


@dataclass(frozen=True)
class Clip:
    source: str
    start: float
    observed: str
    role: str


def run(*command):
    result = subprocess.run(list(map(str, command)), capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def ffmpeg(*args):
    return run("ffmpeg", "-y", "-hide_banner", "-nostdin", "-v", "error", *args)


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path))


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def exact_write(path, body):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(path)


def font(size, bold=True):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def wrap(draw, text, face, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        proposal = f"{current} {word}".strip()
        if current and draw.textlength(proposal, font=face) > width:
            lines.append(current)
            current = word
        else:
            current = proposal
    return [*lines, current]


def medallion(draw, position, label, accent):
    x, y = position
    draw.ellipse((x - 27, y - 27, x + 27, y + 27), fill=CARD, outline=accent, width=3)
    draw.text((x, y - 1), label, font=font(24), fill=accent, anchor="mm")


def card(episode, cut, clip, demonstration, has_captions, destination):
    is_game = cut % 2 == 0
    art = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(art)
    d.line((65, 119, 1015, 119), fill=LINE, width=3)
    d.text((66, 66), "엘든 링 개발 이야기", font=font(31), fill=TEAL)
    d.text((1013, 67), episode["topic"], font=font(28), fill=SOFT, anchor="ra")
    heading = font(66)
    headline = wrap(d, episode["title"], heading, 945)
    if len(headline) > 2:
        heading = font(53)
        headline = wrap(d, episode["title"], heading, 945)
    for n, label in enumerate(headline):
        d.text((65, 176 + 82 * n), label, font=heading, fill=GOLD)
    d.rounded_rectangle((62, 465, 1018, 1120), radius=17, fill=CARD, outline=LINE, width=3)
    if is_game:
        label = "엘든 링 실제 플레이" if clip else "실제 플레이 삽입 대기"
        if clip and clip.role == "in-game":
            label = "엘든 링 게임 내 연출"
        d.text((65, 410), label, font=font(32), fill=GOLD)
        content = clip.observed if clip else episode["requiredGameplay"][cut // 2]
        if not clip:
            d.text((105, 641), "이 장면의 원본이 필요합니다", font=font(49), fill=GOLD)
            for n, item in enumerate(wrap(d, content, font(42), 865)):
                d.text((105, 754 + 60 * n), item, font=font(42), fill=TEXT)
        else:
            role = "관찰한 장면" if clip.role == "direct" else "개념을 설명하는 플레이 예시"
            d.text((65, 1160), role, font=font(25), fill=GOLD)
            for n, item in enumerate(wrap(d, content, font(30), 940)):
                d.text((65, 1203 + 43 * n), item, font=font(30), fill=TEXT)
    elif demonstration:
        d.text((65, 410), "자체 원리 시연", font=font(32), fill=TEAL)
    else:
        d.text((65, 410), "개발 원리 도식", font=font(32), fill=TEAL)
        for n, label in enumerate(episode["diagram"]):
            y = 559 + 190 * n
            if n:
                d.line((153, y - 127, 153, y - 41), fill=LINE, width=4)
                d.polygon(((153, y - 30), (144, y - 48), (162, y - 48)), fill=LINE)
            accent = TEAL if n <= cut // 2 else GOLD
            medallion(d, (153, y), str(n + 1), accent)
            for row, item in enumerate(wrap(d, label, font(47), 745)):
                d.text((221, y - 35 + 61 * row), item, font=font(47), fill=accent)
    if has_captions:
        d.rounded_rectangle((62, 1410, 1018, 1717), radius=18, fill=CARD)
        caption = episode["narrationKo"][cut]
        face = font(43)
        lines = wrap(d, caption, face, 869)
        if len(lines) > 4:
            face = font(39)
            lines = wrap(d, caption, face, 869)
        assert len(lines) <= 4
        for n, line in enumerate(lines):
            d.text((WIDTH // 2, 1450 + 55 * n), line, font=face, fill=TEXT, anchor="ma")
    art.save(destination)


def wav_duration(path):
    with wave.open(str(path)) as audio:
        return audio.getnframes() / audio.getframerate()


def rms_measure(path):
    output = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path),
                             "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                             "-f", "null", "-"], check=True, capture_output=True).stderr.decode(errors="replace")
    measurement = json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}', output)[-1])
    return {"integratedLUFS": float(measurement["input_i"]), "truePeakDbTP": float(measurement["input_tp"])}


def concat_list(paths, target):
    target.write_text("".join(f"file '{source.name}'\n" for source in paths), encoding="ascii")
    return target


def overlay_clip(plate, path, clip, demonstration, frames, target):
    inputs = ["-framerate", FPS, "-i", plate]
    if clip:
        inputs.extend(["-ss", clip.start, "-i", path])
    elif demonstration:
        inputs.extend(["-i", demonstration])
    base = f"[0:v]format=yuv420p,tpad=stop_mode=clone:stop_duration={frames / FPS:.4f}[plate]"
    if clip:
        filters = (base + ";[1:v]fps=60,scale=950:534:flags=fast_bilinear,setsar=1[game];"
                   "[plate][game]overlay=x=65:y=525:shortest=1[out]")
    elif demonstration:
        filters = (base + ";[1:v]crop=980:690:50:532,fps=60,scale=924:650,"
                   "setsar=1,tpad=stop_mode=clone:stop_duration=15[sim];"
                   "[plate][sim]overlay=x=78:y=468:shortest=1[out]")
    else:
        filters = base + ";[plate]null[out]"
    ffmpeg(*inputs, "-filter_complex_threads", 2, "-filter_complex", filters,
           "-map", "[out]", "-an", "-frames:v", frames, "-c:v", "libx264", "-threads", 4,
           "-preset", "ultrafast", "-crf", 19, "-pix_fmt", "yuv420p", target)


def code_time(frames):
    ms = round(frames * 1000 / FPS)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def open_inputs(output):
    routing = json.loads((HERE / "footage-map-v1.json").read_text(encoding="utf-8"))
    sources = {}
    roots = {"repo": ROOT, "output": output, "archive": SOURCE_ARCHIVE}
    for name, record in routing["sources"].items():
        base = roots[record["base"]]
        path = base / record["path"]
        if not path.is_file():
            continue
        info = probe(path)
        video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
        assert video["height"] >= 1080, f"Sub-FHD source: {path}"
        sources[name] = {**record, "path": path, "size": [video["width"], video["height"]],
                         "sha256": sha(path), "seconds": float(info["format"]["duration"])}
    return sources, routing["episodes"]


def validate(path, frames):
    ffmpeg("-xerror", "-threads", 3, "-i", path, "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-")
    info = probe(path)
    video, audio = (next(s for s in info["streams"] if s["codec_type"] == kind) for kind in ("video", "audio"))
    assert (video["width"], video["height"], video["avg_frame_rate"], int(video["nb_frames"])) == (WIDTH, HEIGHT, "60/1", frames)
    assert abs(float(audio["duration"]) - frames / FPS) < .03
    timestamps = json.loads(run("ffprobe", "-v", "error", "-select_streams", "v:0",
                                "-show_frames", "-show_entries", "frame=best_effort_timestamp",
                                "-of", "json", path))["frames"]
    numerator, denominator = map(int, video["time_base"].split("/"))
    assert len(timestamps) == frames
    assert all(t["best_effort_timestamp"] * numerator * FPS == denominator * i for i, t in enumerate(timestamps))
    return {"path": path.name, "sha256": sha(path), "frames": frames}


def render(episode, output, sources, route, include_drafts):
    cue_wavs = [output / "review-voice" / f"{episode['id']}-{index}.wav" for index in range(4)]
    pair_lengths = [max(7, int(max(wav_duration(a), wav_duration(b)) + 1.15))
                    for a, b in zip(cue_wavs[::2], cue_wavs[1::2])]
    lengths = [seconds * FPS for seconds in pair_lengths for _ in range(2)]
    clips = []
    for index, cut in enumerate(route):
        clip = Clip(*cut) if cut else None
        if clip is not None and (clip.source not in sources or
                                 clip.start + pair_lengths[index] > sources[clip.source]["seconds"]):
            clip = None
        clips.append(clip)
    if not all(clips) and not include_drafts:
        return
    dest = output / episode["id"]
    dest.mkdir(exist_ok=True)
    records, stems = [], []
    lists = {"captioned": [], "clean": []}
    for index, frames in enumerate(lengths):
        clip = clips[index // 2] if index % 2 == 0 else None
        demonstration = None
        if index % 2 and episode["id"] in MATCHED_DEMOS:
            candidate = PAIR_REVIEW / MATCHED_DEMOS[episode["id"]][index // 2]
            if candidate.is_file():
                demonstration = candidate
        source = sources[clip.source] if clip else None
        for label in lists:
            plate = dest / f"{index}-{label}.png"
            card(episode, index, clip, demonstration, label == "captioned", plate)
            path = dest / f"{index}-{label}.mp4"
            overlay_clip(plate, source["path"] if source else None, clip, demonstration, frames, path)
            lists[label].append(path)
        audio = dest / f"voice-{index}.wav"
        ffmpeg("-i", cue_wavs[index], "-af", "adelay=130:all=1,apad", "-t", frames / FPS,
               "-ar", 48000, "-ac", 1, audio)
        stems.append(audio)
        record = {"frames": frames, "type": "gameplay" if clip else ("waiting-footage" if index % 2 == 0 else "explanation")}
        if clip:
            record.update({k: source[k] for k in ("recorder", "url", "rights", "sha256", "size")})
            record.update(start=clip.start, end=clip.start + frames / FPS, observed=clip.observed, role=clip.role)
        if demonstration:
            record.update(demonstration=str(demonstration), sha256=sha(demonstration))
        records.append(record)
    for suffix, text in (("ko", episode["narrationKo"]), ("en", episode["captionsEn"])):
        start, cues = 0, []
        for index, (frames, caption) in enumerate(zip(lengths, text)):
            end = start + frames
            cues.append(f"{index + 1}\n{code_time(start)} --> {code_time(end)}\n{caption}\n")
            start = end
        exact_write(dest / f"{suffix}.srt", "\n".join(cues))
    frames = sum(lengths)
    duration = frames / FPS
    narration = dest / "voice.wav"
    ffmpeg("-f", "concat", "-safe", 0, "-i", concat_list(stems, dest / "voice.txt"), "-c:a", "pcm_s16le", narration)
    gain = -16.8 - rms_measure(narration)["integratedLUFS"]
    soundtrack = dest / "mix.m4a"
    fade = duration - 1
    filt = (f"[0:a]volume={gain:.3f}dB,aformat=sample_rates=48000:channel_layouts=stereo[v];"
            f"[1:a]volume=-13dB,afade=d=0.4,afade=t=out:st={fade}:d=1[b];"
            "[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.83:level=false:latency=true[a]")
    ffmpeg("-i", narration, "-ss", 14 + int(episode["id"]) % 12 * 7, "-i", MUSIC,
           "-filter_complex", filt, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", soundtrack)
    result = {}
    for label, shots in lists.items():
        target = dest / f"{label}.mp4"
        ffmpeg("-f", "concat", "-safe", 0, "-i", concat_list(shots, dest / f"{label}.txt"),
               "-i", soundtrack, "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", target)
        result[label] = validate(target, frames)
    audio_level = rms_measure(dest / result["captioned"]["path"])
    gameplay = sum(cut["frames"] for cut in records if cut["type"] == "gameplay")
    expected = sum(lengths[1::2])
    if all(clips):
        assert gameplay == expected and expected * 2 == frames
    result.update(seconds=duration, gameplaySeconds=gameplay / FPS, explanationSeconds=expected / FPS,
                  missing=[episode["requiredGameplay"][i] for i, clip in enumerate(clips) if not clip],
                  cuts=records, audio=audio_level,
                  narration="Microsoft Heami Desktop, 임시 검수 음성", music=ATTRIBUTION,
                  subtitles={language: sha(dest / f"{language}.srt") for language in ("ko", "en")},
                  humanReview="pending")
    exact_write(dest / "verification.json", json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{episode['id']} {duration:.1f}s, {gameplay / FPS:.1f}s game, {len(result['missing'])} missing clips", flush=True)


def reviews(output):
    rows = []
    for episode in PLAN:
        path = output / episode["id"] / "verification.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if data:
            for label in ("captioned", "clean"):
                artifact = path.parent / data[label]["path"]
                assert artifact.is_file() and sha(artifact) == data[label]["sha256"]
            data["subtitles"] = {language: sha(path.parent / f"{language}.srt") for language in ("ko", "en")}
            assert len(data["cuts"]) == 4 and data["audio"]["truePeakDbTP"] < -1
            if not data["missing"]:
                assert data["gameplaySeconds"] == data["explanationSeconds"] == data["seconds"] / 2
        source, url = SOURCE_ROWS[int(episode["id"])]
        rows.append({**episode, "review": data, "source": {"title": source, "url": url}})
    return rows


def review_page(output, approved_voice=False, native_unity=False, asset_library=False):
    rows = reviews(output)
    complete = sum(bool(r["review"]) and not r["review"]["missing"] for r in rows)
    drafts = sum(bool(r["review"]) for r in rows) - complete
    cards = []
    for row in rows:
        number = row["id"]
        report = row["review"]
        source = row["source"]
        status = "PC 검수본" if report and not report["missing"] else ("미삽입 구간 표시본" if report else "대본 · 영상 확보 중")
        details = row["requiredGameplay"] if report is None else report["missing"]
        status_content = "".join(f"<li>{escape(detail)}</li>" for detail in details)
        match = f"<ul>{status_content}</ul>" if details else ""
        video_links = ""
        if report:
            video_links = (f'<video controls preload="none" playsinline src="{number}/captioned.mp4"></video>'
                           f'<p><a href="{number}/captioned.mp4">자막 영상</a> · <a href="{number}/clean.mp4">클린 영상</a>'
                           f' · <a href="{number}/ko.srt">한국어 SRT</a> · <a href="{number}/en.srt">영어 SRT</a></p>'
                           f'<p>{report["seconds"]:g}초 · 실제 플레이 {report["gameplaySeconds"]:g}초 · '
                           f'설명 {report["explanationSeconds"]:g}초 · 최종 {report["audio"]["integratedLUFS"]:.2f} LUFS</p>')
            footage = [
                f'<li>{escape(cut["observed"])} '
                f'<a href="{escape(cut["url"], quote=True)}">{escape(cut["recorder"])}</a></li>'
                for cut in report["cuts"] if cut["type"] == "gameplay"
            ]
            if footage:
                video_links += f'<details><summary>플레이 원본 및 장면 확인</summary><ul>{"".join(footage)}</ul></details>'
        script = "".join(f"<li>{escape(line)}</li>" for line in row["narrationKo"])
        cards.append(f'<article id="ep{number}"><span class="flag">{status}</span><h2>{number}. {escape(row["title"])}</h2>'
                     f'{video_links}{match}<details><summary>대본</summary><ol>{script}</ol></details>'
                     f'<p><a href="{escape(source["url"], quote=True)}">{escape(source["title"])}</a></p></article>')
    navigation = " ".join(f'<a href="#ep{row["id"]}">{row["id"]}</a>' for row in rows)
    if asset_library:
        status_note = f"PC 검수본 {complete}편 · 실제 플레이 50% · Unity 원리 시연 50%"
        review_note = ("비디오에디팅 프로젝트의 공용 캐릭터·환경·소품을 연결해 Unity 시연 72개를 새로 촬영했습니다. "
                       "기존 쇼츠 목소리를 사용했습니다. 번호를 누르면 해당 편으로 이동합니다.")
    elif native_unity:
        status_note = f"PC 검수본 {complete}편 · 실제 플레이 50% · Unity 원리 시연 50%"
        review_note = "기존 쇼츠 목소리를 사용했습니다. 36편에 Unity 시연 72개를 넣었습니다. 번호를 누르면 해당 편으로 이동합니다."
    elif approved_voice:
        status_note = f"PC 검수본 {complete}편 · 실제 플레이 50% · 설명 50%"
        review_note = "기존 쇼츠 승인 목소리로 다시 렌더했습니다. 번호를 누르면 해당 편으로 이동합니다."
    else:
        status_note = f"실제 플레이를 맞춘 검수본 {complete}편 · 영상 초안 {drafts}편 · 대본만 {36-complete-drafts}편"
        review_note = ("실제 플레이가 확보된 구간에서는 설명과 길이를 맞춥니다. 원본이 필요한 구간은 편별로 표시했습니다. "
                       "사용 음성은 임시 검수 음성입니다.")
    index = f'''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>엘든 링 개발 쇼츠 36편 PC 검수</title>
<style>body{{background:#10171b;color:#fff8ea;font:16px/1.7 "Malgun Gothic",sans-serif;margin:auto;max-width:1240px;padding:24px}}
article{{padding:18px;background:#1a292e;border:1px solid #3b5357;border-radius:12px;scroll-margin:18px}}
h1,h2{{line-height:1.3;color:#ffd68a}}h2{{font-size:22px}}a{{color:#81e2d5}}nav a{{display:inline-block;margin:4px}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:16px}}
.flag{{font-weight:bold;color:#81e2d5}}video{{display:block;width:min(100%,280px);margin:auto;aspect-ratio:9/16;background:black}}
summary{{cursor:pointer}}footer{{margin-block:25px}}</style>
<h1>엘든 링 개발 쇼츠 36편 PC 검수</h1><p>{status_note}</p>
<p>{review_note} 클립의 PC 검수 범위와 출처는 <a href="manifest.json">검수 기록</a>에 있습니다.</p>
<nav>{navigation}</nav><main>{''.join(cards)}</main>
<footer>{ATTRIBUTION} · <a href="https://creativecommons.org/licenses/by/4.0/">음악 이용 조건</a></footer></html>'''
    if asset_library:
        version = "unity-shared-assets-v4"
    else:
        version = "unity-principles-v3" if native_unity else "approved-voice-v2" if approved_voice else "temporary-voice-v1"
    exact_write(output / "manifest.json", json.dumps({"count": len(rows), "videoReviews": complete,
                                                     "reviewVersion": version,
                                                     "roughCuts": drafts, "episodes": rows}, ensure_ascii=False, indent=2))
    exact_write(output / "index.html", index)
    print(f"PC index: {complete} matched footage, {drafts} rough cuts, {36-complete-drafts} scripts", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--only", nargs="+")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--drafts", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    assert list(SOURCE_ROWS) == list(range(1, 37))
    assert [int(ep["id"]) for ep in PLAN] == list(SOURCE_ROWS)
    if not args.index:
        sources, routes = open_inputs(output)
        for episode in PLAN:
            number = episode["id"]
            if args.only and number not in args.only:
                continue
            try:
                render(episode, output, sources, routes.get(number, [None, None]), args.drafts)
            except (RuntimeError, AssertionError) as problem:
                print(f"{number} render or validation failed: {problem}", flush=True)
    review_page(output)


if __name__ == "__main__":
    main()
