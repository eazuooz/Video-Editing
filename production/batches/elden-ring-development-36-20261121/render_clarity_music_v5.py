"""Re-edit all 72 verified Unity captures with frame-aligned instruction and licensed music."""

from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
import re
import shutil
import wave

import psutil

from PIL import Image, ImageColor, ImageDraw, ImageOps

import build_pc_review as edit
import make_unity_revision_v3 as native
from make_unity_revision_v3 import track_sha
from make_approved_voice_v2 import DEFAULT_OUTPUT, HERE, read, save, sha

WORK = Path("D:/YamyamProduction/elden-ring-development-36-clarity-v5")
V4 = DEFAULT_OUTPUT.with_name("pc-review-v4")
OUTPUT = DEFAULT_OUTPUT.with_name("pc-review-v5")
PLAN_FILE = HERE / "clarity-plan-v5.json"
VERSION = "unity-clarity-and-music-v5"
PHASES = ("처음 상태", "바꾼 것", "보이는 결과")
ACCENTS = ("#f8c86e", "#6ee2d1", "#abe284")
BG = "#10191e"
CARD = "#1c2b32"
TEXT = "#f6f6e9"
MUTED = "#b7c9ca"

LEGENDS = {
    "01": (("금색  현재 칸", 0), ("청록  읽은 주변 칸", 1)),
    "02": (("청록 점  밀도를 읽은 곳", 1), ("노란 선  시선", 0)),
    "03": (("왼쪽  표면 비교 기준", 0), ("오른쪽  바뀐 빛 반응", 1)),
    "07": (("왼쪽  격자 높이", 0), ("오른쪽  메시 편집", 1)),
    "08": (("왼쪽  움직이는 점", 1), ("오른쪽  위치를 저장한 행", 0)),
    "10": (("노란 점  현재 재생 위치", 0), ("청록 키  효과 발생 위치", 1)),
    "11": (("초록 면  걸을 수 있는 곳", 1), ("노란 길  선택한 연결", 0)),
    "12": (("초록 선  기록된 경로", 1), ("붉은 원  기록한 좌표", 0)),
    "14": (("노란 원  예고", 0), ("빨간 원  타격 범위", 1)),
    "15": (("앞쪽  개별 배치", 0), ("뒤쪽  넓은 꽃밭", 1)),
    "19": (("왼쪽  들판", 1), ("오른쪽  성문", 0)),
    "20": (("위  걷는 경로", 0), ("아래  이동 비교", 1)),
    "22": (("노란 표식  첫 번째 탐험가", 0), ("파란 표식  두 번째 탐험가", 1)),
    "26": (("왼쪽  가벼운 무기", 1), ("오른쪽  무거운 무기", 0)),
    "27": (("노란 원  직접음", 0), ("청록 원  반사음", 1)),
    "29": (("청록  데칼이 붙는 바닥", 1), ("푸른 벽  방향 검사 대상", 0)),
    "30": (("위  고른 갱신", 1), ("아래  불규칙한 갱신", 0)),
    "32": (("흰 막대  비플레이어", 0), ("청록 막대  플레이어", 1)),
    "33": (("노란 선  들어오는 광선", 0), ("청록 선  반사 경로", 1)),
    "34": (("회색  원래 증가", 0), ("색 막대  조정 후", 1)),
    "35": (("빨간 원  위험 범위", 0), ("초록 선  재시도 경로", 1)),
    "36": (("노란 인물  요청한 쪽", 0), ("초록 인물  합류한 쪽", 1)),
}
VISUAL_SAMPLES = {"10-1": .62, "10-3": .67, "14-1": .75, "14-3": .75, "27-1": .83, "27-3": .70}
ACTION = {"06","11","14","17","19","20","24","26","30","32","35","36"}
DARK_ENVIRONMENT = {"02","03","08","10","12","13","27","29","33"}


def sample(movie, frame):
    data = edit.run("ffmpeg", "-v", "error", "-threads", 1, "-ss", f"{frame/60:.6f}", "-i", movie,
                    "-frames:v", 1, "-threads", 1, "-c:v", "png", "-f", "image2pipe", "-")
    with Image.open(io.BytesIO(data)) as picture:
        return picture.convert("RGB")


def fit_text(canvas, body, xy, width, start, fill=TEXT, anchor=None, floor=32):
    for size in range(start, floor - 1, -1):
        face = edit.font(size)
        if canvas.textlength(body, font=face) <= width:
            canvas.text(xy, body, font=face, fill=fill, anchor=anchor)
            return
    raise ValueError(f"Text does not fit safely: {body!r}")


def phase_frame(cut, value):
    first = cut["speechStartFrame"]
    return round(first + value * (cut["speechEndFrame"] - first))


def layout(episode, cut, lesson, phase, stills, captions, destination):
    art = Image.new("RGB", (edit.WIDTH, edit.HEIGHT), BG)
    draw = ImageDraw.Draw(art)
    draw.text((65, 61), "엘든 링 개발 이야기 · Unity 원리 시연", font=edit.font(32), fill=ACCENTS[1])
    draw.line((65, 114, 1015, 114), width=3, fill="#3c5358")
    title_face = edit.font(59)
    title_lines = edit.wrap(draw, episode["title"], title_face, 950)
    if len(title_lines) > 2:
        title_face = edit.font(47)
        title_lines = edit.wrap(draw, episode["title"], title_face, 950)
    assert 1 <= len(title_lines) <= 3
    title_step = 55 if len(title_lines) == 3 else 67
    for row, line in enumerate(title_lines):
        draw.text((65, 138 + row * title_step), line, font=title_face, fill="#ffd88f")
    for i, label in enumerate(PHASES):
        x = 65 + i * 322
        color = ACCENTS[i] if i == phase else "#334950"
        draw.rounded_rectangle((x, 312, x + 305, 370), radius=12, fill=color if i == phase else CARD,
                               outline=color, width=3)
        draw.text((x + 152, 342), label, font=edit.font(32), fill=BG if i == phase else MUTED, anchor="mm")
    fit_text(draw, lesson["lines"][phase], (65, 394), 950, 45)
    draw.rounded_rectangle((62, 451, 1018, 1107), radius=12, outline="#486269", width=3)
    for side, picture in enumerate(stills):
        x = 65 + 485 * side
        color = ACCENTS[0 if side == 0 else 2]
        is_active = side == 0 and phase == 0 or side == 1 and phase == 2
        draw.rounded_rectangle((x, 1124, x + 465, 1389), radius=14, fill=CARD,
                               outline=color if is_active else "#3d5057", width=4)
        draw.text((x + 22, 1139), "처음 화면" if side == 0 else "변화 뒤 화면",
                  font=edit.font(30), fill=color)
        preview = ImageOps.contain(picture, (430, 187), Image.Resampling.LANCZOS)
        art.paste(preview, (x + (465-preview.width)//2, 1187))
    if captions:
        draw.rounded_rectangle((62, 1441, 1018, 1710), radius=18, fill=CARD)
        face = edit.font(43)
        lines = edit.wrap(draw, episode["narrationKo"][cut["shot"]], face, 878)
        if len(lines) > 4:
            face = edit.font(38)
            lines = edit.wrap(draw, episode["narrationKo"][cut["shot"]], face, 878)
        assert len(lines) <= 4
        for row, line in enumerate(lines):
            draw.text((540, 1472 + 51 * row), line, font=face, anchor="ma", fill=TEXT)
    art.save(destination)


def legend(episode, cut, output):
    art = Image.new("RGBA", (950, 650))
    draw = ImageDraw.Draw(art)
    labels = LEGENDS.get(episode["id"], ())
    if cut["id"] == "35-1":
        labels = labels[:1]
    if cut["id"] == "29-1":
        labels = (("흰 선  카메라 시선", 0), labels[0])
    for i, (label, color) in enumerate(labels):
        x = 16 + i * 460
        font = edit.font(31)
        width = min(437, round(draw.textlength(label, font=font)) + 34)
        draw.rounded_rectangle((x, 14, x + width, 67), radius=11, fill=(13, 25, 34, 237))
        fit_text(draw, label, (x + 16, 21), width - 20, 31, ACCENTS[color], floor=25)
    art.save(output)


def verify_phases(movie, starts, frames):
    selected = [starts[0]//2, (starts[0]+starts[1])//2, (starts[1]+frames-1)//2]
    filter_chain = "+".join(f"eq(n\\,{frame})" for frame in selected)
    raw = edit.run("ffmpeg", "-v", "error", "-threads", 1, "-i", movie,
                   "-vf", f"select={filter_chain},crop=650:2:82:334",
                   "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-")
    stride = 650*2*3
    assert len(raw) == stride*3
    for phase, hex_color in enumerate(ACCENTS):
        start = phase*stride+phase*322*3
        expected = ImageColor.getrgb(hex_color)
        assert all(abs(a-b) <= 23 for a, b in zip(raw[start:start+3], expected)), (movie, phase)


def explanation(episode, cut, native_record, lesson, destination):
    key = cut["id"]
    original = Path(native_record["path"])
    assert sha(original) == native_record["sha256"]
    assert sha(Path(native_record["scenePath"])) == native_record["sceneSha256"]
    starts = [phase_frame(cut, a) for a in lesson["phaseStarts"]]
    assert 0 < starts[0] < starts[1] < cut["frames"]
    selected = [phase_frame(cut, .05), phase_frame(cut, VISUAL_SAMPLES.get(key, .91))]
    stills = [sample(original, frame) for frame in selected]
    assert all(picture.size == native.WINDOW for picture in stills)
    guide = destination / f"{key}-guide.png"
    legend(episode, cut, guide)
    for flavor in ("captioned", "clean"):
        plates = []
        for phase in range(3):
            plate = destination / f"{key}-{flavor}-{phase}.png"
            layout(episode, cut, lesson, phase, stills, flavor == "captioned", plate)
            plates.append(plate)
        first, second = (frame / 60 for frame in starts)
        filters = (
            f"[0:v][1:v]overlay=enable='gte(t,{first:.8f})'[first];"
            f"[first][2:v]overlay=enable='gte(t,{second:.8f})'[plate];"
            "[3:v]setsar=1[scene];[scene][4:v]overlay[sceneGuided];"
            "[plate][sceneGuided]overlay=65:454:shortest=1[out]"
        )
        edit.ffmpeg("-loop", 1, "-framerate", 60, "-i", plates[0],
                    "-framerate", 60, "-i", plates[1], "-framerate", 60, "-i", plates[2],
                    "-threads", 2, "-i", original, "-framerate", 60, "-i", guide,
                    "-filter_complex_threads", 2, "-filter_complex", filters, "-map", "[out]", "-an",
                    "-frames:v", cut["frames"], "-c:v", "libx264", "-threads", 4, "-preset", "ultrafast",
                    "-crf", 19, "-pix_fmt", "yuv420p", destination / f"{cut['shot']}-{flavor}.mp4")
    verify_phases(destination / f"{cut['shot']}-captioned.mp4", starts, cut["frames"])
    return native_record | {"phaseLabels": list(PHASES), "phaseStartsAtFrames": [0,*starts],
                            "phaseText": lesson["lines"], "comparedNativeFrames": selected,
                            "legend": [text for text, color in LEGENDS.get(episode["id"], ())]}


def exact_voice(number, frames):
    origin = native.PRIOR / number
    wav = origin / "narration-timed.wav"
    with wave.open(str(wav)) as all_voice:
        assert (all_voice.getframerate(), all_voice.getnchannels(), all_voice.getsampwidth()) == (48000, 1, 2)
        assert all_voice.getnframes() == sum(frames)*800
        for index, length in enumerate(frames):
            with wave.open(str(origin / f"scene-{index}-mix.wav")) as part:
                assert part.getnframes() == length*800
                assert all_voice.readframes(length*800) == part.readframes(length*800)
    return wav


def mixed_sound(number, track, frames, dest, *, voice=None):
    if voice is None:
        voice = exact_voice(number, frames)
    seconds = sum(frames)/60
    offset = 13 + int(number) % 14 * 6
    source = WORK / track["file"]
    assert sha(source) == track["sha256"]
    excerpt, bed = (dest / name for name in ("music-excerpt.wav", "music-bed.wav"))
    raw, sound = (dest / name for name in ("mix-unmastered.wav", "mix.m4a"))
    edit.ffmpeg("-ss", offset, "-i", source, "-t", seconds, "-ac", 2, "-ar", 48000, excerpt)
    original_level = edit.rms_measure(excerpt)["integratedLUFS"]
    voice_level = edit.rms_measure(voice)["integratedLUFS"]
    edit.ffmpeg("-i", excerpt, "-af",
                f"volume={min(-31, voice_level - 13)-original_level:.2f}dB,"
                f"afade=d=0.35,afade=t=out:st={seconds-0.75}:d=0.75",
                "-c:a", "pcm_f32le", bed)
    bed_level = edit.rms_measure(bed)["integratedLUFS"]
    assert voice_level - bed_level >= 11.5
    filters = ("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit[voice][key];"
               "[1:a][key]sidechaincompress=threshold=0.035:ratio=2.5:attack=32:release=230[music];"
               "[voice][music]amix=inputs=2:duration=first:normalize=0")
    edit.ffmpeg("-i", voice, "-i", bed, "-filter_complex", filters, "-t", seconds, "-c:a", "pcm_f32le", raw)
    gain = -16.6-edit.rms_measure(raw)["integratedLUFS"]
    ceiling = -2.7
    for _ in range(3):
        edit.ffmpeg("-i", raw, "-af", f"volume={gain:.3f}dB,aresample=192000,"
                    f"alimiter=limit={10**(ceiling/20):.6f}:level=false:latency=true,aresample=48000",
                    "-c:a", "aac", "-b:a", "192k", sound)
        levels = edit.rms_measure(sound)
        if -18 <= levels["integratedLUFS"] <= -15 and levels["truePeakDbTP"] < -1:
            return sound, dict(levels, speechLufs=voice_level, unduckedMusicLufs=bed_level,
                               startSeconds=offset, dryNarrationSha256=sha(voice), fileSha256=sha(sound))
        gain += -16.6-levels["integratedLUFS"]
        ceiling -= max(0, levels["truePeakDbTP"]+1.6)
    raise ValueError(f"Final audio outside review range for {number}: {levels}")


def verify_gameplay(new, old, edits):
    old_packets, new_packets = (native.packet_fingerprints(path) for path in (old, new))
    assert len(old_packets) == len(new_packets) == sum(edits)
    start = 0
    for i, frames in enumerate(edits):
        end = start + frames
        if i in (0, 2) and old_packets[start:end] != new_packets[start:end]:
            assert native.decoded_range(old, start, frames) == native.decoded_range(new, start, frames)
        start = end


def render_episode(episode, native_cuts, timing, plan, fingerprint, output):
    number = episode["id"]
    old = V4 / number
    dest = output / number
    dest.mkdir(parents=True, exist_ok=True)
    receipt = dest / "verification.json"
    if receipt.exists():
        result = read(receipt)
        assert result["revisionId"] == fingerprint
        for flavor in ("clean", "captioned"):
            assert sha(dest / f"{flavor}.mp4") == result[flavor]["sha256"]
        return result

    record = deepcopy(read(old / "verification.json"))
    edits = [piece["frames"] for piece in record["cuts"]]
    assert edits[0] == edits[1] and edits[2] == edits[3]
    index = 1 if number in ACTION else 2 if number in DARK_ENVIRONMENT else 0
    track = plan["music"][index]
    sound, mix = mixed_sound(number, track, edits, dest)
    for cut in native_cuts:
        key = cut["id"]
        entry = explanation(episode, timing[key], cut, plan["phases"][key], dest)
        record["cuts"][int(key[-1])].update(unity=entry, picture=VERSION)
    for flavor in ("captioned", "clean"):
        prior_movie = old / f"{flavor}.mp4"
        assert sha(prior_movie) == record[flavor]["sha256"]
        listing = (old / f"{flavor}.txt").read_text(encoding="utf-8").splitlines()
        assert len(listing) == 4 and all(re.fullmatch(r"file '[^']+'", line) for line in listing)
        for i in (1, 3):
            listing[i] = f"file '{(dest / f'{i}-{flavor}.mp4').as_posix()}'"
        input_list = dest / f"{flavor}.txt"
        input_list.write_text("\n".join(listing) + "\n", encoding="utf-8")
        movie = dest / f"{flavor}.mp4"
        edit.ffmpeg("-f", "concat", "-safe", 0, "-i", input_list, "-i", sound,
                    "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart", movie)
        verify_gameplay(movie, prior_movie, edits)
        assert track_sha(movie, "a") == track_sha(sound, "a")
        record[flavor] = edit.validate(movie, sum(edits))
    for language in ("ko", "en"):
        file = f"{language}.srt"
        shutil.copy2(old / file, dest / file)
        assert sha(dest / file) == record["subtitles"][language]
    record.pop("previousVoiceAndMusicPreserved", None)
    record.update(revisionId=fingerprint, existingNarrationPreserved=True, music=track | {
        "adjustments": "excerpt, gain, fades, narration ducking",
        "adjustmentsKo": "길이, 음량, 페이드 및 내레이션에 맞춘 음량 조정",
        "mixEvidence": mix,
    }, audio=edit.rms_measure(dest / "captioned.mp4"))
    assert record["audio"] == {k: mix[k] for k in ("integratedLUFS", "truePeakDbTP")}
    save(receipt, record)
    print(f"{number}: two phase-guided Unity scenes, {track['title']}, {record['audio']}", flush=True)
    return record


def review(output, episodes, results, plan, fingerprint):
    cards = []
    for episode, report in zip(episodes, results, strict=True):
        number = episode["id"]
        position = 0
        scenes = []
        for cut in report["cuts"]:
            if cut["type"] == "explanation":
                guided = cut["unity"]
                links = []
                for frame, label, line in zip(guided["phaseStartsAtFrames"], PHASES, guided["phaseText"], strict=True):
                    sections = position + frame
                    links.append(f'<li><button data-position="{sections / 60:.6f}">{escape(label)}</button> {escape(line)}</li>')
                scene_uri = Path(guided["scenePath"]).as_uri()
                scenes.append("<ol>" + "".join(links) + "</ol>"
                              + f'<p><a href="{escape(scene_uri, quote=True)}">Unity 씬 파일</a></p>')
            position += cut["frames"]
        music = report["music"]
        title = escape(episode["title"])
        source_title, source_url = edit.SOURCE_ROWS[int(number)]
        cuts = " ".join(f'<li>{escape(cut["observed"])} <a href="{escape(cut["url"], quote=True)}">플레이 출처</a></li>'
                        for cut in report["cuts"] if cut["type"] == "gameplay")
        cards.append(f'<article id="ep{number}"><h2>{number}. {title}</h2>'
                     f'<video controls preload="none" src="{number}/captioned.mp4"></video>'
                     f'<p>{report["gameplaySeconds"]:g}초 실제 플레이 + {report["explanationSeconds"]:g}초 Unity 시연</p>'
                     f'<p><a href="{number}/captioned.mp4">자막 영상</a> · <a href="{number}/clean.mp4">클린 영상</a> · '
                     f'<a href="{number}/ko.srt">한글 SRT</a> · <a href="{number}/en.srt">영어 SRT</a></p>'
                     '<details><summary>시연 단계와 장면으로 이동</summary>' + ''.join(scenes) + '</details>'
                     f'<details><summary>자료와 실제 플레이 출처</summary><ul>{cuts}</ul>'
                     f'<p><a href="{escape(source_url, quote=True)}">{escape(source_title)}</a></p></details>'
                     f'<p>배경음악 <a href="{escape(music["source"], quote=True)}">{escape(music["title"])}</a></p></article>')
    nav = " ".join(f'<a href="#ep{e["id"]}">{e["id"]}</a>' for e in episodes)
    credits = " · ".join(f'<a href="{m["source"]}">{escape(m["title"])}</a>' for m in plan["music"])
    page = f"""<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>엘든 링 개발 쇼츠 36편 PC 검수</title>
<style>
body{{margin:auto;max-width:1240px;padding:26px;background:#10191e;color:#f6f6e9;font:16px/1.65 "Malgun Gothic",sans-serif}}
h1,h2{{color:#ffd88f;line-height:1.35}}h2{{font-size:22px}}a{{color:#83ecd9}}nav a{{display:inline-block;margin:4px 7px}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,350px),1fr));gap:19px}}
article{{padding:18px;background:#1c2b32;border:1px solid #456067;border-radius:13px;scroll-margin:14px}}
video{{display:block;width:min(100%,284px);aspect-ratio:9/16;margin:auto;background:black}}
summary,button{{cursor:pointer}}button{{font:inherit;font-size:.85em;background:#223943;color:#e5ffef;border:1px solid #65918b;border-radius:4px}}
footer{{margin-block:24px}}
</style>
<h1>엘든 링 개발 쇼츠 36편 PC 검수</h1>
<p>Unity 시연 72구간에서 처음 상태, 조작, 화면의 결과를 순서대로 표시했습니다. 편별로 시연 단계 버튼을 누르면 해당 위치로 이동합니다.</p>
<p>실제 플레이 50% · Unity 시연 50% · <a href="manifest.json">편별 제작 및 음량 기록</a></p>
<nav>{nav}</nav><main>{''.join(cards)}</main>
<script>
document.addEventListener("click", event => {{
  const position = event.target.dataset.position;
  if (position === undefined) return;
  const video = event.target.closest("article").querySelector("video");
  const seek = () => {{video.currentTime = Number(position); video.play().catch(() => {{}});}};
  if (video.readyState > 0) seek();
  else {{video.addEventListener("loadedmetadata", seek, {{once:true}}); video.load();}}
}});
</script>
<footer>배경음악 {credits} · Kevin MacLeod (incompetech.com) ·
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · 길이·음량·페이드 조정</footer></html>"""
    result = dict(reviewVersion=VERSION, revisionId=fingerprint, count=len(results),
                  demonstrationCuts=2*len(results), humanReview="pending",
                  music=plan["music"], originalSoundtrackPolicy=plan["originalSoundtrackPolicy"], episodes=results)
    edit.exact_write(output / "manifest.json", json.dumps(result, ensure_ascii=False, indent=2))
    edit.exact_write(output / "index.html", page)
    links = native.ReviewLinks(output)
    links.feed(page)
    assert links.media == [f"{episode['id']}/captioned.mp4" for episode in episodes]
    save(output / "audit.json", dict(reviewVersion=VERSION, revisionId=fingerprint, count=len(results),
                                    demonstrationCuts=2*len(results), reviewPage=(output/"index.html").as_posix(),
                                    reviewPageSha256=sha(output/"index.html"),
                                    manifestSha256=sha(output/"manifest.json"), planSha256=sha(PLAN_FILE),
                                    previousUnityAuditSha256=sha(V4/"audit.json"),
                                    humanReview="pending", musicRights=plan["music"]))
    print(f"Verified local PC review: {output / 'index.html'}", flush=True)


def main():
    parser = ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    assert args.execute != args.pilot
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    plan = read(PLAN_FILE)
    episodes, _, timing = native.load_plan()
    prior = read(V4 / "audit.json")
    pinned = read(HERE / "review-receipt-v4.json")
    assert prior["manifestSha256"] == pinned["manifestSha256"] == sha(V4/"manifest.json")
    assert prior["reviewPageSha256"] == pinned["reviewPageSha256"] == sha(V4/"index.html")
    assert prior["count"] == 36 and prior["assetLibraryCuts"] == 72
    native_cuts = {episode["id"]: episode["cuts"] for episode in prior["results"]}
    assert set(plan["phases"]) == set(timing)
    output = WORK / "pilot" if args.pilot else OUTPUT
    if args.pilot:
        episodes = [episode for episode in episodes if episode["id"] in {"01","07","29"}]
    else:
        assert len(episodes) == 36
    fingerprint = sha256((sha(PLAN_FILE) + sha(Path(__file__)) + sha(V4/"audit.json")).encode()).hexdigest()
    results = [render_episode(episode, native_cuts[episode["id"]], timing, plan, fingerprint, output)
               for episode in episodes]
    review(output, episodes, results, plan, fingerprint)


if __name__ == "__main__":
    main()

