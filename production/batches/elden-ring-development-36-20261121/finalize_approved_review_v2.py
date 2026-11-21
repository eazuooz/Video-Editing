"""Verify, then expose the complete 36-episode approved-voice PC review."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import time
from urllib.parse import urlsplit

import build_pc_review as edit
from audit_pc_review import audit_file
from make_approved_voice_v2 import DEFAULT_OUTPUT, pinned_plan, read, save, sha
from review_approved_voice_v2 import compare


class ReviewLinks(HTMLParser):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.media = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag not in ("video", "a"):
            return
        address = attributes.get("src" if tag == "video" else "href", "")
        url = urlsplit(address)
        if not url.scheme and url.path and not (self.root / url.path).is_file():
            raise ValueError(f"Broken local review link: {url.path}")
        if tag == "video":
            self.media.append(url.path)


def sub_matches(path, takes, cuts):
    cues = []
    previous = 0
    for index, (line, cut) in enumerate(zip(takes, cuts, strict=True), 1):
        start, end = cut["subtitleFrames"]
        if not (previous <= start < end):
            raise ValueError(f"Subtitle timings overlap in {path.name}")
        previous = end
        cues.append(f"{index}\n{edit.code_time(start)} --> {edit.code_time(end)}\n{line}")
    if path.read_text(encoding="utf-8").strip() != "\n\n".join(cues):
        raise ValueError(f"Subtitle text/timing changed: {path}")


def missing(output, plan):
    return [ep["id"] for ep in plan if not
            (output / ep["id"] / "verification.json").is_file() or not
            (output / "voice-qa-mix" / f"{ep['id']}.json").is_file()]


def finalize(output, plan):
    generation_path = output / "voice-generation-v2.json"
    generation = read(generation_path)
    if len(generation["takes"]) != 144:
        raise ValueError("The approved voice proof needs 144 takes")
    durations, results, reuse_count = [], [], 0
    for episode in plan:
        number = episode["id"]
        folder = output / number
        report = read(folder / "verification.json")
        mixed = read(output / "voice-qa-mix" / f"{number}.json")
        if mixed["sha256"] != report["captioned"]["sha256"]:
            raise ValueError(f"Mixed audio proof changed for {number}")
        actual_score, differences = compare(mixed["expected"], mixed["recognized"])
        if actual_score < .88:
            raise ValueError(f"Mixed read-back for {number} needs checking: {differences}")
        cuts = report["cuts"]
        assert [cut["type"] for cut in cuts] == ["gameplay", "explanation"] * 2
        assert cuts[0]["frames"] == cuts[1]["frames"] and cuts[2]["frames"] == cuts[3]["frames"]
        source_scores, active_drops = [], []
        for index, cut in enumerate(cuts):
            key = f"{number}-{index}"
            proof = output / "voice-qa-source" / f"{key}.json"
            readback = read(proof)
            source = generation["takes"][key]
            assert cut["sourceVoiceProofSha256"] == sha(proof)
            assert cut["voiceSha256"] == source["sha256"] == readback["sha256"] == sha(output / "approved-voice" / source["file"])
            score, _ = compare(readback["expected"], readback["recognized"])
            source_scores.append(score)
            active_drops.append(readback["levels"]["speechHalfMedianChangeDb"])
        frames = sum(cut["frames"] for cut in cuts)
        packets_reused = sum(cut["picture"] == "prior-video-packets" for cut in cuts)
        reuse_count += packets_reused
        durations.append(frames / edit.FPS)
        for label in ("captioned", "clean"):
            artifact = folder / report[label]["path"]
            assert sha(artifact) == report[label]["sha256"]
            audit_file(artifact, frames)
        for language, script in (("ko", episode["narrationKo"]), ("en", episode["captionsEn"])):
            subs = folder / f"{language}.srt"
            assert sha(subs) == report["subtitles"][language]
            sub_matches(subs, script, cuts)
        assert -18 <= report["audio"]["integratedLUFS"] <= -15 and report["audio"]["truePeakDbTP"] < -1
        results.append({"id": number, "seconds": frames / edit.FPS, "gameplaySeconds": frames / (2 * edit.FPS),
                        "captioned": report["captioned"], "clean": report["clean"], "captions": report["subtitles"],
                        "mixedASRSha256": sha(output / "voice-qa-mix" / f"{number}.json"), "mixedASRSimilarity": actual_score,
                        "sourceASRSimilarities": source_scores, "speechHalfMedianChangesDb": active_drops,
                        "audio": report["audio"], "priorPictureCutsReused": packets_reused})
    edit.review_page(output, approved_voice=True)
    browser = ReviewLinks(output)
    browser.feed((output / "index.html").read_text(encoding="utf-8"))
    assert browser.media == [f"{ep['id']}/captioned.mp4" for ep in plan]
    result = {"reviewVersion": "approved-voice-v2", "count": len(results), "takes": 144, "reusedPictureCuts": reuse_count,
              "shortestSeconds": min(durations), "longestSeconds": max(durations), "totalSeconds": round(sum(durations), 3),
              "reviewPage": (output / "index.html").as_posix(), "reviewPageSha256": sha(output / "index.html"),
              "manifestSha256": sha(output / "manifest.json"), "voiceGenerationSha256": sha(generation_path),
              "humanReview": "pending", "results": results}
    save(output / "audit.json", result)
    print(f"Verified {len(results)} approved-voice videos; {reuse_count}/144 prior picture cuts were reused.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--watch-minutes", type=int, default=0)
    args = parser.parse_args()
    output = args.output.resolve()
    plan = pinned_plan()
    stop = time.monotonic() + args.watch_minutes * 60
    while remaining := missing(output, plan):
        if time.monotonic() >= stop:
            raise RuntimeError(f"The complete review is still waiting for {remaining}")
        time.sleep(15)
    finalize(output, plan)


if __name__ == "__main__":
    main()
