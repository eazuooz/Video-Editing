"""Clarify the existing Elden Ring 02 short with a viewing-ray diagram and Unity footage."""

from html.parser import HTMLParser
from math import exp
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, ImageDraw
import psutil

import render_established_format_v6 as film

OLD = film.OUT
OUT = OLD.with_name("pc-review-v7")
WORK = Path("D:/YamyamProduction/elden-ring-development-36-raymarch-v7")
EPISODE = "02"
BLACK = (0, 0, 0)
PANEL = (14, 26, 36)
TEAL = (115, 199, 194)
GOLD = (232, 207, 131)
WHITE = (245, 245, 245)
MUTED = (164, 181, 195)
FOG_LIGHT = (154, 186, 196)
CAMERA_X, ROCK_X = 134, 856
SAMPLES = (228, 338, 448, 558, 668, 778)
DENSITIES = (0.12, 0.23, 0.78, 0.92, 0.42, 0.13)
RAY_DEMO = {
    1: (480, "해설용 모형 · 화면의 한 점", "Unity 시연 · 가까운 안개의 형태"),
    3: (540, "해설용 모형 · 가까운 안개와 먼 안개", "Unity 시연 · 먼 안개와 이어지는 풍경"),
}
REFERENCES = {
    "developerTalk": "https://cedec.cesa.or.jp/2022/session/detail/124.html",
    "rayTransmittance": "https://pbr-book.org/4ed/Volume_Scattering/Transmittance",
}


def text(draw, x, y, value, font, color=WHITE, anchor="mm"):
    assert font.getlength(value) <= 930, value
    draw.text((x, y), value, fill=color, font=font, anchor=anchor)


def camera(draw, x, y):
    draw.rounded_rectangle((x-48, y-28, x+20, y+28), radius=9, fill=PANEL, outline=TEAL, width=4)
    draw.polygon([(x+20, y-12), (x+48, y-22), (x+48, y+22), (x+20, y+12)], fill=TEAL)


def rock(draw, x, ground_y, scale, opacity=0.0):
    def softened(rgb):
        return tuple(round(color*(1-opacity)+fog*opacity) for color, fog in zip(rgb, FOG_LIGHT))

    silhouette = ((-46, 0), (-35, -38), (-11, -65), (23, -60), (43, -30), (56, 0))
    face = ((-35, -38), (-11, -65), (23, -60), (13, -23), (-10, 0), (-46, 0))
    for points, color in ((silhouette, (36, 49, 63)), (face, (71, 92, 107))):
        draw.polygon([(x+scale*a, ground_y+scale*b) for a,b in points], fill=softened(color))


def ray(draw, x0, x1, y, color):
    draw.line((x0, y, x1, y), fill=color, width=4)
    draw.polygon(((x1, y), (x1-14, y-8), (x1-14, y+8)), fill=color)


def dot(draw, x, y, radius, color, outline=None):
    draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill=color, outline=outline, width=3)


def near_scene(base, painter, second):
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    label, note = painter.label, painter.body
    ray_y = 746
    draw.rounded_rectangle((30, 512, 954, 911), radius=18, fill=PANEL)
    text(draw, CAMERA_X-9, 582, "카메라", label, TEAL)
    text(draw, ROCK_X, 582, "뒤 바위", label)
    camera(draw, CAMERA_X, ray_y)
    rock(draw, ROCK_X, 786, 1.22)
    text(draw, 488, 582, "화면의 한 점이 보는 방향", note)
    for offset, density in zip(SAMPLES, DENSITIES, strict=True):
        shade = tuple(round(a + (b-a)*density) for a,b in zip(PANEL, FOG_LIGHT))
        draw.rounded_rectangle((offset-50, 657, offset+50, 815), radius=7, fill=shade)
    ray(draw, 183, 800, ray_y, GOLD)
    progress = min(len(SAMPLES), max(0.0, (second-1.1)/0.68))
    finished = int(progress)
    for index, offset in enumerate(SAMPLES):
        if index < finished:
            dot(draw, offset, ray_y, 12, GOLD)
        else:
            dot(draw, offset, ray_y, 10, PANEL, GOLD)
    if finished < len(SAMPLES) and progress > 0:
        dot(draw, SAMPLES[finished], ray_y, 15, GOLD)
    text(draw, 490, 867, "옅은 곳과 짙은 곳을 차례로 확인", label)
    optical_depth = sum(DENSITIES[:finished])
    if finished < len(DENSITIES):
        optical_depth += (progress-finished)*DENSITIES[finished]
    haze = 1-exp(-0.91*optical_depth)

    # Constant fog lighting in this teaching example. Every segment attenuates
    # the same background ray; the fog itself adds light along that viewing ray.
    for center, fog, legend in ((260, 0, "안개가 없을 때"), (724, haze, "안개를 통과한 뒤")):
        sky = tuple(round(a*(1-fog)+b*fog) for a,b in zip((101,137,154), FOG_LIGHT))
        ground = tuple(round(a*(1-fog)+b*fog) for a,b in zip((47,69,83), FOG_LIGHT))
        draw.rounded_rectangle((center-202, 963, center+202, 1196), radius=12, fill=sky)
        draw.rectangle((center-202, 1141, center+202, 1196), fill=ground)
        rock(draw, center, 1141, 2.05, fog)
        dot(draw, center, 1078, 8, None, GOLD)
        text(draw, center, 1240, legend, label)
    bottom = ("이 방향을 조금씩 따라가며 안개를 확인" if second < 1.1 else
              "확인한 안개가 쌓이면서 바위가 흐려짐" if second < 5.7 else
              "Ray Marching (레이 마칭)")
    text(draw, 492, 1397, bottom, note, GOLD)
    return frame


def far_scene(base, painter, second):
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    label, note = painter.label, painter.body
    stage_end = 0.8 + 18*0.17
    for chosen, y, title in ((False, 650, "모든 거리를 같은 간격으로 확인"), (True, 1020, "엘든 링의 계산 분담")):
        draw.rounded_rectangle((30,y-130,954,y+138), radius=18, fill=PANEL)
        text(draw, 492, y-75, title, note)
        camera(draw, 103, y+7)
        rock(draw, 886, y+32, 0.76, 0.4)
        ray(draw, 151, 849, y+7, MUTED)
        split_x = 372
        if chosen:
            draw.rounded_rectangle((split_x, y-18, 833, y+33), radius=10, fill=(84,119,130))
            ray(draw, split_x, 848, y+7, TEAL)
            draw.text((260,y+82), "가까이: 여러 지점", fill=GOLD, font=label, anchor="mm")
            draw.text((640,y+82), "멀리: 간단한 안개 계산", fill=TEAL, font=label, anchor="mm")
        else:
            text(draw, 490, y+82, "거리가 늘면 확인할 지점도 늘어남", label)
        count = 6 if chosen else 18
        active = int((second-0.8)/0.17)+1
        for index in range(count):
            x = 161 + index*38
            dot(draw, x, y+7, 7, GOLD if index < active else PANEL, GOLD)
    bottom = "같은 간격으로 확인하면 먼 곳까지 일일이 확인" if second < stage_end else "가까이의 형태와 멀리의 깊이"
    text(draw, 492, 1376, bottom, note, GOLD)
    return frame


def encode_diagram(base, painter, draw_scene, frames, target):
    assert frames % 2 == 0
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1080x1920", "-framerate", "30",
        "-i", "pipe:0", "-vf", "fps=60,format=yuv420p", "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "ultrafast", "-threads", "4", "-crf", "19", str(target),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as process:
        for frame in range(frames//2):
            process.stdin.write(draw_scene(base, painter, frame/30).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError(f"Could not encode {target}")


def native_tail(painter, source, offset, frames, label, folder, index):
    base = folder/f"{index}-unity.png"
    picture = painter.base(label)
    picture.save(base)
    target = folder/f"{index}-unity.mp4"
    x,y,w,h = film.rectangles((950,650))
    film.edit.ffmpeg("-loop",1,"-framerate",60,"-i",base,"-ss",offset/60,"-i",source,
                    "-filter_complex_threads",2,"-filter_complex",
                    f"[1:v]scale={w}:{h}:flags=lanczos,format=rgba,setsar=1[body];[0:v][body]overlay={x}:{y}:shortest=1",
                    "-an","-frames:v",frames,"-c:v","libx264","-threads",4,"-preset","ultrafast",
                    "-crf",19,"-pix_fmt","yuv420p",target)
    return target


def write_list(paths, file):
    file.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8")
    return file


class LocalMedia(HTMLParser):
    def __init__(self):
        super().__init__()
        self.media = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href","src"} and re.fullmatch(r"(?:\.\./pc-review-v6/)?\d\d/[\w.]+", value):
                self.media.append(value)


def update_page():
    html = (OLD/"index.html").read_text(encoding="utf-8")
    start = '<article id="ep02">'
    before, partition, rest = html.partition(start)
    assert partition
    original, end_tag, after = rest.partition("</article>")
    assert end_tag
    changes = {
        "시선이 안개를 통과": "카메라가 화면의 한 점을 보는 방향",
        "노란 선 위의 점에서 밀도 읽기": "옅은 안개와 짙은 안개를 차례로 확인",
        "읽은 밀도를 합쳐 안개를 표시": "안개가 쌓일수록 뒤 바위가 흐려지는 결과",
        "가까운 안개부터 계산": "멀리까지 같은 간격으로 확인하는 경우",
        "가까운 곳에 표본을 촘촘히": "가까운 곳은 여러 지점, 먼 곳은 간단한 안개 계산",
        "먼 안개는 적은 표본으로 이어짐": "가까운 형태와 먼 풍경의 깊이를 함께 표현",
        "23초 실제 플레이 + 23초 Unity 시연": "23초 실제 플레이 + 23초 안개 원리 설명과 Unity 시연",
    }
    for previous, current in changes.items():
        assert previous in original
        original = original.replace(previous, current, 1)
    for previous, current in ((12.05, 12.1), (15.483333, 16.7), (35.65, 37.9), (38.966667, 43.0)):
        original = original.replace(f'data-position="{previous:.6f}"', f'data-position="{current:.6f}"')
    html = before + partition + original + end_tag + after
    html = re.sub(r'((?:src|href)=")(?!02/)(\d\d/)', r"\1../pc-review-v6/\2", html)
    html = html.replace("실제 플레이 50% · Unity 시연 50%", "실제 플레이 50% · 원리 설명 50%", 1)
    parser = LocalMedia()
    parser.feed(html)
    assert len(set(parser.media)) == 144
    assert all((OUT/link).is_file() for link in parser.media)
    assert 'src="02/captioned.mp4"' in html
    (OUT/"index.html").write_text(html, encoding="utf-8")


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    prior = OLD/EPISODE
    dest = OUT/EPISODE
    dest.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    v6 = film.read(film.HERE/"review-receipt-v6.json")
    assert film.sha(OLD/"index.html") == v6["reviewPageSha256"]
    assert film.sha(OLD/"manifest.json") == v6["manifestSha256"]
    manifest = film.read(OLD/"manifest.json")
    record = film.read(prior/"verification.json")
    assert manifest["episodes"][1] == record
    prior_hash = film.sha(prior/"clean.mp4")
    assert prior_hash == record["clean"]["sha256"]
    mixer = film.native.track_sha(prior/"clean.mp4","a")
    assert mixer == film.native.track_sha(prior/"captioned.mp4","a")
    painter = film.compositor(film.read(film.FORMAT), EPISODE)
    painter.body = painter.label.font_variant(size=42)
    parts = []
    revisions = {}
    for index, cut in enumerate(record["cuts"]):
        if index not in RAY_DEMO:
            parts.append(prior/f"{index}-clean.mp4")
            continue
        diagram_frames, label, native_label = RAY_DEMO[index]
        draw = near_scene if index == 1 else far_scene
        diagram = WORK/f"{index}-diagram.mp4"
        base = painter.base(label)
        encode_diagram(base, painter, draw, diagram_frames, diagram)
        parts.append(diagram)
        native = Path(cut["unity"]["path"])
        assert film.sha(native) == cut["unity"]["sha256"]
        parts.append(native_tail(painter,native,diagram_frames,cut["frames"]-diagram_frames,native_label,WORK,index))
        revisions[f"{EPISODE}-{index}"] = {
            "diagramFrames": diagram_frames, "unityFrames": cut["frames"]-diagram_frames,
            "unitySourceSha256": cut["unity"]["sha256"], "diagramSha256": film.sha(diagram),
        }
    frames = sum(cut["frames"] for cut in record["cuts"])
    clean = dest/"clean.mp4"
    film.edit.ffmpeg("-f","concat","-safe",0,"-i",write_list(parts,WORK/"clean.ffconcat"),"-i",prior/"clean.mp4",
                    "-map","0:v:0","-map","1:a:0","-c","copy","-movflags","+faststart",clean)
    assert film.native.track_sha(clean,"a") == mixer
    record["clean"] = film.edit.validate(clean,frames)
    subtitle_input,cues = film.caption_track(EPISODE,painter,film.read(film.CAPTIONS)["paragraphs"],frames,WORK)
    captioned = dest/"captioned.mp4"
    film.edit.ffmpeg("-reinit_filter",0,"-threads",2,"-i",clean,"-f","concat","-safe",0,"-i",subtitle_input,
                    "-filter_complex_threads",2,"-filter_complex","[0:v][1:v]overlay=0:1470:eof_action=pass:shortest=1[out]",
                    "-map","[out]","-map","0:a:0","-c:v","libx264","-threads",4,"-preset","ultrafast","-crf",19,
                    "-c:a","copy","-frames:v",frames,"-pix_fmt","yuv420p","-movflags","+faststart",captioned)
    assert film.native.track_sha(captioned,"a") == mixer
    record["captioned"] = film.edit.validate(captioned,frames)
    record["captionPixelReview"] = film.caption_pixels(captioned,cues,WORK)
    for language in ("ko","en"):
        name = f"{language}.srt"
        shutil.copyfile(prior/name,dest/name)
        assert film.sha(dest/name) == record["subtitles"][language]
    assert (WORK/"ko.srt").read_bytes() == (dest/"ko.srt").read_bytes()
    record["rayMarchingRevision"] = {"formatBase":"v6","sources":REFERENCES,"explanations":revisions}
    record["reviewStatus"] = "pending"
    film.save(dest/"verification.json",record)
    manifest["episodes"][1] = record
    manifest["reviewVersion"] = "ray-marching-02-v7"
    film.save(OUT/"manifest.json",manifest)
    update_page()
    film.save(OUT/"audit.json", {
        "episode": EPISODE, "masterFrames": frames, "audioTrackSha256": mixer,
        "sourceReviewPageSha256": v6["reviewPageSha256"], "reviewPageSha256":film.sha(OUT/"index.html"),
        "manifestSha256":film.sha(OUT/"manifest.json"), "scriptSha256":film.sha(Path(__file__)),
        "record":record,
    })
    print(OUT/"index.html")


if __name__ == "__main__":
    main()
