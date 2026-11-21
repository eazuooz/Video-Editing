import argparse
import json
from pathlib import Path
import re

from build_pc_review import FPS, PLAN, code_time, probe, review_page, reviews, run, sha


def audit_file(path, expected_frames):
    streams = probe(path)["streams"]
    assert [s["codec_type"] for s in streams] == ["video", "audio"], path
    video, audio = streams
    assert (video["width"], video["height"], video["avg_frame_rate"]) == (1080, 1920, "60/1"), path
    assert abs(float(audio["duration"]) - expected_frames / FPS) < .03, path
    numerator, denominator = map(int, video["time_base"].split("/"))
    packets = json.loads(run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
                             "-show_entries", "packet=pts", "-of", "json", path))["packets"]
    pts = sorted(p["pts"] for p in packets)
    assert len(pts) == expected_frames, path
    assert all(position * numerator * FPS == frame * denominator for frame, position in enumerate(pts)), path


def audit_captions(folder, takes, cuts):
    start = 0
    result = []
    for index, (line, cut) in enumerate(zip(takes, cuts, strict=True), 1):
        end = start + cut["frames"]
        result.append(f"{index}\n{code_time(start)} --> {code_time(end)}\n{line}")
        start = end
    return "\n\n".join(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    review_page(root)
    overview = []
    for episode, data in zip(PLAN, reviews(root), strict=True):
        report = data["review"]
        if not report:
            continue
        folder = root / episode["id"]
        cuts = report["cuts"]
        frames = sum(cut["frames"] for cut in cuts)
        for label in ("captioned", "clean"):
            audit_file(folder / report[label]["path"], frames)
        for lang, planned in (("ko", episode["narrationKo"]), ("en", episode["captionsEn"])):
            path = folder / f"{lang}.srt"
            assert path.read_text(encoding="utf-8").strip() == audit_captions(folder, planned, cuts), path
        assert [c["type"] for c in cuts[1::2]] == ["explanation"] * 2
        assert -18 <= report["audio"]["integratedLUFS"] <= -15
        assert report["audio"]["truePeakDbTP"] < -1
        overview.append({"id": episode["id"], "durationSeconds": frames / FPS, "unfilledClips": report["missing"],
                         "files": {f"{label}.mp4": report[label]["sha256"] for label in ("captioned", "clean")},
                         "captions": report["subtitles"], "audio": report["audio"]})
        print(f"{episode['id']} video PTS, audio duration and both SRTs verified.", flush=True)
    ready = sum(not item["unfilledClips"] for item in overview)
    manifest = root / "manifest.json"
    page = root / "index.html"
    page_text = page.read_text(encoding="utf-8")
    assert re.findall('id="ep([0-9]{2})"', page_text) == [episode["id"] for episode in PLAN]
    assert len(re.findall("<video ", page_text)) == len(overview)
    result = {"reviewedFiles": len(overview), "withMatchedGameplay": ready, "totalPlanned": len(PLAN),
              "humanReview": "pending", "reviewPage": str(page), "reviewPageSha256": sha(page),
              "reviewManifest": str(manifest), "reviewManifestSha256": sha(manifest),
              "technicalChecks": ["full audio and video decode at render", "60 fps PTS",
                                  "exact paired gameplay and explanation duration where all clips are present",
                                  "Korean and English SRTs", "integrated loudness and true peak"],
              "results": overview}
    (root / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Verified {len(overview)} playable review files; {ready} include every required screen slot.")


if __name__ == "__main__":
    main()
