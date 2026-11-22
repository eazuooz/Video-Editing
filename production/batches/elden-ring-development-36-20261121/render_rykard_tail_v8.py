"""Append an observed ten-second Rykard gameplay excerpt to episode 08."""

from hashlib import sha256
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory

import psutil

import render_established_format_v6 as film


EPISODE = "08"
OUT = film.OUT.with_name("pc-review-v8")
PRIOR = film.OUT / EPISODE
SOURCE = film.OUT.with_name("pc-review-v1") / "sources" / "GQQZUGbeTDE.mp4"
SOURCE_SHA = "284680a204a1350722b64c569881876497cc396a4318561461e77b1ce1f25369"
SOURCE_START, SOURCE_END = 198, 208
FPS, SAMPLE_RATE = 60, 48_000
TAIL_FRAMES = (SOURCE_END - SOURCE_START) * FPS
LABEL = "라이커드 실제 전투"
PHASE = "검을 들어 올리고 몸을 틀어 휘두릅니다"
MUSIC_FADE_IN, MUSIC_FADE_OUT = 0.25, 0.75
MASTER_TRIM_DB = 0.10
RMS = film.edit.rms_measure


def audio_pcm(path, samples):
    return film.edit.run(
        "ffmpeg", "-v", "error", "-threads", 2, "-i", path,
        "-map", "0:a:0", "-af", f"atrim=end_sample={samples}",
        "-ar", SAMPLE_RATE, "-ac", 2, "-f", "f32le", "-",
    )


def append_music(record, start, work):
    music = record["music"]
    score = film.previous.WORK / music["file"]
    assert film.sha(score) == music["sha256"]
    offset = music["mixEvidence"]["startSeconds"] + start
    duration = SOURCE_END - SOURCE_START
    sample_count = duration * SAMPLE_RATE
    excerpt = work / "music-excerpt.wav"
    film.edit.ffmpeg("-ss", offset, "-i", score, "-t", duration,
                     "-ar", SAMPLE_RATE, "-ac", 2, "-c:a", "pcm_f32le", excerpt)
    target_level = music["mixEvidence"]["unduckedMusicLufs"]
    gain = target_level - RMS(excerpt)["integratedLUFS"]
    tail = work / "music-tail.wav"
    film.edit.ffmpeg(
        "-i", excerpt, "-af", f"volume={gain:.2f}dB,afade=d={MUSIC_FADE_IN},"
        f"afade=t=out:st={duration-MUSIC_FADE_OUT}:d={MUSIC_FADE_OUT}",
        "-c:a", "pcm_f32le", tail,
    )
    prefix = audio_pcm(PRIOR / "clean.mp4", start * SAMPLE_RATE)
    assert prefix == audio_pcm(PRIOR / "captioned.mp4", start * SAMPLE_RATE)
    extension = audio_pcm(tail, sample_count)
    assert len(prefix) == start * SAMPLE_RATE * 8
    assert len(extension) == sample_count * 8
    unencoded = work / "extended-mix.f32"
    with unencoded.open("wb") as out:
        out.write(prefix)
        out.write(extension)
    mix = work / "extended-mix.m4a"
    film.edit.ffmpeg("-f", "f32le", "-ar", SAMPLE_RATE, "-ac", 2, "-i", unencoded,
                     "-af", f"volume={MASTER_TRIM_DB}dB", "-c:a", "aac", "-b:a", "256k", "-threads", 2, mix)
    measurement = RMS(mix)
    assert -18 <= measurement["integratedLUFS"] <= -15, measurement
    assert measurement["truePeakDbTP"] < -1, measurement
    return mix, measurement, {
        "songOffsetSeconds": [offset, offset + duration],
        "musicGainDb": round(gain, 2),
        "fadeInSeconds": MUSIC_FADE_IN,
        "fadeOutSeconds": MUSIC_FADE_OUT,
        "masterTrimDb": MASTER_TRIM_DB,
        "tailLevel": RMS(tail),
        "priorDecodedPcmSha256BeforeReencoding": sha256(prefix).hexdigest(),
        "tailMusicPcmSha256BeforeReencoding": sha256(extension).hexdigest(),
        "audioReencodedAtKbps": 256,
        "mixFileSha256": film.sha(mix),
        "gameplayAudioMuted": True,
    }


def render_tail(work):
    painter = film.compositor(film.read(film.FORMAT), EPISODE)
    assert painter.label.getlength(PHASE) <= 900
    plate = work / "tail-layout.png"
    film.draw_base(painter, LABEL, plate, PHASE)
    body = film.rectangles((1920, 1080))
    x, y, width, height = body
    video = work / "tail-video.mp4"
    film.edit.ffmpeg(
        "-loop", 1, "-framerate", FPS, "-i", plate, "-ss", SOURCE_START,
        "-threads", 2, "-i", SOURCE,
        "-filter_complex_threads", 2, "-filter_complex",
        f"[1:v]fps={FPS},scale={width}:{height}:flags=lanczos,format=rgba,setsar=1[game];"
        f"[0:v][game]overlay={x}:{y}:shortest=1[out]",
        "-map", "[out]", "-an", "-frames:v", TAIL_FRAMES, "-c:v", "libx264",
        "-threads", 3, "-preset", "ultrafast", "-crf", 19, "-pix_fmt", "yuv420p", video,
    )
    stream, = film.edit.probe(video)["streams"]
    assert stream["codec_type"] == "video" and int(stream["nb_frames"]) == TAIL_FRAMES
    return video, body


def picture_hash(path, start_frame, frames):
    return film.edit.run(
        "ffmpeg", "-v", "error", "-threads", 2, "-ss", f"{start_frame/FPS:.8f}",
        "-i", path, "-map", "0:v:0", "-frames:v", frames, "-f", "hash", "-hash", "sha256", "-",
    ).decode().strip().split("=", 1)[1]


def render_master(flavor, prefix_frames, tail, mix, work, staged):
    previous = PRIOR / f"{flavor}.mp4"
    prefix_video = work / f"{flavor}-prefix-video.mp4"
    film.edit.ffmpeg("-i", previous, "-map", "0:v:0", "-c", "copy", prefix_video)
    listing = work / f"{flavor}.ffconcat"
    listing.write_text("ffconcat version 1.0\n" +
                       f"file '{prefix_video.as_posix()}'\n"
                       f"duration {prefix_frames/FPS:.8f}\n"
                       f"file '{tail.as_posix()}'\n",
                       encoding="utf-8")
    movie = staged / f"{flavor}.mp4"
    film.edit.ffmpeg("-f", "concat", "-safe", 0, "-i", listing, "-i", mix,
                     "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart", movie)
    result = film.edit.validate(movie, prefix_frames + TAIL_FRAMES)
    prior_packets, combined_packets = map(film.native.packet_fingerprints, (previous, movie))
    same_packets = combined_packets[:prefix_frames] == prior_packets
    assert len(prior_packets) == prefix_frames
    assert len(combined_packets) == prefix_frames + TAIL_FRAMES
    prefix_hash = picture_hash(movie, 0, prefix_frames)
    assert prefix_hash == picture_hash(previous, 0, prefix_frames)
    assert picture_hash(movie, prefix_frames, TAIL_FRAMES) == picture_hash(tail, 0, TAIL_FRAMES)
    samples = SAMPLE_RATE * (prefix_frames + TAIL_FRAMES)//FPS
    assert audio_pcm(movie, samples) == audio_pcm(mix, samples)
    return result, {"unchangedPrefixPackets": same_packets, "prefixDecodedVideoSha256": prefix_hash}


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    receipt = film.read(film.HERE / "review-receipt-v6.json")
    manifest = film.OUT / "manifest.json"
    assert film.sha(manifest) == receipt["manifestSha256"]
    record = film.read(PRIOR / "verification.json")
    assert record == film.read(manifest)["episodes"][int(EPISODE)-1]
    for flavor in ("clean", "captioned"):
        assert film.sha(PRIOR / f"{flavor}.mp4") == record[flavor]["sha256"]

    source_meta = SOURCE.with_suffix(".info.json")
    meta = film.read(source_meta)
    source_video = film.edit.probe(SOURCE)["streams"][0]
    assert film.sha(SOURCE) == SOURCE_SHA
    assert (source_video["width"], source_video["height"], source_video["avg_frame_rate"]) == (1920, 1080, "30/1")
    assert SOURCE_END <= float(source_video["duration"])
    assert meta["uploader"] == "Kruczx" and meta["webpage_url"] == record["cuts"][0]["url"]
    assert meta["license"] == "Creative Commons Attribution license (reuse allowed)"
    assert all(cut["end"] <= SOURCE_START for cut in record["cuts"] if cut["type"] == "gameplay")

    destination = OUT / EPISODE
    assert not destination.exists(), destination
    OUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".08-tail-", dir=OUT) as temporary:
        work = Path(temporary)
        staged = work / EPISODE
        staged.mkdir()
        prefix_frames = sum(cut["frames"] for cut in record["cuts"])
        assert prefix_frames % FPS == 0
        start_seconds = prefix_frames // FPS
        tail, body = render_tail(work)
        mix, levels, audio_review = append_music(record, start_seconds, work)
        visuals = {}
        for flavor in ("clean", "captioned"):
            record[flavor], visuals[flavor] = render_master(flavor, prefix_frames, tail, mix, work, staged)
        for language in ("ko", "en"):
            sidecar = staged / f"{language}.srt"
            copy2(PRIOR / sidecar.name, sidecar)
            assert film.sha(sidecar) == record["subtitles"][language]

        previous = record["cuts"][0]
        record["cuts"].append({
            "type": "gameplay", "role": "boss-movement-tail", "frames": TAIL_FRAMES,
            "recorder": meta["uploader"], "url": meta["webpage_url"], "rights": previous["rights"],
            "sha256": SOURCE_SHA, "size": [1920, 1080], "start": SOURCE_START, "end": SOURCE_END,
            "observed": "라이커드가 검을 들어 올리고 몸을 틀어 휘두르는 실제 전투", "picture": "rykard-tail-v8",
        })
        record["formatSources"].append({
            "source": str(SOURCE), "sourceSha256": SOURCE_SHA, "sourceStart": SOURCE_START,
            "sourceEnd": SOURCE_END, "sourceSpeed": 1, "bodyRect": list(body),
            "originalAspectPreserved": True, "reaction": None, "phaseStarts": [],
            "originalTemplate": record["formatSources"][0]["originalTemplate"],
        })
        record["music"]["tailMixEvidence"] = audio_review
        record.update(
            revisionId="rykard-tail-v8-" + film.sha(Path(__file__)),
            seconds=(prefix_frames+TAIL_FRAMES)/FPS,
            gameplaySeconds=record["gameplaySeconds"] + TAIL_FRAMES/FPS,
            audio=levels,
            previousAudioTrackPreserved=False,
            tailVerification={
                "sourceMetadata": str(source_meta), "sourceMetadataSha256": film.sha(source_meta),
                "movieFrames": [prefix_frames, prefix_frames+TAIL_FRAMES],
                "rawGameplaySeconds": [SOURCE_START, SOURCE_END], "originalSpeed": True,
                "firstFourSegments": visuals, "bothTailPicturesShared": True,
                "tailDecodedVideoSha256": picture_hash(tail, 0, TAIL_FRAMES),
                "gameplayOriginalAudio": False, "captionSidecarsUnchanged": True,
            },
        )
        film.save(staged / "verification.json", record)
        staged.rename(destination)
    print(f"{EPISODE}: {record['seconds']}s, {record['gameplaySeconds']}s gameplay, {levels}, {destination}")


if __name__ == "__main__":
    main()
