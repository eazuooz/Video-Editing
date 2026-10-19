"""Prepare D21 v3's six preserved PCM ranges and five new Korean TTS groups.

    python prepare-voice-reuse.py --dry-run
    python prepare-voice-reuse.py --prepare

All three v3 scripts must have a status beginning with "locked". Dry-run
validates text/provenance and prints the proposed order; it does not load PCM,
create directories, or write files. Prepare reads the existing v2 FLOAT/24kHz
mono source, chooses nearby quiet boundaries, writes six FLOAT WAV slices,
and verifies their float32 bits after readback. It does not synthesize speech,
run ASR/FFmpeg, assemble the replacement voice, or touch shared controls.

Prepare outputs:
  production/reference-preserving-v3/voice-reuse-plan.json
  production/local/reference-preserving-v3/voice/tts-groups.json
  production/local/reference-preserving-v3/voice/reused/reused-*.wav

The final assembler must alternate R1,G1,...,R5,G5,R6 in that order, with no
implicit silence, fades, gain changes or time stretching. New TTS paths/hashes
remain pending until real generated files exist. Human join listening remains
pending even when sample-preservation and quiet-boundary checks pass.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path
import uuid


ROOT = Path(__file__).resolve().parents[4]
PRODUCTION = Path(__file__).resolve().parent
PROJECT = PRODUCTION.parents[1]
REVISION = PRODUCTION.name
SLUG = PROJECT.name
SCRIPT = PROJECT / "script" / REVISION
OLD_SCRIPT = PROJECT / "script" / "reference-preserving-v2"
LOCAL = PROJECT / "production" / "local" / REVISION
VOICE = LOCAL / "voice"
OLD_VOICE = ROOT / "shared/output/narration/player-customization/reference-preserving-v2"
OLD_PCM = OLD_VOICE / "narration-source.wav"
OLD_TIMINGS = OLD_VOICE / "source-scene-timings.json"
OLD_ASR = OLD_VOICE / "whole-source-asr.json"
PLAN_FILE = PRODUCTION / "voice-reuse-plan.json"
GROUP_FILE = VOICE / "tts-groups.json"
RATE = 24000
SOURCE_SAMPLES = 9679935
SOURCE_SHA = "9fae24f4cd9ef48032b50e723f6c83a0c5278c6ff3b721942e7e6be9357793e0"
TIMINGS_SHA = "4cbd7b632929fbefac2d6665d06b4f8d33829de52fbd89240aae595a64b247ab"
ASR_SHA = "778c943776bc209ff76d33b4499a243978850a38dccb8e952786cb5054076ef1"
LANGUAGES = ("ko", "en", "spoken-ko")
SCENE_COUNTS = (("01", 3), ("02", 5), ("03", 5), ("04", 5),
                ("05", 4), ("06", 5), ("07", 4), ("08", 4))
TARGETS = (19.04, 35.44, 49.91, 63.21, 83.13, 106.93,
           178.68, 189.09, 270.06, 284.84)
RADIUS_SECONDS = .22
QUIET_WINDOW_SECONDS = .010
RMS_LIMIT_DBFS = -60.0
PEAK_LIMIT_DBFS = -45.0
SHARED_TAILS = {
    "03-p02": {
        "text": "이렇게 얻는 것과 포기하는 것이 연결된 관계를 트레이드오프라고 합니다.",
        "asrStartSeconds": 107.2, "firstWord": "이렇게", "range": "R4",
    },
    "06-p03": {
        "text": "메뉴에서 나와 긴 이동이나 전투를 거쳐야만 차이를 알 수 있다면, 마음에 들지 않는 조합을 고칠 때마다 같은 준비를 반복해야 하죠.",
        "asrStartSeconds": 285.06, "firstWord": "메뉴에서", "range": "R6",
    },
}
GROUP_PARTS = (
    ("G1", (("01-p03", "full"), ("02-p01", "full"))),
    ("G2", (("02-p03", "full"),)),
    ("G3", (("03-p01", "full"), ("03-p02", "prefix-before-shared-tail"))),
    ("G4", (("04-p03", "full"),)),
    ("G5", (("06-p02", "full"), ("06-p03", "prefix-before-shared-tail"))),
)
REPLACED_IDS = frozenset(pid for _, parts in GROUP_PARTS for pid, _ in parts)
GROUP_COUNT = len(GROUP_PARTS)
PRESERVED_RANGE_COUNT = GROUP_COUNT + 1


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()


def receipt(path):
    path = Path(path)
    return {"path": relative(path), "sha256": sha(path),
            "bytes": path.stat().st_size}


def sample_at(seconds):
    value = Decimal(str(seconds)) * RATE
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def require_authorized():
    authorization = PRODUCTION / "authorization.json"
    control = ROOT / "shared/publishing/video-production-control.json"
    approval, policy = read(authorization), read(control)
    if (SLUG, REVISION) != ("player-customization", "reference-preserving-v3"):
        raise ValueError("This helper is scoped to D21 reference-preserving-v3")
    if approval.get("slug") != SLUG or approval.get("revision") != REVISION:
        raise ValueError("Authorization identifies a different project/revision")
    if approval.get("fullProductionAuthorized") is not True:
        raise ValueError("Current v3 production authorization is missing")
    if approval.get("driveFinalReviewAuthorized") is not True:
        raise ValueError("Current v3 Drive-review scope is missing")
    if approval.get("automaticNextVideo") is not False:
        raise ValueError("Authorization must preserve the one-video boundary")
    if set(approval.get("selectedGameTitles", [])) != {
            "Splatoon Raiders", "Animal Crossing: New Horizons",
            "The Legend of Zelda: Breath of the Wild"}:
        raise ValueError("Expected the current explicit Raiders/BOTW/ACNH title selection")
    voice = approval.get("voice", "")
    if isinstance(voice, dict):
        approved = (voice.get("provider", "").lower() == "elevenlabs"
                    and voice.get("approvedSample", "").upper() == "B")
    else:
        approved = "elevenlabs" in voice.lower() and "sample b" in voice.lower()
    if not approved:
        raise ValueError("Expected the approved ElevenLabs own voice, sample B")
    return {"authorization": receipt(authorization), "control": receipt(control),
            "observedGlobalSelection": policy.get("selectedVideo"),
            "globalControlModified": False, "foreignProcessesModified": False}


def flatten_script(document, *, require_lock, label):
    if require_lock and not str(document.get("status", "")).startswith("locked"):
        raise ValueError(f"{label}: script is not locked")
    scenes = document.get("scenes", [])
    expected = list(SCENE_COUNTS)
    actual = [(str(scene.get("id", "")), len(scene.get("lines", [])))
              for scene in scenes]
    if actual != expected:
        raise ValueError(f"{label}: expected the existing eight scenes/35 paragraphs")
    flat = {}
    for scene in scenes:
        for index, line in enumerate(scene["lines"], 1):
            if not isinstance(line, str) or not line.strip():
                raise ValueError(f"{label}: empty or non-string paragraph")
            flat[f'{scene["id"]}-p{index:02d}'] = line
    return flat


def prefix_without_tail(text, tail, label):
    if text.count(tail) != 1 or not text.endswith(tail):
        raise ValueError(f"{label}: preserve the complete shared tail exactly")
    prefix = text[:-len(tail)].rstrip()
    if not prefix or prefix[-1] not in ".?!…":
        raise ValueError(f"{label}: new prefix must end as a complete sentence")
    return prefix


def validate_inputs():
    authorization = require_authorized()
    old, new, script_receipts = {}, {}, []
    for language in LANGUAGES:
        old_path = OLD_SCRIPT / f"narration.{language}.json"
        new_path = SCRIPT / f"narration.{language}.json"
        old[language] = flatten_script(read(old_path), require_lock=False,
                                      label=relative(old_path))
        new[language] = flatten_script(read(new_path), require_lock=True,
                                      label=relative(new_path))
        script_receipts += [
            {"role": f"old-{language}", **receipt(old_path)},
            {"role": f"locked-new-{language}", **receipt(new_path)},
        ]
        unexpected = [pid for pid in old[language]
                      if pid not in REPLACED_IDS
                      and old[language][pid] != new[language][pid]]
        if unexpected:
            raise ValueError(f"{language}: unexpected changes in preserved paragraphs "
                             f"{unexpected}; repair scripts or explicitly revise this map")
    # 02-p02 remains the general attack-pattern explanation. BOTW04-p01 is
    # restored exactly to its v2 wording, so its PCM also remains unchanged.
    for language in LANGUAGES:
        for pid in ("02-p02", "04-p01"):
            if old[language][pid] != new[language][pid]:
                raise ValueError(f"{language}: {pid} must remain exactly unchanged")
    for pid, shared in SHARED_TAILS.items():
        for language in ("ko", "spoken-ko"):
            prefix_without_tail(old[language][pid], shared["text"],
                                f"old {language}/{pid}")
            prefix_without_tail(new[language][pid], shared["text"],
                                f"new {language}/{pid}")
    if sha(OLD_TIMINGS) != TIMINGS_SHA or sha(OLD_ASR) != ASR_SHA:
        raise ValueError("Existing v2 timing/ASR hashes changed; do not infer a new map")
    timings, asr = read(OLD_TIMINGS), read(OLD_ASR)
    if timings.get("sourceSha256") != SOURCE_SHA or asr.get("audio_sha256") != SOURCE_SHA:
        raise ValueError("Timing/ASR does not identify the approved v2 PCM")
    if timings.get("sampleRate") != RATE:
        raise ValueError("Expected original 24kHz timing units")
    nominal_paragraphs = {}
    for scene in timings["scenes"]:
        for paragraph in scene["paragraphs"]:
            pid = f'{scene["id"]}-p{paragraph["paragraph"]:02d}'
            for language, field in (("ko", "text"), ("en", "english"),
                                    ("spoken-ko", "spokenText")):
                if paragraph[field] != old[language][pid]:
                    raise ValueError(f"Old script/timing text mismatch: {language}/{pid}")
            origin = scene["sourceOrigin"]
            nominal_paragraphs[pid] = {
                "sourceStart": origin + paragraph["start"],
                "sourceEnd": origin + paragraph["end"],
            }
    if len(nominal_paragraphs) != 35:
        raise ValueError("Existing timing must map all35 paragraphs")
    anchors = {}
    for pid, shared in SHARED_TAILS.items():
        matches = [word for word in asr["words"]
                   if abs(word["timestamp"][0] - shared["asrStartSeconds"]) < 1e-7
                   and word["text"].strip().startswith(shared["firstWord"])]
        if len(matches) != 1:
            raise ValueError(f"{pid}: existing shared-tail ASR anchor is not unique")
        anchors[pid] = matches[0]
    groups = []
    for group_id, parts in GROUP_PARTS:
        entries = []
        for pid, portion in parts:
            display, spoken = new["ko"][pid], new["spoken-ko"][pid]
            if portion == "prefix-before-shared-tail":
                tail = SHARED_TAILS[pid]["text"]
                display = prefix_without_tail(display, tail, f"ko/{pid}")
                spoken = prefix_without_tail(spoken, tail, f"spoken-ko/{pid}")
            entries.append({
                "paragraphId": pid, "portion": portion,
                "displayKo": display, "spokenKo": spoken,
                "englishFullParagraphReference": new["en"][pid],
                "englishReferenceIsNotSynthesizedOrClaimedAsThisPartialSpan":
                    portion != "full",
            })
        groups.append({
            "id": group_id, "parts": entries,
            "text": "\n\n".join(item["spokenKo"] for item in entries),
            "displayKo": "\n\n".join(item["displayKo"] for item in entries),
            "status": "pending-real-ElevenLabs-sample-B-generation",
            "generatedAudio": None, "generatedAudioSha256": None,
        })
    unchanged = [pid for pid in old["ko"] if pid not in REPLACED_IDS]
    boundary_settings = {
        "targetsSeconds": list(TARGETS), "radiusSeconds": RADIUS_SECONDS,
        "windowSeconds": QUIET_WINDOW_SECONDS, "rmsLimitDbfs": RMS_LIMIT_DBFS,
        "peakLimitDbfs": PEAK_LIMIT_DBFS,
        "selection": "quiet zero-crossing candidates first, then nearest target; "
                     "not minimum-amplitude endpoint selection",
    }
    inputs = {
        "scriptReceipts": script_receipts, "oldTimings": receipt(OLD_TIMINGS),
        "oldAsr": receipt(OLD_ASR), "sourcePcm": {
            "path": relative(OLD_PCM), "expectedSha256": SOURCE_SHA,
            "expectedSamples": SOURCE_SAMPLES, "sampleRate": RATE,
            "sha256Verified": False,
        },
        "helper": receipt(Path(__file__)), "boundarySettings": boundary_settings,
    }
    return {
        "inputSignature": canonical_hash(inputs), "inputs": inputs,
        "authorization": authorization, "groups": groups,
        "unchangedParagraphIds": unchanged,
        "replacementParagraphIds": sorted(REPLACED_IDS),
        "sharedTails": {pid: {**shared, "existingAsrAnchor": anchors[pid]}
                        for pid, shared in SHARED_TAILS.items()},
        "paragraphTimings": nominal_paragraphs, "asrWords": asr["words"],
        "unchangedCountExplanation":
            "The explicitly specified five groups contain eight replacement "
            "paragraphs, so35 minus8 equals27 completely unchanged paragraphs, "
            "plus two retained tails inside changed paragraphs.",
    }


def dbfs(value):
    return 20 * math.log10(value) if value > 0 else -300.0


def choose_quiet_boundary(pcm, target):
    """Choose a local quiet crossing by distance, not by an endpoint minimum."""
    import numpy as np
    target_sample = sample_at(target)
    half = sample_at(QUIET_WINDOW_SECONDS) // 2
    radius = sample_at(RADIUS_SECONDS)
    left = max(half, target_sample - radius)
    right = min(len(pcm) - half - 1, target_sample + radius)
    rms_limit, peak_limit = 10 ** (RMS_LIMIT_DBFS / 20), 10 ** (PEAK_LIMIT_DBFS / 20)
    candidates = []
    for index in range(left, right + 1):
        window = pcm[index - half:index + half]
        rms = float(np.sqrt(np.mean(np.square(window, dtype=np.float64))))
        peak = float(np.max(np.abs(window)))
        if rms <= rms_limit and peak <= peak_limit:
            a, b = float(pcm[index - 1]), float(pcm[index])
            crossing = a == 0 or b == 0 or (a < 0) != (b < 0)
            candidates.append((index, rms, peak, crossing, abs(a) + abs(b)))
    if not candidates:
        raise ValueError(f"No10ms quiet boundary within ±{RADIUS_SECONDS}s of"
                         f"{target}s; do not silently use a louder/remote minimum")
    crossings = [candidate for candidate in candidates if candidate[3]]
    eligible = crossings or candidates
    index, rms, peak, crossing, _ = min(
        eligible, key=lambda candidate: (
            abs(candidate[0] - target_sample), candidate[4],
            candidate[1], candidate[0]))
    return {
        "targetSeconds": target, "targetSample": target_sample,
        "sample": index, "seconds": index / RATE,
        "offsetSamples": index - target_sample,
        "offsetSeconds": (index - target_sample) / RATE,
        "windowStartSample": index - half, "windowEndSampleExclusive": index + half,
        "rmsDbfs": dbfs(rms), "peakDbfs": dbfs(peak),
        "zeroCrossing": crossing, "quietCandidateCount": len(candidates),
        "quietZeroCrossingCandidateCount": len(crossings),
        "selection": "nearest quiet zero crossing" if crossing
                     else "nearest quiet sample; no crossing existed among quiet candidates",
        "sampleBefore": float(pcm[index - 1]), "sampleAfter": float(pcm[index]),
        "listening": "pending; quiet measurements are not perceptual approval",
    }


def words_near(words, seconds):
    return [word for word in words
            if word["timestamp"][1] >= seconds - .5
            and word["timestamp"][0] <= seconds + .5]


def write_new_or_identical_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"Preserve incompatible existing output: {relative(path)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def dry_run(state):
    nominal = [0.0, *TARGETS, SOURCE_SAMPLES / RATE]
    return {
        "status": "dry-run; no PCM loaded, directories created, or files written",
        "inputSignature": state["inputSignature"],
        "lockedScriptsValidated": True,
        "inputs": state["inputs"],
        "unchangedParagraphIds": state["unchangedParagraphIds"],
        "unchangedCountExplanation": state["unchangedCountExplanation"],
        "newTtsGroups": state["groups"],
        "nominalPreservedRanges": [[nominal[i], nominal[i + 1]]
                                    for i in range(0, len(nominal)-1, 2)],
        "assemblyOrder": [item for index in range(1, GROUP_COUNT+1)
                          for item in (f"R{index}", f"G{index}")]
                         + [f"R{PRESERVED_RANGE_COUNT}"],
        "quietSampleSelection": "pending actual prepare; nominal targets are not chosen cuts",
        "sourcePcmSha256Verification": "pending actual prepare",
    }


def prepare(state):
    import numpy as np
    import soundfile as sf
    # Verify the live source even when reusing a previous preparation receipt.
    # The input signature describes pinned requirements, not a mutable claim
    # that the source was already rehashed during a dry-run.
    if sha(OLD_PCM) != SOURCE_SHA:
        raise ValueError("Original v2 narration PCM no longer matches its pinned SHA256")
    source_verification = {
        "actualSha256": SOURCE_SHA, "sha256Verified": True,
        "actualBytes": OLD_PCM.stat().st_size,
    }
    if PLAN_FILE.exists():
        previous = read(PLAN_FILE)
        if previous.get("inputSignature") != state["inputSignature"]:
            raise ValueError("Existing v3 voice-reuse-plan has different locked inputs; "
                             "preserve/archive it before preparing a different revision")
        for item in previous["preservedRanges"]:
            path = ROOT / item["output"]["path"]
            if not path.is_file() or sha(path) != item["output"]["sha256"]:
                raise ValueError("Existing preserved output changed; do not overwrite it")
        if not GROUP_FILE.exists() or sha(GROUP_FILE) != previous["ttsGroups"]["sha256"]:
            raise ValueError("Existing TTS group text changed; preserve and review it")
        return {"status": "cached-identical-prepared-plan", **receipt(PLAN_FILE)}
    info = sf.info(OLD_PCM)
    if (info.samplerate, info.channels, info.frames, info.subtype) != (
            RATE, 1, SOURCE_SAMPLES, "FLOAT"):
        raise ValueError("Expected exactly9679935 mono FLOAT samples at24kHz")
    pcm, rate = sf.read(OLD_PCM, dtype="float32", always_2d=False)
    if rate != RATE or pcm.ndim != 1 or not np.all(np.isfinite(pcm)):
        raise ValueError("Original PCM must be finite mono float32 at24kHz")
    boundaries = [choose_quiet_boundary(pcm, target) for target in TARGETS]
    cuts = [0, *(item["sample"] for item in boundaries), len(pcm)]
    if any(a >= b for a, b in zip(cuts, cuts[1:])):
        raise ValueError("Quiet boundaries changed the intended range ordering")
    for boundary in boundaries:
        boundary["existingAsrWordsNearby"] = words_near(
            state["asrWords"], boundary["seconds"])
        boundary["asrWordsCrossingCut"] = [
            word for word in boundary["existingAsrWordsNearby"]
            if word["timestamp"][0] < boundary["seconds"] < word["timestamp"][1]]
        boundary["asrTimingMeaning"] = (
            "ASR intervals may include quiet tails. A crossing is reported, not "
            "silently treated as proof of clipped audible speech or ignored.")
    for pid, shared in state["sharedTails"].items():
        range_number = int(shared["range"][1:])
        selected = cuts[2*(range_number-1)]
        if selected > sample_at(shared["asrStartSeconds"]):
            raise ValueError(f"{pid}: chosen boundary would lose the shared-tail start")
    preserved = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts)-1, 2)]
    replaced = [(cuts[i], cuts[i + 1]) for i in range(1, len(cuts)-1, 2)]
    if len(preserved) != PRESERVED_RANGE_COUNT or len(replaced) != GROUP_COUNT:
        raise ValueError("Boundary count must match six preserved ranges/five new groups")
    if sum(b - a for a, b in preserved + replaced) != len(pcm):
        raise ValueError("Original sample partition has lost or duplicated indices")
    kept_ids = state["unchangedParagraphIds"]
    range_entries, before_hash, after_hash = [], hashlib.sha256(), hashlib.sha256()
    VOICE.joinpath("reused").mkdir(parents=True, exist_ok=True)
    for number, (start, end) in enumerate(preserved, 1):
        # Re-read the scope before each media write without changing it.
        current = require_authorized()
        if current["authorization"]["sha256"] != state["authorization"]["authorization"]["sha256"]:
            raise ValueError("Production authorization changed during prepare")
        target = VOICE / "reused" / f"reused-R{number}-{start:09d}-{end:09d}.wav"
        target.resolve().relative_to(LOCAL.resolve())
        expected = np.ascontiguousarray(pcm[start:end])
        expected_bits = expected.view(np.uint32)
        if not target.exists():
            temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.wav")
            sf.write(temporary, expected, RATE, subtype="FLOAT", format="WAV")
            check, check_rate = sf.read(temporary, dtype="float32")
            if check_rate != RATE or not np.array_equal(check.view(np.uint32), expected_bits):
                temporary.unlink(missing_ok=True)
                raise ValueError("FLOAT output readback changed preserved sample bits")
            temporary.replace(target)
        actual, actual_rate = sf.read(target, dtype="float32")
        if actual_rate != RATE or actual.shape != expected.shape:
            raise ValueError(f"Existing preserved file shape changed: {relative(target)}")
        if not np.array_equal(actual.view(np.uint32), expected_bits):
            raise ValueError(f"Preserved float32 bits changed: {relative(target)}")
        source_bytes, output_bytes = expected.tobytes(), actual.tobytes()
        before_hash.update(source_bytes)
        after_hash.update(output_bytes)
        paragraphs = []
        for pid in kept_ids:
            timing = state["paragraphTimings"][pid]
            middle = (timing["sourceStart"] + timing["sourceEnd"]) / 2
            if start / RATE <= middle < end / RATE:
                paragraphs.append({
                    "id": pid, **timing,
                    "nominalAsrSpanInsideSelectedRange":
                        start <= sample_at(timing["sourceStart"])
                        and sample_at(timing["sourceEnd"]) <= end,
                })
        tails = [pid for pid, item in state["sharedTails"].items()
                 if item["range"] == f"R{number}"]
        range_entries.append({
            "id": f"R{number}", "sourceStartSample": start,
            "sourceEndSampleExclusive": end, "sourceStartSeconds": start / RATE,
            "sourceEndSeconds": end / RATE, "samples": end - start,
            "output": receipt(target),
            "sourceSlicePcmSha256": hashlib.sha256(source_bytes).hexdigest(),
            "outputPcmSha256": hashlib.sha256(output_bytes).hexdigest(),
            "bitExactFloat32Readback": True, "maximumAbsoluteError": 0.0,
            "selectedRangeLostSamples": 0, "selectedRangeDuplicatedSamples": 0,
            "retainedFullParagraphs": paragraphs, "retainedSharedTails": tails,
            "gainAppliedDb": 0.0, "fadeApplied": False, "timeStretchApplied": False,
        })
    assigned = [item["id"] for entry in range_entries
                for item in entry["retainedFullParagraphs"]]
    if sorted(assigned) != sorted(kept_ids) or len(assigned) != len(set(assigned)):
        raise ValueError("Unchanged paragraph mapping was lost or duplicated")
    if before_hash.hexdigest() != after_hash.hexdigest():
        raise ValueError("Ordered preserved PCM readback changed")
    tts = {
        "schemaVersion": 1, "slug": SLUG, "revision": REVISION,
        "inputSignature": state["inputSignature"],
        "voice": "Existing user-approved ElevenLabs own cloned voice, sample B",
        "language": "ko", "groupCount": GROUP_COUNT, "groups": state["groups"],
        "sharedTailsExcludedFromNewTts": state["sharedTails"],
        "generationPerformed": False, "asrPerformed": False,
    }
    write_new_or_identical_json(GROUP_FILE, tts)
    assembly_order = []
    for number, entry in enumerate(range_entries, 1):
        assembly_order.append({
            "id": entry["id"], "kind": "preserved-original-pcm",
            "path": entry["output"]["path"], "sha256": entry["output"]["sha256"],
        })
        if number <= GROUP_COUNT:
            assembly_order.append({"id": f"G{number}", "kind": "new-tts-pending",
                                   "path": None, "sha256": None})
    plan = {
        "schemaVersion": 1, "slug": SLUG, "revision": REVISION,
        "status": "prepared-six-exact-pcm-ranges-five-tts-text-groups",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "inputSignature": state["inputSignature"], "inputs": state["inputs"],
        "sourcePcmVerification": source_verification,
        "authorization": state["authorization"],
        "timeBasis": "Original narration-source.wav starts at0; branding2s is not included",
        "sampleRate": RATE, "sourceSamples": len(pcm), "sourceDurationSeconds": len(pcm) / RATE,
        "unchangedParagraphIds": kept_ids,
        "completelyUnchangedParagraphCount": len(kept_ids),
        "countExplanation": state["unchangedCountExplanation"],
        "replacementParagraphIds": state["replacementParagraphIds"],
        "sharedTails": state["sharedTails"], "boundaries": boundaries,
        "preservedRanges": range_entries,
        "removedOldReplacementRanges": [
            {"sourceStartSample": a, "sourceEndSampleExclusive": b,
             "samples": b - a} for a, b in replaced],
        "orderedSelectedRangePcmSha256Before": before_hash.hexdigest(),
        "orderedSelectedRangePcmSha256After": after_hash.hexdigest(),
        "preservationClaimScope": "Only the six selected original ranges have0lost/"
                                  "0duplicated samples and bit-exact readback. "
                                  "The five replaced old ranges are intentionally excluded.",
        "ttsGroups": receipt(GROUP_FILE), "assemblyOrder": assembly_order,
        "rawManifestInstructions": {
            "sources": "Resolve assemblyOrder with real generated files and actual SHA256s",
            "joinSilenceSeconds": 0.0, "sourceOrderMustMatchAssemblyOrder": True,
            "implicitFadeGainOrTimeStretch": False,
            "doNotConcatenateWithDefaultPointTwoSecondGaps": True,
        },
        "continuousPreservedSharedConnections": [
            "R4 retains03-p02 shared trade-off tail,03-p03/p04/p05 and unchanged BOTW04-p01/p02 in one old range",
            "R6 retains06-p03 shared menu/travel tail and all remaining old voice in one range",
        ],
        "humanBoundaryListening": "pending; measurements and ASR are not listening",
        "newGenerationPerformed": False, "newAsrPerformed": False,
        "finalAssemblyPerformed": False, "globalOrForeignChanges": False,
    }
    write_new_or_identical_json(PLAN_FILE, plan)
    return {"status": plan["status"], "plan": receipt(PLAN_FILE),
            "ttsGroups": receipt(GROUP_FILE), "preservedFiles": len(range_entries),
            "preservedSamples": sum(end - start for start, end in preserved),
            "humanBoundaryListening": "pending"}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="Validate locked scripts and print planned text/order; write nothing")
    mode.add_argument("--prepare", action="store_true",
                      help="Select quiet cuts and write six exact FLOAT WAVs plus two manifests")
    args = parser.parse_args()
    try:
        state = validate_inputs()
        result = dry_run(state) if args.dry_run else prepare(state)
    except (ValueError, FileNotFoundError, KeyError, OSError) as exc:
        parser.exit(2, f"Voice reuse preparation stopped: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
