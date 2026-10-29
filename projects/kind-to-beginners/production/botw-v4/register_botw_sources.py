"""Register inspected local source pool; never download or alter source media."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
PRODUCTION = Path(__file__).resolve().parent
RESEARCH = ROOT / "projects/kind-to-beginners/production/local/botw-v4/research"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    inventory = json.loads((RESEARCH / "candidate-inventory.json").read_text(encoding="utf-8"))
    for name in ("sources.json", "audio-source-review.json"):
        if (PRODUCTION / name).exists():
            raise FileExistsError("Preserve existing " + name)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    source_doc = json.loads((PRODUCTION.parent / "clarity-v3/sources.json").read_text(encoding="utf-8"))
    audio_doc = json.loads((PRODUCTION.parent / "clarity-v3/audio-source-review.json").read_text(encoding="utf-8"))
    source_doc["revision"] = audio_doc["revision"] = "botw-v4"
    source_doc["updatedAt"] = audio_doc["reviewedAt"] = now
    source_doc["sources"] = [x for x in source_doc["sources"] if x["id"] != "mk8"]
    audio_doc["sources"] = [x for x in audio_doc["sources"] if x["id"] != "mk8"]
    source_doc["footageResearch"] = inventory["newMediaBase"] + "candidate-inventory.json"
    audio_doc["state"] = "source-selection-reviewed-final-mix-pending"
    audio_doc["earOrHumanListeningPerformed"] = False
    audio_doc["priorRevisionApplicationEvidence"] = audio_doc.pop("applicationEvidence", None)
    audio_doc["applicationEvidence"] = {"status": "pending-new-botw-v4-mix"}
    for entry in source_doc["sources"]:
        entry["reusedFrom"] = "clarity-v3; source-specific rights decision retained"
        audio = entry.get("audio")
        if isinstance(audio, dict):
            audio["priorRevisionApplicationEvidence"] = audio.pop("applicationEvidence", None)
            audio["decisionStatus"] = "retained-source-decision-botw-v4-mix-pending"
    for entry in audio_doc["sources"]:
        entry["priorRevisionApplicationEvidence"] = entry.pop("applicationEvidence", None)
        entry["decisionStatus"] = "retained-source-decision-botw-v4-mix-pending"
    verified = []
    for entry in inventory["sources"]:
        base = inventory["sourceBase"] if entry["existing"] else inventory["newMediaBase"]
        file = base + entry["filename"]
        path = ROOT / file
        if sha(path) != entry["sha256"]:
            raise ValueError("Source changed: " + file)
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration,size",
            "-of", "json", str(path)], text=True))
        video = next(x for x in probe["streams"] if x["codec_type"] == "video")
        stream = next(x for x in probe["streams"] if x["codec_type"] == "audio")
        if (video["width"], video["height"], video["r_frame_rate"]) != (1920, 1080, "60/1"):
            raise ValueError("Unexpected source format")
        audio = {
            "originalPreserved": True, "streamPresentVerified": True,
            "nativeStereoStream": stream.get("channels") == 2,
            "decision": "retain", "sourceAudioEnabled": True,
            "decisionStatus": "source-specific-selection-reviewed-final-mix-pending",
            "reason": "Recorder permits monetized edited gameplay. Preserve the synchronized ordinary Nintendo game mix under publisher commentary guidance; no standalone soundtrack. No inserted external music identified in metadata/visuals. Actual ear listening not performed.",
            "policyOrPrimaryUrl": "https://www.nintendo.co.jp/networkservice_guideline/en/index.html",
            "recorderPermissionUrl": "https://www.nintblkc.com/archive-64",
            "actualListeningPerformed": False, "sourceSha256": entry["sha256"], "stream": stream,
        }
        source = {
            "id": entry["id"], "classification": "independent-gameplay", "referenceLesson": False,
            "file": file, "sha256": entry["sha256"],
            "url": "https://www.youtube.com/watch?v=" + ("tOvTBrO7bPo" if entry["part"] == 1 else "kjSH8R2fk2c"),
            "creator": "Archive 64 / NintendoBlackCrisis", "originalOffsetSeconds": entry["requestedStart"],
            "requestedSourceWindowSeconds": [entry["requestedStart"], entry["requestedEnd"]],
            "originTimingPrecision": "Stream-copy sections; use inspected local seconds for editing, requested source origin approximate within keyframe trim tolerance.",
            "decoded": {"width": 1920, "height": 1080, "fps": "60/1", "duration": float(probe["format"]["duration"]), "aspect": "16:9", "codec": video["codec_name"]},
            "nativeFhd": True,
            "recordingEnvironment": "Uploader states CEMU, internal2K60 upscaled4K. Original2991080p60+140AAC downloaded; not Switch hardware/performance evidence.",
            "inspected": "Fresh decoded sample/contact review, dense menu transitions. No whole watching or ear listening claim.",
            "permissionBasis": "Recorder expressly permits monetized/nonmonetized edited reuse; credit optional. Publisher guidance separately recorded. Not a CC license.",
            "rightsRecord": inventory["newMediaBase"] + "rights-review.json", "audio": audio,
            "creditDestination": "absolute bottom of description only; original UI preserved",
            "usableLocalRanges": [{"start": a, "end": b, "observed": c} for a, b, c in entry["ranges"]],
            "visualProof": inventory["newMediaBase"] + entry["proof"],
            "visualProofSha256": sha(RESEARCH / entry["proof"]),
            "limits": ["Field thermometer hidden by Pro HUD; menu thermometer is visible.", "No verified cold-heart-loss sequence.", "Native normal speed only; prerequisite stills count as explanation."],
        }
        source_doc["sources"].append(source)
        audio_doc["sources"].append({"id": entry["id"], "sourceFile": file, "sourceSha256": entry["sha256"], **copy.deepcopy(audio)})
        verified.append({"id": entry["id"], "file": file, "sha256": entry["sha256"], "probe": probe})
    write_new(PRODUCTION / "sources.json", source_doc)
    write_new(PRODUCTION / "audio-source-review.json", audio_doc)
    write_new(RESEARCH / "verified-source-probes.json", {"checkedAt": now, "sources": verified})
    print(json.dumps({"sourceCount": len(source_doc["sources"]), "sourcesSha256": sha(PRODUCTION / "sources.json"), "audioSha256": sha(PRODUCTION / "audio-source-review.json")}))


if __name__ == "__main__":
    main()
