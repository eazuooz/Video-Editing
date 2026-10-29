"""Normalize one retained source record without changing its media or decision."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def main():
    path = HERE / "sources.json"
    original = path.read_bytes()
    data = json.loads(original)
    before = copy.deepcopy(data)
    rows = {row["id"]: row for row in data["sources"]}
    row = rows["unpacking-launch"]
    if isinstance(row.get("audio"), dict):
        raise SystemExit("Already normalized; no rewrite performed")
    media = ROOT / row["file"]
    actual_sha = hashlib.sha256(media.read_bytes()).hexdigest()
    assert actual_sha == row["sha256"]
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
        "-of", "json", str(media)
    ], text=True))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (video["width"], video["height"], video["r_frame_rate"]) == (1920, 1080, "30/1")
    decisions = json.loads((HERE / "audio-source-review.json").read_text(encoding="utf-8"))
    decision = copy.deepcopy(next(s for s in decisions["sources"] if s["id"] == row["id"]))
    assert decision["sourceSha256"] == actual_sha
    decision.pop("id")
    decision.pop("sourceFile")
    decision["previousProseRecord"] = row["audio"]
    decision["stream"] = audio
    row["classification"] = "independent-gameplay"
    row["referenceLesson"] = False
    row["nativeFhd"] = True
    row["decoded"] = {
        "width": video["width"], "height": video["height"],
        "fps": video["r_frame_rate"], "duration": float(probe["format"]["duration"]),
        "aspect": "16:9", "codec": video["codec_name"]
    }
    row["audio"] = decision
    for retained in data["sources"]:
        assert retained["classification"] == "independent-gameplay"
        assert retained["referenceLesson"] is False
        assert retained["nativeFhd"] is True
        assert isinstance(retained["audio"]["sourceAudioEnabled"], bool)
    assert [s for s in before["sources"] if s["id"] != row["id"]] == [s for s in data["sources"] if s["id"] != row["id"]]
    assert path.read_bytes() == original, "Concurrent source change; abort"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "normalized-one-retained-record", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "sourceCount": len(data["sources"]), "decoded": row["decoded"]}))


if __name__ == "__main__":
    main()
