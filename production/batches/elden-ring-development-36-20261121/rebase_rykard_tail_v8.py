"""Reuse the verified Rykard tail and score with a verified 44-second episode 08 edit."""

from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory

import psutil

import render_rykard_tail_v8 as tail


film = tail.film
FALLBACK = tail.OUT / tail.EPISODE


def append_verified_tail(body: Path, destination: Path) -> dict:
    """Join the existing outputs on the established frame and sample boundaries."""
    body, destination = body.resolve(), destination.resolve()
    assert not destination.exists(), destination
    base = film.read(body / "verification.json")
    rendered = film.read(FALLBACK / "verification.json")
    prefix_frames, total_frames = rendered["tailVerification"]["movieFrames"]
    assert len(base["cuts"]) == 4
    assert sum(cut["frames"] for cut in base["cuts"]) == prefix_frames
    assert base["seconds"] == prefix_frames / tail.FPS
    assert base["gameplaySeconds"] == 22 and base["explanationSeconds"] == 22
    assert len(base["formatSources"]) == 4
    samples = tail.SAMPLE_RATE * prefix_frames // tail.FPS
    audio_hash = rendered["music"]["tailMixEvidence"]["priorDecodedPcmSha256BeforeReencoding"]
    for flavor in ("clean", "captioned"):
        prior = body / base[flavor]["path"]
        assert film.sha(prior) == base[flavor]["sha256"]
        assert sha256(tail.audio_pcm(prior, samples)).hexdigest() == audio_hash
    fallback_master = FALLBACK / rendered["clean"]["path"]
    assert film.sha(fallback_master) == rendered["clean"]["sha256"]

    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".08-rebase-", dir=destination.parent) as temporary:
        work = Path(temporary)
        staged = work / "result"
        staged.mkdir()
        tail_picture = work / "tail-video.mp4"
        film.edit.ffmpeg("-ss", prefix_frames/tail.FPS, "-i", fallback_master,
                         "-map", "0:v:0", "-c:v", "copy", "-an", "-frames:v", total_frames-prefix_frames,
                         tail_picture)
        tail_hash = tail.picture_hash(tail_picture, 0, total_frames-prefix_frames)
        assert tail_hash == rendered["tailVerification"]["tailDecodedVideoSha256"]

        record = deepcopy(base)
        visual_proof = {}
        for flavor in ("clean", "captioned"):
            prior = body / base[flavor]["path"]
            prefix_video = work / f"{flavor}-prefix-video.mp4"
            film.edit.ffmpeg("-i", prior, "-map", "0:v:0", "-c", "copy", prefix_video)
            listing = work / f"{flavor}.ffconcat"
            listing.write_text("ffconcat version 1.0\n"
                               f"file '{prefix_video.as_posix()}'\n"
                               f"duration {prefix_frames/tail.FPS:.8f}\n"
                               f"file '{tail_picture.as_posix()}'\n", encoding="utf-8")
            movie = staged / f"{flavor}.mp4"
            film.edit.ffmpeg("-f", "concat", "-safe", 0, "-i", listing, "-i", fallback_master,
                             "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart", movie)
            record[flavor] = film.edit.validate(movie, total_frames)
            assert film.native.track_sha(movie, "a") == film.native.track_sha(fallback_master, "a")
            source_packets = film.native.packet_fingerprints(prior)
            result_packets = film.native.packet_fingerprints(movie)
            same_packets = result_packets[:prefix_frames] == source_packets
            prefix_hash = tail.picture_hash(movie, 0, prefix_frames)
            assert prefix_hash == tail.picture_hash(prior, 0, prefix_frames)
            assert tail.picture_hash(movie, prefix_frames, total_frames-prefix_frames) == tail_hash
            visual_proof[flavor] = {"unchangedPrefixPackets": same_packets, "prefixDecodedVideoSha256": prefix_hash}
        for language in ("ko", "en"):
            name = f"{language}.srt"
            copy2(body / name, staged / name)
            assert film.sha(staged / name) == base["subtitles"][language]

        record["cuts"].append(rendered["cuts"][-1])
        record["formatSources"].append(rendered["formatSources"][-1])
        record.update(
            revisionId="rykard-tail-rebased-v8-" + film.sha(Path(__file__)),
            seconds=rendered["seconds"], gameplaySeconds=rendered["gameplaySeconds"],
            music=rendered["music"], audio=rendered["audio"], previousAudioTrackPreserved=False,
            tailVerification=rendered["tailVerification"] | {
                "firstFourSegments": visual_proof,
                "baseReviewSha256": film.sha(body / "verification.json"),
                "fallbackReviewSha256": film.sha(FALLBACK / "verification.json"),
                "fallbackAudioTrackPreserved": True,
            },
        )
        film.save(staged / "verification.json", record)
        staged.rename(destination)
    return record


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("body", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    result = append_verified_tail(args.body, args.destination)
    print(f"08: {result['seconds']}s · {args.destination}")
