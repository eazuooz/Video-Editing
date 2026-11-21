import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / "projects/shorts-elden-ring-screen-space-decals/elden-ring-development-research.md"
TITLES = {
    "decals": "카메라를 돌려도 발자국이 남는 이유",
    "terrain": "엘든 링은 왜 땅을 만드는 법을 바꿨나",
}
DESCRIPTIONS = {
    "decals": "엘든 링의 진흙 발자국을 출발점으로 화면의 깊이, 3차원 위치 복원, 투영 상자, 벽에 무늬가 번지는 것을 막는 방법을 순서대로 보여줍니다. 실제 플레이 장면은 바닥과 벽을 보는 예시입니다. 진흙 발자국의 렌더 단계는 별도의 PC 프레임 분석에서 확인했습니다.",
    "terrain": "엘든 링이 플레이에 필요한 단차를 세밀하게 편집하기 위해 초기 하이트맵에서 폴리곤 메시 편집으로 전환한 과정을 다룹니다. 두 시연은 같은 단차를 목표로 합니다. 실제 플레이에 나오는 지형을 제작진의 변경 결정이 일어난 특정 장소로 지목하지 않습니다.",
}
CREDIT = "Wholesome by Kevin MacLeod (incompetech.com) · CC BY 4.0 · 길이, 페이드 및 음량 조정"
POLICY = {
    "developer": "https://www.fromsoftware.jp/ww/faq-other.html",
    "publisher": "https://static.bandainamcoent.eu/content/BANDAI_NAMCO_Entertainment_Video_Policy_%2820220124%29.pdf",
    "decals": "https://mamoniem.com/behind-the-pretty-frames-elden-ring/#decals",
    "terrain": "https://www.4gamer.net/games/463/G046388/20220715099/",
    "license": "https://creativecommons.org/licenses/by/4.0/",
}


def command(*args):
    return subprocess.run(args, capture_output=True, check=True).stdout


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def video_info(path, seconds, frames):
    command("ffmpeg", "-v", "error", "-xerror", "-threads", "3", "-i", str(path),
            "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-")
    info = json.loads(command("ffprobe", "-v", "error", "-show_streams",
                              "-show_format", "-of", "json", str(path)))
    vid = next(s for s in info["streams"] if s["codec_type"] == "video")
    aud = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (vid["width"], vid["height"], int(vid["nb_frames"]), vid["avg_frame_rate"]) == (1080, 1920, frames, "24/1")
    assert abs(float(vid["duration"]) - seconds) < .001
    assert abs(float(aud["duration"]) - seconds) < .025
    timing = json.loads(command("ffprobe", "-v", "error", "-select_streams", "v:0",
                                "-show_frames", "-show_entries", "frame=best_effort_timestamp",
                                "-of", "json", str(path)))
    timestamps = [frame["best_effort_timestamp"] for frame in timing["frames"]]
    numerator, denominator = map(int, vid["time_base"].split("/"))
    assert len(timestamps) == frames
    assert all(timestamp * numerator * 24 == frame_index * denominator
               for frame_index, timestamp in enumerate(timestamps))
    return {"file": path.name, "sha256": sha256(path), "videoCodec": vid["codec_name"],
            "audioCodec": aud["codec_name"], "audioSamplesPerSecond": int(aud["sample_rate"])}


def validate_subtitle(path, expected):
    raw = path.read_text(encoding="utf-8")
    cues = []
    for block in raw.strip().split("\n\n"):
        index, timing, text = block.split("\n", 2)
        assert int(index) == len(cues) + 1 and text.strip()
        raw_values = re.findall(r"\d+", timing)
        pairs = [list(map(int, raw_values[i:i+4])) for i in (0, 4)]
        start, end = [(h * 3600000 + m * 60000 + s * 1000 + ms) for h, m, s, ms in pairs]
        cues.append((start, end))
    assert len(cues) == 8
    assert cues[0][0] == 0 and cues[-1][1] == round(expected * 1000)
    assert all(a[1] == b[0] for a, b in zip(cues, cues[1:]))
    return {"file": path.name, "sha256": sha256(path), "cues": len(cues)}


def verify(output):
    report = {}
    for key in TITLES:
        data = json.loads((output / f"{key}-verification.json").read_text(encoding="utf-8"))
        print(f"Decoding and verifying {key}…", flush=True)
        assert data["gameplaySeconds"] == data["demoSeconds"] == data["seconds"] / 2
        assert [cut["kind"] for cut in data["cuts"]] == ["game", "demo"] * 4
        assert data["audio"]["encoded"]["truePeakDbTP"] < -1
        assert abs(data["audio"]["encoded"]["integratedLUFS"] + 16) < 1.5
        for cut in data["cuts"]:
            if "footage" in cut:
                source = cut["footage"]
                assert sha256(Path(source["path"])) == source["sha256"]
        report[key] = {
            "title": TITLES[key], "description": DESCRIPTIONS[key], "version": "review-v2",
            "seconds": data["seconds"], "gameplaySeconds": data["gameplaySeconds"],
            "demoSeconds": data["demoSeconds"], "cuts": data["cuts"], "audio": data["audio"],
            "captioned": video_info(output / f"{key}-review-v2.mp4", data["seconds"], data["frames"]),
            "clean": video_info(output / f"{key}-clean-v2.mp4", data["seconds"], data["frames"]),
            "captions": {language: validate_subtitle(output / f"{key}.{language}.srt", data["seconds"])
                         for language in ("ko", "en")},
        }
        assert report[key]["captioned"]["sha256"] == data["sha256"]
        assert all(report[key]["captions"][lang]["sha256"] == data["subtitles"][lang] for lang in ("ko", "en"))
    return report


def source_index(markdown):
    rows = re.findall(r"^\| (\d+) \| (.*?) \| (.*?) \| \[(.*?)\]\((https?://[^)]+)\) \|$", markdown, re.M)
    assert [int(r[0]) for r in rows] == list(range(1, len(rows) + 1))
    assert len({r[-1] for r in rows}) == len(rows) >= 20
    return rows


def review_page(output, report, rows):
    cards = []
    for key, data in report.items():
        audio = data["audio"]["encoded"]
        cards.append(f"""<article>
<h2>{escape(data['title'])}</h2>
<video controls playsinline preload="metadata" src="{key}-review-v2.mp4" aria-label="{escape(data['title'])}"></video>
<p>{escape(data['description'])} <a href="{POLICY[key]}">개발 근거</a></p>
<p>길이 {data['seconds']:.2f}초 · 실제 플레이 {data['gameplaySeconds']:.3f}초 · 자체 시연 {data['demoSeconds']:.3f}초</p>
<p>최종 음량 {audio['integratedLUFS']:.2f} LUFS · 트루피크 {audio['truePeakDbTP']:.2f} dBTP</p>
<p class="links"><a href="{key}-review-v2.mp4">자막 영상</a> <a href="{key}-clean-v2.mp4">클린 영상</a> <a href="{key}.ko.srt">한국어 SRT</a> <a href="{key}.en.srt">영어 SRT</a></p>
</article>""")
    index = "".join(f'<li><span>{escape(kind)}</span> {escape(detail)} <a href="{url}">{escape(title)}</a></li>'
                    for _, kind, detail, title, url in rows)
    source_rights = (
        "촬영자가 Creative Commons Attribution으로 표시한 플레이 클립을 무음으로 사용했습니다. "
        "이 검수본에 쓰인 제3자 영상의 공개 편집 범위는 확인이 남아 있습니다."
    )
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>엘든 링 쇼츠 2편 검수</title><style>
body{{margin:auto;padding:18px;max-width:1020px;font:16px/1.65 'Malgun Gothic',system-ui,sans-serif;background:#10171b;color:#f8f4e8}}
h1,h2{{color:#ffd893;line-height:1.25}}a{{color:#8de9e1}}section.grid{{display:grid;gap:22px;grid-template-columns:repeat(auto-fit,minmax(min(100%,343px),1fr))}}
article,.notes{{background:#1b292e;border:1px solid #35555c;border-radius:12px;padding:16px}}
video{{display:block;width:min(100%,330px);margin:auto;border-radius:5px;background:black;aspect-ratio:9/16}}
.links a{{margin-right:9px}}li{{margin-bottom:8px}}li span{{color:#ffd893}}footer{{margin-block:28px}}
</style></head><body>
<header><h1>엘든 링 쇼츠 2편 검수</h1><p><a href="#sources">개발 자료 {len(rows)}개</a> · <a href="review-manifest-v2.json">영상 검증 및 파일 해시</a></p></header>
<main><section class="grid">{''.join(cards)}</section>
<section class="notes" aria-label="검수 정보">
<p>한국어 검수용 임시 내레이션을 사용했습니다.</p>
<p>{source_rights} <a href="{POLICY['publisher']}">배급사 영상 정책</a></p>
<p>두 편 모두 엘든 링 플레이 원음을 끄고 별도 배경 음악을 넣었습니다. <a href="{POLICY['developer']}">FromSoftware 음악 안내</a></p>
</section>
<section id="sources"><h2>엘든 링 개발 자료 {len(rows)}개</h2><ol>{index}</ol></section>
</main><footer>{CREDIT} · <a href="{POLICY['license']}">라이선스</a></footer></body></html>"""
    (output / "index.html").write_text(doc, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    rows = source_index(RESEARCH.read_text(encoding="utf-8"))
    report = verify(output)
    page_manifest = {"reviewScope": "local user review", "developmentSources": len(rows),
                     "encodedAudioVideoDecode": "pass", "visualCheck": "eight sampled frames per episode",
                     "humanReview": "pending", "publicationRights": "third-party footage scope pending",
                     "descriptionCredit": CREDIT, "videos": report}
    (output / "review-manifest-v2.json").write_text(json.dumps(page_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_page(output, report, rows)
    print(f"Verified {len(report)} videos, four output files each, and {len(rows)} development sources.")


if __name__ == "__main__":
    main()
