"""Persist the completed manual whole-text audit; never run ASR or edit audio."""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
VOICE = PROJECT / "production/local/botw-v4/voice"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    source = VOICE / "narration-source.wav"
    asr_path = VOICE / "whole-source-asr.json"
    compare_path = VOICE / "whole-source-comparison.json"
    asr, comparison = read(asr_path), read(compare_path)
    spoken_path = PROJECT / "script/botw-v4/narration.spoken-ko.json"
    spoken_text = PROJECT / "script/botw-v4/narration.spoken-ko.txt"
    spoken = read(spoken_path)
    expected = " ".join(line for scene in spoken["scenes"] for line in scene["lines"])
    assert expected == comparison["expectedSpokenText"]
    assert re.sub(r"\s+", " ", spoken_text.read_text(encoding="utf-8-sig")).strip() == expected
    assert asr["text"] == comparison["recognized"]
    assert sha(source) == comparison["audioSha256"] == asr["audio_sha256"]
    assert sha(asr_path) == comparison["asrSha256"]
    for item in comparison["scriptInputs"]:
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert asr["completeAudioSubmitted"] and asr["noExpectedPrompt"]
    assert len(comparison["differences"]) == 6
    # Decisions below follow the direct full-text reading, not a similarity threshold.
    windows = [(4.6, 6.46), (20.14, 22.36), (116.5, 117.6),
               (117.94, 119.12), (303.52, 306.38), (319.32, 322.24)]
    decisions = [
      ("01-p01", "설원→서론", "bounded-pronunciation-or-ASR-uncertainty", "The cold-warning and snowy exploration sentence is present. The recognized place noun differs; context supports the intended 설원, but text alone cannot settle the actual pronunciation."),
      ("01-p01", "경험의→경험에", "ordinary-particle-pronunciation-or-ASR-spelling", "A common 의/에 spoken rendering; the burden-of-first-experience phrase remains intact."),
      ("03-p02", "눈앞의→눈앞에", "ordinary-particle-pronunciation-or-ASR-spelling", "The visible object and small first-action meaning remain intact; no missing teaching step indicated."),
      ("03-p02", "주워→주어", "ordinary-phonetic-or-ASR-spelling", "The full pickup clause is present and adjacent 줍는/물건 acquisition context is intact; no replacement of the action is inferred."),
      ("07-p01", "옆에서→옆", "bounded-short-syllable-uncertainty", "The entire next-button/path/action and loss-of-choice argument is recognized. The 에서 syllables are absent from the ASR string; the word timing overlaps the preceding sentence, so this is not enough to diagnose an actual audio omission."),
      ("07-p02", "어 쇼트 하이크→쇼트하이크", "bounded-title-prefix-uncertainty", "The identifiable game title and walking/climbing/gliding explanation are recognized. The initial 어/A is absent in ASR; actual audio pronunciation remains unconfirmed.")
    ]
    diffs = []
    for raw, window, (pid, label, category, decision) in zip(comparison["differences"], windows, decisions):
        words = [w for w in asr["words"] if w["timestamp"][0] is not None
                 and window[0] <= w["timestamp"][0] <= window[1]]
        diffs.append({"paragraphId": pid, "label": label, "difference": raw,
                      "classification": category, "assessment": decision,
                      "sourceSeconds": list(window), "actualAsrWords": words,
                      "audioAuditionPerformed": False})
    pending = [
      {"paragraphId": "01-p01", "sourceSeconds": [4.6, 6.46], "finalApproxSeconds": [6.6, 8.46], "check": "설원 noun vs recognized 서론"},
      {"paragraphId": "07-p01", "sourceSeconds": [303.52, 306.38], "finalApproxSeconds": [305.52, 308.38], "check": "옆에서 particle before 다음 버튼"},
      {"paragraphId": "07-p02", "sourceSeconds": [319.32, 322.24], "finalApproxSeconds": [321.32, 324.24], "check": "어/A prefix before 쇼트 하이크"}
    ]
    result = {
      "schemaVersion": 1, "slug": "kind-to-beginners", "revision": "botw-v4",
      "status": "complete-source-text-compared-bounded-audio-uncertainties-retained",
      "reviewedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "audioSha256": sha(source), "comparisonSha256": sha(compare_path), "asrSha256": sha(asr_path),
      "fullTextDirectlyCompared": True,
      "method": "Directly read all23 expected spoken paragraphs and the complete current ASR text from beginning to end; compared every teaching section, then inspected all6 normalized differences and their original word timestamps. Similarity alone was not used as approval.",
      "expectedSpokenTextFile": spoken_text.relative_to(ROOT).as_posix(),
      "expectedSpokenTextSha256": sha(spoken_text),
      "scriptInputs": comparison["scriptInputs"],
      "normalizedSimilarity": comparison["normalizedSimilarity"],
      "paragraphCount": 23,
      "sceneCoverage": [{"scene": s["id"], "paragraphsDirectlyRead": len(s["lines"]),
                         "result": "Section's teaching statements and order located in full ASR; specific short-form differences remain recorded below."}
                        for s in spoken["scenes"]],
      "notes": "The complete expected and recognized text was directly compared. Cold food/effect/warning order, pickup, explicit generic competition, menu thermometer, conditional cold-health rule, Cold Resistance, Warm Doublet, timed-food versus worn clothing, Unpacking controls, A Short Hike agency and conclusion are represented. 의/에 twice and 주워/주어 are ordinary phonetic/spelling differences. 설원/서론, 옆에서/옆 and the 어 prefix in A Short Hike remain bounded uncertainties, not confirmed mispronunciations or confirmed audio omissions. This is sufficient to proceed with source-preserving measured splitting, not a claim of exact spoken fidelity or completed listening.",
      "differences": diffs,
      "permittedNextStep": "Proceed with measured source-preserving scene alignment; do not delete, trim or regenerate speech to force agreement with ASR.",
      "nextVerification": {"method": "Use the already-planned one complete final-mix ASR in segment mode and direct text review; branding normally shifts these source positions by2seconds. Validate actual alignment before pinpointing final times.", "boundedTargets": pending, "newRecognitionRunStartedByThisReview": False},
      "actualListening": False, "actualListeningPerformed": False,
      "humanListening": "pending", "humanWholeReview": "pending",
      "originalPcmModified": False, "newAsrOrVoiceGeneration": False,
      "doesNotAssert": ["No syllable was omitted in the actual audio", "Exact pronunciation is confirmed", "A human listened to the whole recording"]
    }
    target = HERE / "source-asr-review.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"path": target.relative_to(ROOT).as_posix(), "sha256": sha(target),
                      "audioSha256": result["audioSha256"], "comparisonSha256": result["comparisonSha256"],
                      "fullTextDirectlyCompared": True, "boundedUncertainties": 3}))


if __name__ == "__main__":
    main()
