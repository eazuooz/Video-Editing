"""Audit retained pixels/closed-GOP bitstreams without decoding or encoding.

Run --prepare-baseline while the replacement pair is still being encoded.
Run --compare only after root confirms the new pair AND pixel extraction ready.
--self-test exercises the frame/GOP comparison with synthetic B-frame packets.
Only metadata caches and a QA report are written; masters are never modified.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right, bisect_left
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/game-math-euler-axis-angle"
LOCAL = PROJECT / "production/local/revision-v2"
OLD = LOCAL / "before-axis-label-repair"
CACHE = LOCAL / "retained-audit-cache"
TIMELINE = Path(__file__).with_name("timeline.json")
FLAT_IDS = {"01", "13", "15", "24", "25", "26"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".partial")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def probe(arguments, path):
    return json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", *arguments,
         "-of", "json", str(path)], text=True, encoding="utf-8"))


def extradata_bytes(dump):
    # ffprobe's 16-byte hex column occupies39 characters after the offset.
    return bytes.fromhex("".join(line[10:49].replace(" ", "")
                                   for line in dump.splitlines() if ": " in line))


def nal_types(payload, length_size):
    offset, result = 0, []
    while offset < len(payload):
        if offset + length_size > len(payload):
            raise ValueError("Truncated AVC NAL length")
        count = int.from_bytes(payload[offset:offset + length_size], "big")
        offset += length_size
        if count <= 0 or offset + count > len(payload):
            raise ValueError("Invalid AVC packet NAL length")
        result.append(payload[offset] & 31)
        offset += count
    return result


def packet_frame(value, time_base):
    result = int(value) * Fraction(time_base) * 60
    if result.denominator != 1:
        raise ValueError("Packet timestamp is not on the measured60fps grid")
    return int(result)


def closed_gop_evidence(packets, keys, total_frames):
    if not keys or keys[0]["frame"] != 0:
        raise ValueError("Missing opening IDR")
    intervals = []
    for i, key in enumerate(keys):
        end_index = keys[i + 1]["packetIndex"] if i + 1 < len(keys) else len(packets)
        end_frame = keys[i + 1]["frame"] if i + 1 < len(keys) else total_frames
        frames = [p["frame"] for p in packets[key["packetIndex"]:end_index]]
        complete = len(frames) == end_frame - key["frame"] and sorted(frames) == list(range(key["frame"], end_frame))
        intervals.append({"startFrame": key["frame"], "endFrame": end_frame,
                          "startPacketIndex": key["packetIndex"], "endPacketIndex": end_index,
                          "startsWithIDR": key["hasIDR"], "noLeadingOrMissingPresentationFrames": complete})
    return intervals


def metadata_cache(directory, name):
    """One cached packet scan plus direct IDR-byte inspection; never decode."""
    directory = Path(directory)
    pair_file = directory / "pair-source.json"
    pair = read(pair_file)
    path = directory / "euler-captioned.mp4"
    expected = pair["outputs"]["captioned"]["sha256"]
    st = path.stat()
    signature = {"file": rel(path), "expectedSha256": expected,
                 "bytes": st.st_size, "mtimeNs": st.st_mtime_ns,
                 "pairReceiptSha256": sha(pair_file)}
    cache = CACHE / (name + "-video-packets.json")
    cached = read(cache) if cache.exists() else None
    if cached is not None and cached.get("signature") == signature:
        return cached, True
    actual_hash = sha(path)
    if actual_hash != expected:
        raise ValueError("Captioned master does not match its completed pair receipt")
    stream = probe(["-show_streams", "-show_data", "-show_entries",
                    "stream=codec_name,profile,level,width,height,pix_fmt,r_frame_rate,time_base,nb_frames,has_b_frames,color_range,color_space,color_primaries,color_transfer,extradata,extradata_size"], path)["streams"][0]
    if (stream["codec_name"], stream["width"], stream["height"], stream["r_frame_rate"]) != ("h264", 1920, 1080, "60/1"):
        raise ValueError("Expected native FHD60 H264 master")
    data = extradata_bytes(stream["extradata"])
    if len(data) != stream["extradata_size"] or not data or data[0] != 1:
        raise ValueError("Invalid avcC extradata")
    length_size = (data[4] & 3) + 1
    raw = probe(["-show_packets", "-show_data_hash", "sha256", "-show_entries",
                 "packet=pts,dts,duration,size,pos,flags,data_hash"], path)["packets"]
    packets, keys = [], []
    with path.open("rb") as handle:
        for i, packet in enumerate(raw):
            row = {"pts": int(packet["pts"]), "dts": int(packet["dts"]),
                   "duration": int(packet["duration"]), "bytes": int(packet["size"]),
                   "frame": packet_frame(packet["pts"], stream["time_base"]),
                   "dtsFrame": packet_frame(packet["dts"], stream["time_base"]),
                   "payloadSha256": packet["data_hash"].removeprefix("SHA256:"),
                   "key": "K" in packet["flags"]}
            if len(row["payloadSha256"]) != 64:
                raise ValueError("ffprobe did not supply the packet payload SHA256")
            packets.append(row)
            if row["key"]:
                handle.seek(int(packet["pos"]))
                payload = handle.read(row["bytes"])
                if hashlib.sha256(payload).hexdigest() != row["payloadSha256"]:
                    raise ValueError("Direct key-packet bytes differ from ffprobe payload hash")
                types = nal_types(payload, length_size)
                keys.append({"packetIndex": i, "frame": row["frame"],
                             "nalUnitTypes": types, "hasIDR": 5 in types})
    count = int(stream["nb_frames"])
    if len(packets) != count or sorted(p["frame"] for p in packets) != list(range(count)):
        raise ValueError("Packet PTS does not cover every frame exactly once")
    if any(a["dts"] >= b["dts"] for a, b in zip(packets, packets[1:])):
        raise ValueError("Non-monotonic video DTS")
    gops = closed_gop_evidence(packets, keys, count)
    after = path.stat()
    if (st.st_size, st.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Master changed during packet audit")
    result = {"schemaVersion": 1, "signature": signature, "actualFileSha256": actual_hash,
              "method": "ffprobe metadata/payload hashing and direct sync-packet NAL reads; no decoding",
              "stream": {k: v for k, v in stream.items() if k not in ("extradata", "disposition", "tags")},
              "extradataHex": data.hex(), "extradataSha256": hashlib.sha256(data).hexdigest(),
              "avcNalLengthBytes": length_size, "packets": packets, "keys": keys, "gops": gops,
              "allSyncPacketsAreIDR": all(k["hasIDR"] for k in keys),
              "allGopsHaveNoLeadingOrMissingPresentationFrames": all(g["noLeadingOrMissingPresentationFrames"] for g in gops)}
    save(cache, result)
    return result, False


def dependency_window(meta, start, end):
    keys = [k["frame"] for k in meta["keys"]]
    left_index = bisect_right(keys, start) - 1
    right_index = bisect_left(keys, end)
    if left_index < 0:
        raise ValueError("No preceding IDR for target")
    total = int(meta["stream"]["nb_frames"])
    left = meta["keys"][left_index]
    right = meta["keys"][right_index] if right_index < len(keys) else None
    finish = right["frame"] if right else total
    packet_end = right["packetIndex"] if right else len(meta["packets"])
    gops = [g for g in meta["gops"] if left["frame"] <= g["startFrame"] < finish]
    closed = bool(gops) and all(g["startsWithIDR"] and g["noLeadingOrMissingPresentationFrames"] for g in gops)
    return {"frames": [left["frame"], finish], "packets": [left["packetIndex"], packet_end],
            "closedIDRDependencyWindow": closed}


def compare_target(old, new, start, end):
    a, b = dependency_window(old, start, end), dependency_window(new, start, end)
    reasons = []
    if old["extradataHex"] != new["extradataHex"]:
        reasons.append("SPS/PPS avcC bytes changed")
    fields = ("codec_name", "profile", "level", "width", "height", "pix_fmt", "r_frame_rate", "time_base", "has_b_frames", "color_range", "color_space", "color_primaries", "color_transfer")
    if any(old["stream"].get(k) != new["stream"].get(k) for k in fields):
        reasons.append("Relevant stream decoding/display metadata changed")
    if a["frames"] != b["frames"]:
        reasons.append("Previous/next IDR dependency windows differ")
    if not a["closedIDRDependencyWindow"] or not b["closedIDRDependencyWindow"]:
        reasons.append("Dependency window is not proven closed by IDR and presentation coverage")
    op = old["packets"][slice(*a["packets"])]
    np = new["packets"][slice(*b["packets"])]
    identical = len(op) == len(np) and all(x == y for x, y in zip(op, np))
    if not identical:
        reasons.append("Packet PTS/DTS/duration/payload differs inside the dependency window")
    new_by_frame = {p["frame"]: p for p in np}
    changed_frames = [p["frame"] for p in op if p != new_by_frame.get(p["frame"])]
    return {"targetFrames": [start, end], "oldDependencyWindow": a,
            "newDependencyWindow": b, "sameExtradata": old["extradataHex"] == new["extradataHex"],
            "dependencyPacketRowsIdentical": identical,
            "differentDependencyPacketFrames": sorted(changed_frames),
            "targetPacketDifferenceCount": sum(start <= frame < end for frame in changed_frames),
            "reuseWholeMovingTarget": not reasons, "failureReasons": reasons,
            "neededMovingReviewFrames": [] if not reasons else [start, end],
            "proofKind": "closed-IDR H264 bitstream/PTS equivalence, not an executed decoded-frame comparison"}


def pixel_comparison(old_dir, new_dir, expected_old, expected_new):
    old_qa, new_qa = Path(old_dir) / "qa", Path(new_dir) / "qa"
    old_receipt, new_receipt = read(old_qa / "pixel-extraction.json"), read(new_qa / "pixel-extraction.json")
    old_index, new_index = read(old_qa / "pixel-sample-index.json"), read(new_qa / "pixel-sample-index.json")
    if old_receipt["inputs"]["videoSha256"] != expected_old or new_receipt["inputs"]["videoSha256"] != expected_new:
        raise ValueError("Pixel extraction does not belong to the completed masters")
    same_index = old_index == new_index
    same_extractor = old_receipt["inputs"]["extractorSha256"] == new_receipt["inputs"]["extractorSha256"]
    rows = []
    for i, row in enumerate(old_index, 1):
        old_path, new_path = old_qa / f"frame-{i:04}.jpg", new_qa / f"frame-{i:04}.jpg"
        old_hash = sha(old_path)
        new_hash = sha(new_path) if new_path.exists() else None
        identical = old_hash == new_hash
        rows.append({"sampleIndexOneBased": i, **row,
                     "oldFile": rel(old_path), "newFile": rel(new_path),
                     "oldSha256": old_hash, "newSha256": new_hash,
                     "artifactBytesIdentical": identical,
                     "reusePriorStaticSampleReview": same_index and same_extractor and identical})
    return {"oldSamples": len(old_index), "newSamples": len(new_index),
            "sameFrameAndLabelIndex": same_index, "sameExtractor": same_extractor,
            "byteIdenticalSampleCount": sum(r["artifactBytesIdentical"] for r in rows),
            "reusableStaticSampleCount": sum(r["reusePriorStaticSampleReview"] for r in rows),
            "limit": "JPEG-byte identity proves the inspected artifact is unchanged; lossy JPEG equality alone does not prove full native YUV or whole-scene motion equivalence.",
            "rows": rows}


def compare(old_dir, new_dir, report_file):
    old_pair, new_pair = read(Path(old_dir) / "pair-source.json"), read(Path(new_dir) / "pair-source.json")
    old_hash = old_pair["outputs"]["captioned"]["sha256"]
    new_hash = new_pair["outputs"]["captioned"]["sha256"]
    # Fail before opening a possibly partial current MP4 if receipt is still old.
    if new_hash == old_hash:
        raise ValueError("Replacement pair receipt is not finalized; do not read the active master")
    timeline = read(TIMELINE)
    if old_pair["inputs"]["timelineSha256"] != new_pair["inputs"]["timelineSha256"] or sha(TIMELINE) != new_pair["inputs"]["timelineSha256"]:
        raise ValueError("Timeline changed; retained-time reuse requires a separate mapping")
    pixels = pixel_comparison(old_dir, new_dir, old_hash, new_hash)
    old, old_reused = metadata_cache(old_dir, "baseline")
    new, new_reused = metadata_cache(new_dir, "replacement")
    if any(int(meta["stream"]["nb_frames"]) != timeline["totalFrames"] for meta in (old, new)):
        raise ValueError("Master packet/frame count differs from the fixed timeline")
    scenes = []
    for scene in timeline["scenes"]:
        if scene["kind"] != "actual" and scene["id"] not in FLAT_IDS:
            continue
        entry = compare_target(old, new, scene["startFrame"], scene["endFrame"])
        samples = [r for r in pixels["rows"] if scene["startFrame"] <= r["frame"] < scene["endFrame"]]
        entry.update(scene=scene["id"], kind=scene["kind"],
                     priorScopeNote="Reuse is limited to previously reviewed matching content; it never upgrades pending human listening or previously unreviewed movement.",
                     staticSamples=len(samples), reusableStaticSamples=sum(r["reusePriorStaticSampleReview"] for r in samples))
        scenes.append(entry)
    if len(scenes) != 14:
        raise ValueError("Expected exactly8 actual and6 Manim target scenes")
    report = {"schemaVersion": 1, "createdAt": datetime.now(timezone.utc).isoformat(),
              "status": "retained-output-equivalence-audit-complete",
              "oldCaptionedSha256": old_hash, "newCaptionedSha256": new_hash,
              "timelineSha256": sha(TIMELINE),
              "baselinePacketCache": rel(CACHE / "baseline-video-packets.json"),
              "replacementPacketCache": rel(CACHE / "replacement-video-packets.json"),
              "packetCacheReused": {"baseline": old_reused, "replacement": new_reused},
              "method": "ffprobe packet metadata/hash + IDR NAL inspection + existing JPEG file hashes; no decoding/rendering/ASR",
              "pixelArtifacts": pixels, "retainedSceneTargets": scenes,
              "summary": {"targetScenes": len(scenes), "movingTargetsReusableByBitstreamIdentity": sum(s["reuseWholeMovingTarget"] for s in scenes),
                          "movingReviewScenes": [s["scene"] for s in scenes if not s["reuseWholeMovingTarget"]],
                          "reusableStaticSamples": pixels["reusableStaticSampleCount"]},
              "humanWholeListening": "pending; unchanged by this audit",
              "newWholeOutputIntegrity": "root verifier evidence required; not substituted by equivalence",
              "mediaFilesWritten": False, "newPixelExtraction": False, "ASRRun": False}
    save(report_file, report)
    print(json.dumps({"report": rel(report_file), "sha256": sha(report_file), **report["summary"]}, ensure_ascii=False))


def self_test():
    def fake():
        order = [0, 3, 1, 2, 4, 7, 5, 6]
        packets = [{"pts": f * 1000, "dts": (i - 2) * 1000, "duration": 1000,
                    "bytes": 12, "frame": f, "dtsFrame": i - 2,
                    "payloadSha256": str(f) * 64, "key": f in (0, 4)} for i, f in enumerate(order)]
        keys = [{"frame": f, "packetIndex": order.index(f), "hasIDR": True} for f in (0, 4)]
        return {"stream": {"nb_frames": "8"}, "extradataHex": "same", "packets": packets,
                "keys": keys, "gops": closed_gop_evidence(packets, keys, 8)}
    a, b = fake(), fake()
    assert compare_target(a, b, 1, 3)["reuseWholeMovingTarget"]
    # A changed preceding reference outside target must still reject reuse.
    b["packets"][0]["payloadSha256"] = "changed"
    result = compare_target(a, b, 1, 3)
    assert not result["reuseWholeMovingTarget"] and result["targetPacketDifferenceCount"] == 0
    b = fake(); b["packets"][2]["payloadSha256"] = "changed"
    assert compare_target(a, b, 1, 3)["targetPacketDifferenceCount"] == 1
    b = fake(); b["extradataHex"] = "different"
    assert not compare_target(a, b, 1, 3)["reuseWholeMovingTarget"]
    b = fake(); b["gops"][0]["noLeadingOrMissingPresentationFrames"] = False
    assert not compare_target(a, b, 1, 3)["reuseWholeMovingTarget"]
    assert dependency_window(a, 4, 8)["frames"] == [4, 8]
    assert nal_types(b"\x00\x00\x00\x01\x65", 4) == [5]
    assert packet_frame(1000, "1/60000") == 1
    print(json.dumps({"selfTest": "passed", "cases": 8, "mediaRead": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-baseline", action="store_true")
    modes.add_argument("--compare", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--old-dir", type=Path, default=OLD)
    parser.add_argument("--new-dir", type=Path, default=LOCAL)
    parser.add_argument("--report", type=Path, default=LOCAL / "qa/retained-output-equivalence.json")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.prepare_baseline:
        result, reused = metadata_cache(args.old_dir, "baseline")
        print(json.dumps({"baselineCache": rel(CACHE / "baseline-video-packets.json"),
                          "reused": reused, "sourceSha256": result["actualFileSha256"],
                          "packets": len(result["packets"]), "IDRs": len(result["keys"]),
                          "closedGopEvidence": result["allSyncPacketsAreIDR"] and result["allGopsHaveNoLeadingOrMissingPresentationFrames"],
                          "newMasterRead": False}))
    else:
        compare(args.old_dir, args.new_dir, args.report)
