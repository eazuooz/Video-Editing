import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import wave

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = json.loads((HERE / "review-plan-v2.json").read_text(encoding="utf-8"))
FOOTAGE = ROOT / "production/batches/animation-18-20261031/contrast-v5/footage/local"
MUSIC = ROOT / "shared/assets/music/incompetech/Wholesome.mp3"
FOOTAGE_URLS = {
    "jump": ("RBGamer05", "https://www.youtube.com/watch?v=8kNea5T5YS4"),
    "margit": ("Teal Nation Ent", "https://www.youtube.com/watch?v=sOA7HyK7Qcg"),
}
MOD_PATH = ROOT / "projects/shorts-elden-ring-screen-space-decals/render_review.py"
spec = importlib.util.spec_from_file_location("decal_reference", MOD_PATH)
decal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decal)

FPS = 24
W, H = 1080, 1920
BG, INK, MUTED = "#10171b", "#f8f4e8", "#c2d2d7"
GOLD, BLUE, EDGE = "#ffd893", "#7ce4df", "#35555c"
PANEL = (25, 266, 490, 345)


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def ffmpeg(*args):
    return run(["ffmpeg", "-y", "-hide_banner", "-nostdin", "-loglevel", "error", *map(str, args)])


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def panel_point(x, y, z, offset, scale):
    return (offset[0] + (x - .52 * y) * scale,
            offset[1] + (.37 * x + .41 * y - z) * scale)


def terrain_panel(draw, offset, scale, columns, heights, edits=False):
    project = lambda i, j: panel_point(columns[i], j, heights[i], offset, scale)
    for i in range(len(columns) - 1):
        for j in range(4):
            face = [project(i, j), project(i + 1, j), project(i + 1, j + 1), project(i, j + 1)]
            rise = abs(heights[i + 1] - heights[i])
            base = "#376761" if rise < .3 else "#8e693f"
            draw.polygon(face, fill=base)
            draw.line(face + [face[0]], fill="#141e22", width=1)
            if edits:
                draw.line((face[0], face[2]), fill="#a48755", width=1)
    for i in range(len(columns)):
        for j in range(5):
            x, y = project(i, j)
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=GOLD if edits and 2 <= i <= 3 else BLUE)


def profile(draw, xy, columns, heights, size, marker=2.5):
    x, y = xy
    width, height = size
    p = lambda u, z: (x + width * u / 5, y - height * z / 1.6)
    marker_x = p(marker, 0)[0]
    draw.line((marker_x, y - height - 8, marker_x, y + 7), fill=GOLD, width=2)
    draw.line((x, y, x + width, y), fill=EDGE, width=2)
    vertices = [p(u, z) for u, z in zip(columns, heights)]
    draw.line(vertices, fill=BLUE, width=3)
    for vx, vy in vertices:
        draw.ellipse((vx - 3, vy - 3, vx + 3, vy + 3), fill=INK)


def center(draw, y, text, size, color=INK):
    draw.text((270, y), text, font=decal.font(size, True), fill=color, anchor="mt")


def terrain_demo(draw, mode, seconds):
    phase = min(1, max(0, (seconds - 0.9) / 2.5))
    if mode == "grid":
        base = [0.3, .36, .37 + phase * .59, .38 + phase * 1.12, .45 + phase * .60, .39]
        terrain_panel(draw, (167, 377), 54, list(range(6)), base)
        profile(draw, (83, 556), list(range(6)), base, (372, 60), marker=3.0)
        center(draw, 579, "격자 위 점의 높이를 바꾸면 언덕이 생깁니다", 17, BLUE)
        return
    fixed_columns = list(range(6))
    fixed_heights = [.34, .34, .34, .34 + 1.15 * phase, .34 + 1.15 * phase, .34 + 1.15 * phase]
    mesh_columns = [0, 1.45, 2.40, 2.60, 3.85, 5]
    mesh_heights = [.34, .34, .34, .34 + 1.15 * phase, .34 + 1.15 * phase, .34 + 1.15 * phase]
    if mode == "compare":
        for offset, x, label, cols, vals, edit in (
            ((97, 391), 49, "고정 격자", fixed_columns, fixed_heights, False),
            ((346, 391), 298, "직접 편집한 메시", mesh_columns, mesh_heights, True),
        ):
            draw.text((x, 310), label, font=decal.font(20, True), fill=INK)
            terrain_panel(draw, offset, 26, cols, vals, edit)
            profile(draw, (x, 538), cols, vals, (190, 58))
        center(draw, 582, "금색 선은 만들려는 단차의 위치", 17, GOLD)
    else:
        edited = mode == "mesh"
        cols, vals = (mesh_columns, mesh_heights) if edited else (fixed_columns, fixed_heights)
        terrain_panel(draw, (167, 377), 54, cols, vals, edited)
        profile(draw, (83, 556), cols, vals, (372, 64))
        label = "단차 양쪽의 점을 선택해 직접 이동" if edited else "금색 선 양쪽에서 가장 가까운 기존 점을 조정"
        center(draw, 580, label, 17, GOLD)


def wrap(draw, message, font, width):
    lines = []
    line = ""
    for word in message.split():
        next_line = f"{line} {word}".strip()
        if line and draw.textlength(next_line, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = next_line
    return lines + ([line] if line else [])


def base_canvas(project, key, scene, index):
    kind, source, _, title, korean, _ = scene
    canvas = Image.new("RGB", (540, 960), BG)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((25, 54, 160, 91), radius=8, fill="#24383c")
    d.text((39, 63), project["tag"], font=decal.font(16, True), fill=BLUE)
    center(d, 119, project["title"][0], 41, GOLD)
    center(d, 169, project["title"][1], 40, GOLD)
    d.line((26, 225, 514, 225), fill=EDGE)
    label = "엘든 링 실제 플레이" if kind == "game" else "자체 원리 시연"
    d.text((26, 238), label, font=decal.font(16, True), fill=GOLD if kind == "game" else BLUE)
    d.rounded_rectangle((24, 265, 516, 612), radius=5, fill="#152127", outline=EDGE)
    if kind == "game":
        recorder = FOOTAGE_URLS[source][0]
        d.text((28, 624), f"플레이 촬영  {recorder}", font=decal.font(15), fill=MUTED)
    else:
        d.text((28, 624), "원리 설명용으로 만든 장면", font=decal.font(15), fill=MUTED)
    center(d, 667, title, 25)
    if key == "decals" and index == 0:
        center(d, 704, "진흙 발자국 근거 · 별도 PC 프레임 분석", 14, MUTED)
    if key == "terrain" and index == 4:
        center(d, 704, "개발진 공개 사례 · Too 메이킹 2022", 14, MUTED)
    d.rectangle((25, 733, 515, 873), fill="#18252b")
    caption = decal.font(23, True)
    lines = wrap(d, korean, caption, 445)
    for n, line in enumerate(lines):
        d.text((270, 756 + n * 34), line, font=caption, fill=INK, anchor="mt")
    for m in range(8):
        x = 25 + m * 62
        d.rounded_rectangle((x, 904, x + 55, 909), radius=2, fill=BLUE if m == index else EDGE)
    return canvas


def demo_frame(base, key, mode, seconds):
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas)
    if key == "terrain":
        terrain_demo(draw, mode, seconds)
    elif mode == "compare":
        for k, enabled in enumerate((False, True)):
            y = 274 + k * 164
            canvas.paste(decal.color_frame(.7, 472, 155, mode, enabled), (34, y))
            decal.chip(draw, 42, y + 9, "방향 검사 켬" if enabled else "방향 검사 끔", BLUE if enabled else GOLD)
    elif mode == "depth":
        for k, current in enumerate(("depth", "reconstruct")):
            y = 274 + k * 164
            canvas.paste(decal.color_frame(.35 + min(seconds, 7) * .12, 472, 155, current), (34, y))
            decal.chip(draw, 42, y + 9, "화면의 깊이" if k == 0 else "복원한 공간 좌표", BLUE)
    else:
        canvas.paste(decal.color_frame(seconds * .46, 488, 343, mode), (26, 267))
    return canvas.resize((W, H), Image.Resampling.BICUBIC)


def process(args):
    return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def write_visual(project, key, scene, index, frames, target):
    kind, source, start, _, _, _ = scene
    base = base_canvas(project, key, scene, index)
    game_decoder = None
    if kind == "game":
        source_path = FOOTAGE / f"elden-{source}.mp4"
        game_decoder = process([
            "ffmpeg", "-v", "error", "-ss", str(start), "-i", str(source_path), "-an",
            "-threads", "2", "-filter_threads", "1", "-vf", f"fps={FPS},crop=1536:1080,scale=980:690",
            "-frames:v", str(frames), "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1",
        ])
        game_base = base.resize((W, H), Image.Resampling.LANCZOS)
    encoder = process([
        "ffmpeg", "-y", "-v", "error", "-threads", "2", "-filter_threads", "1",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-an", "-c:v", "libx264", "-threads", "3", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
        "-crf", "19", str(target),
    ])
    try:
        for i in range(frames):
            if game_decoder:
                raw = game_decoder.stdout.read(980 * 690 * 3)
                if len(raw) != 980 * 690 * 3:
                    raise RuntimeError(f"Footage ended while decoding {key} scene {index + 1}, frame {i}")
                canvas = game_base.copy()
                canvas.paste(Image.frombytes("RGB", (980, 690), raw), (50, 532))
            else:
                canvas = demo_frame(base, key, source, i / FPS)
            encoder.stdin.write(canvas.tobytes())
    finally:
        encoder.stdin.close()
        if game_decoder:
            game_decoder.stdout.close()
        end = encoder.wait()
        if game_decoder and game_decoder.wait() != 0:
            raise RuntimeError(f"Footage decoder failed for {target.name}")
        if end != 0:
            raise RuntimeError(f"Encoder failed for {target.name}")


def duration(path):
    with wave.open(str(path)) as f:
        return f.getnframes() / f.getframerate()


def levels(path):
    result = run(["ffmpeg", "-hide_banner", "-v", "info", "-i", str(path), "-vn",
                  "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    result = json.loads(re.findall(r"\{\s*\"input_i\"[\s\S]*?\}", result.stderr.decode())[-1])
    return {"integratedLUFS": float(result["input_i"]), "truePeakDbTP": float(result["input_tp"])}


def list_path(paths, file):
    file.write_text("".join(f"file '{p.name}'\n" for p in paths), encoding="ascii")
    return file


def timecode(frames):
    ms = round(frames * 1000 / FPS)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def render_project(key, output):
    project = PLAN[key]
    audio_inputs = [output / f"{key}-voice-{i:02}.wav" for i in range(8)]
    lengths = [math.ceil((max(duration(a), duration(b)) + .27) * FPS / 3) * 3
               for a, b in zip(audio_inputs[::2], audio_inputs[1::2])]
    slots = [size for size in lengths for _ in (0, 1)]
    visuals, audio, edits, ko, en = [], [], [], [], []
    running = 0
    for i, (count, scene, voice) in enumerate(zip(slots, project["scenes"], audio_inputs)):
        visual = output / f"{key}-visual-{i:02}.mp4"
        print(f"{key} scene {i + 1}/8, {count / FPS:.3f}s", flush=True)
        write_visual(project, key, scene, i, count, visual)
        visuals.append(visual)
        padded = output / f"{key}-padded-{i:02}.wav"
        ffmpeg("-i", voice, "-af", f"adelay=120:all=1,apad=whole_dur={count / FPS:.6f}",
               "-t", f"{count / FPS:.6f}", "-ar", 48000, "-ac", 1, padded)
        audio.append(padded)
        start_caption, end_caption = timecode(running), timecode(running + count)
        for data, caption in ((ko, scene[4]), (en, scene[5])):
            data.append(f"{i + 1}\n{start_caption} --> {end_caption}\n{caption}\n")
        edits.append({"startFrame": running, "frameCount": count, "kind": scene[0], "label": scene[3]})
        if scene[0] == "game":
            who, url = FOOTAGE_URLS[scene[1]]
            src = FOOTAGE / f"elden-{scene[1]}.mp4"
            edits[-1]["footage"] = {"path": str(src), "sha256": sha(src), "recorder": who, "url": url,
                                    "start": scene[2], "endExclusive": scene[2] + count / FPS}
        running += count
    for language, data in (("ko", ko), ("en", en)):
        (output / f"{key}.{language}.srt").write_text("\n".join(data), encoding="utf-8")
    total = running / FPS
    voice_pcm = output / f"{key}-narration.wav"
    ffmpeg("-f", "concat", "-safe", 0, "-i", list_path(audio, output / f"{key}-voice-list.txt"),
           "-c:a", "pcm_s16le", voice_pcm)
    foreground = output / f"{key}-narration-mixed-level.wav"
    voice_level = levels(voice_pcm)
    voice_gain = -16.8 - voice_level["integratedLUFS"]
    ffmpeg("-i", voice_pcm, "-af", f"volume={voice_gain:.2f}dB,alimiter=limit=0.83:level=false:latency=true",
           "-ac", 2, foreground)
    bg_base = output / f"{key}-music-cut.wav"
    ffmpeg("-ss", "13" if key == "decals" else "42", "-i", MUSIC, "-t", total, "-ar", 48000, bg_base)
    bed = output / f"{key}-music-mixed-level.wav"
    music_gain = -32.0 - levels(bg_base)["integratedLUFS"]
    ffmpeg("-i", bg_base, "-af", f"volume={music_gain:.2f}dB,afade=t=in:d=0.4,afade=t=out:st={total - 0.8}:d=0.8", bed)
    final = output / f"{key}-review-v2.mp4"
    ffmpeg("-f", "concat", "-safe", 0, "-i", list_path(visuals, output / f"{key}-visual-list.txt"),
           "-i", foreground, "-i", bed, "-filter_complex",
           "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=false:latency=true[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-t", total, "-movflags", "+faststart", final)
    render_clean(final, output / f"{key}-clean-v2.mp4")
    raw = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(final)])
    probe = json.loads(raw.stdout)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    assert int(video["nb_frames"]) == running
    assert (video["width"], video["height"]) == (W, H)
    assert sum(slots[::2]) == sum(slots[1::2]) == running // 2
    assert all(duration(a) + .12 < frame / FPS for a, frame in zip(audio_inputs, slots))
    result = {"path": str(final), "sha256": sha(final), "frames": running, "fps": FPS,
              "seconds": total, "gameplaySeconds": sum(slots[::2]) / FPS,
              "demoSeconds": sum(slots[1::2]) / FPS, "cuts": edits,
              "audio": {"voice": levels(foreground), "music": levels(bed), "encoded": levels(final),
                        "voiceProfile": "Microsoft Heami Desktop, temporary Korean review voice",
                        "musicTrack": "Wholesome – Kevin MacLeod", "musicLicense": "CC BY 4.0",
                        "musicSha256": sha(MUSIC), "originalGameAudio": False},
              "subtitles": {language: sha(output / f"{key}.{language}.srt") for language in ("ko", "en")}}
    (output / f"{key}-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def render_clean(captioned, output):
    ffmpeg("-i", captioned, "-vf", "drawbox=x=0:y=1460:w=iw:h=296:color=0x10171b:t=fill",
           "-c:v", "libx264", "-threads", 3, "-preset", "veryfast", "-crf", 17,
           "-c:a", "copy", "-movflags", "+faststart", output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--only", choices=tuple(PLAN))
    args = parser.parse_args()
    for key in ([args.only] if args.only else PLAN):
        render_project(key, args.output.resolve())


if __name__ == "__main__":
    main()
