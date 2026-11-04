"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M25", "slug": "game-math-acceleration-integration", "edits": [{"index": 0, "mode": "replace", "ko": "포르자 호라이즌 파이브에서 차가 언덕을 타고 공중으로 올라갔다가, 다시 땅에 닿습니다. 이 사이에 차의 위치와 속도는 어떻게 달라질까요? 오늘은 속도의 변화를 가속도로 읽고, 그 변화를 쌓아 위치까지 구해 보겠습니다. 이 관계를 거꾸로 풀면 원하는 높이와 시간에 맞춘 점프도 설계할 수 있어요. 먼저 눈앞의 움직임에서 위치가 아니라 속도 화살표를 따라가 보죠.", "en": "In Forza Horizon 5, a car climbs a hill, becomes airborne, then touches the ground again. How do its position and velocity change along the way? We will read velocity change as acceleration, then accumulate that change to calculate position. Solving the relationship backward also lets us design a jump for a chosen height and timing. First, follow the velocity arrow rather than position alone.", "reason": "Observed approach, takeoff, flight and landing replace unseen generic jump/corner opening. Full source learning order retained.", "screen": "Native Forza51–65: approach, takeoff60, descent61–63, landing64. Follow actual car silhouette with unmeasured velocity-direction guide only. After full action continue the abstract on matching independent ramp model, no freeze or slowdown."}, {"index": 18, "mode": "prepend", "ko": "마리오가 발판에서 뛰면, 위로 올라갔다가 내려와 다시 발판에 닿습니다. 이 움직임을 수평과 수직으로 나누어 읽어 보죠.", "en": "Mario jumps from a platform, rises, comes down, and reaches a platform again. Let us read that motion as horizontal and vertical components.", "reason": "Short complete side-view jump introduces axes; no fitted game gravity or equal-height claim.", "screen": "Native Mario1470–1479. Label Mario and platform, trace moving silhouette briefly; maintain source camera motion. At source end hand off to our static-camera jump model for vectors and formulas while narration continues."}, {"index": 21, "mode": "replace", "ko": "각도와 중력을 고정하고 초기 속력만 두 배로 올려 보죠. 수평 속도가 두 배가 되고, 수직 속도도 두 배라 공중에 머무는 시간까지 두 배가 됩니다. 두 배의 속도로 두 배 오래 가니 수평 거리는 네 배예요. 그래서 도달 거리에 속력의 제곱이 들어 있습니다. 다만 높이가 다른 곳에 착지하거나 공기 저항이 있거나 중력이 달라지면 이 단순한 네 배 관계를 그대로 적용할 수는 없습니다. 라이더스 리퍼블릭의 이 점프에서는 눈 언덕에서 떠오른 뒤 더 낮은 경사면에 내려앉습니다. 이런 경우에는 같은 높이로 돌아오는 공식 대신, 실제 착지 높이를 위치 식에 넣어 시간을 구해야 합니다.", "en": "Hold launch angle and gravity fixed and double only the initial speed. Horizontal velocity doubles, and doubled vertical velocity doubles the flight time as well. Twice the horizontal speed for twice the duration gives four times the range. That explains the squared speed in the formula. Unequal landing heights, air resistance, or changing gravity require different calculations; the simple factor of four is conditional. In this Riders Republic jump, the skier leaves a snowy rise and lands farther down the slope. Here, use the actual landing height in the position equation rather than the equal-height return formula.", "reason": "Observe actual unequal launch and landing heights as the explicit limit of the just-derived range formula.", "screen": "Keep fourfold-range worked model first. At Riders speech prefix switch to native209–219 for complete approach, flip215, landing216 and continued movement. No exact height or game gravity inferred. Return to arbitrary-direction acceleration model."}, {"index": 38, "mode": "replace", "ko": "이번에는 직선과 포물선처럼 각 축의 변화를 중심으로 살펴봤습니다. 그런데 자동차가 코너를 도는 경우처럼, 빠르기는 그대로인데 방향만 계속 바뀌는 움직임도 있죠. 속도 벡터의 변화율이라는 정의를 그대로 적용하면 그것도 가속도입니다. 다음에는 원을 도는 물체를 놓고, 왜 가속도가 중심을 향하는지와 속력·반지름·회전 속도가 어떻게 연결되는지 이어서 살펴보겠습니다.", "en": "We focused on changes along axes, using straight-line motion and parabolas. But a car corner gives another case: unchanged speed with continually changing direction. The same definition, the derivative of the velocity vector, still gives acceleration. Next we will use circular motion to see why that acceleration points inward and how speed, radius, and angular velocity connect.", "reason": "Remove false reference to an opening corner after adopting verified jump opening. Preserve next-episode circular-motion bridge.", "screen": "Continue same self-authored motion stage and bend its path into an arc. Show velocity direction changing; do not replay unrelated racing footage."}], "screenOverrides": {}, "aliases": {"포르자 호라이즌 파이브": "Forza Horizon 5", "라이더스 리퍼블릭": "Riders Republic"}, "corrections": [], "bindings": [{"index": 0, "candidate": "M25-G01-car-takeoff", "speechPrefix": "포르자 호라이즌 파이브에서 차가 언덕을 타고", "role": "Actual-game abstract: approach, flight and landing motivate changing velocity and accumulated position", "after": "Same independent ramp model keeps the actual result visible while entering one-axis acceleration."}, {"index": 18, "candidate": "M25-G02-sideview-jumps", "speechPrefix": "마리오가 발판에서 뛰면", "role": "Platform jump motivates horizontal and vertical components", "after": "Independent jump model carries full original equations; no measured game gravity."}, {"index": 21, "candidate": "M25-G03-ski-airborne", "speechPrefix": "라이더스 리퍼블릭의 이 점프에서는", "role": "Unequal landing height demonstrates the limit of the same-height range formula", "after": "Continue original arbitrary-direction projection and target-jump design."}], "reviewNotes": ["Read all39KO and39EN full draft beats, including derivations, worked examples and integral source sequence.", "Three native gameplay before/action/result roles inserted beside the corresponding explanation. No engine algorithm or numerical game parameters inferred.", "Text joins reviewed without section resets. Audio, native source playback, final annotations and timed composite remain pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "Super Mario Odyssey", "selectionReason": "Racing flight, side-view platforming and downhill sport demonstrate different observations; 1/3 Nintendo, no padding."}}')
PROJECT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

ko_path = PROJECT / "script/draft-narration.ko.json"
en_path = PROJECT / "script/draft-narration.en.json"
ko, en = load(ko_path), load(en_path)
segments, english = copy.deepcopy(ko["segments"]), copy.deepcopy(en["segments"])
assert [s["id"] for s in segments] == [s["id"] for s in english]
changes = []
for edit in CONFIG["edits"]:
    i = edit["index"]
    before, before_en = segments[i]["text"], english[i]["text"]
    segments[i]["text"] = edit["ko"] + (" " + before if edit["mode"] == "prepend" else "")
    english[i]["text"] = edit["en"] + (" " + before_en if edit["mode"] == "prepend" else "")
    segments[i]["screenPlan"] = edit["screen"]
    changes.append({"sourceBeatId":segments[i]["id"], "mode":edit["mode"],
                    "beforeKo":before, "afterKo":segments[i]["text"],
                    "beforeEn":before_en, "afterEn":english[i]["text"],
                    "reason":edit["reason"]})
for fix in CONFIG["corrections"]:
    i = fix["index"]
    before, before_en = segments[i]["text"], english[i]["text"]
    if "koFrom" in fix:
        assert fix["koFrom"] in before
        segments[i]["text"] = before.replace(fix["koFrom"], fix["koTo"])
    if "enFrom" in fix:
        assert fix["enFrom"] in before_en
        english[i]["text"] = before_en.replace(fix["enFrom"], fix["enTo"])
    changes.append({"sourceBeatId":segments[i]["id"], "mode":"readthrough-correction",
                    "beforeKo":before, "afterKo":segments[i]["text"],
                    "beforeEn":before_en, "afterEn":english[i]["text"], "reason":fix["reason"]})
for index, screen in CONFIG["screenOverrides"].items():
    segments[int(index)]["screenPlan"] = screen

def display(text):
    for a, b in CONFIG["aliases"].items():
        text = text.replace(a, b)
    return text

common = {
    "schemaVersion":1, "slug":CONFIG["slug"], "episodeId":CONFIG["episode"],
    "status":"integrated-draft-text-readthrough-complete-runtime-binding-pending",
    "isFinalNarration":False, "chapterOrderPreserved":True,
    "actualDurationSeconds":None,
    "sourceDraftSha256":sha(ko_path), "englishDraftSha256":sha(en_path),
    "speechAndVisualOverlap":True, "defaultHoldSeconds":0
}
scenes, scenes_en = [], []
for i, (s,e) in enumerate(zip(segments, english)):
    scenes.append({"id":f"{i:03d}", "sourceBeatId":s["id"], "title":s["title"],
                   "section":s["section"], "lines":[s["text"]], "displayLines":[display(s["text"])]})
    scenes_en.append({"id":f"{i:03d}", "sourceBeatId":s["id"], "title":e["title"],
                      "section":s["section"], "lines":[e["text"]]})
ko_final = PROJECT / "script/narration.ko.json"
en_final = PROJECT / "script/narration.en.json"
save(ko_final, dict(common, language="Korean", scenes=scenes))
save(en_final, dict(common, language="English", scenes=scenes_en))

footage_path = PROJECT / "planning/footage-audit.json"
footage = load(footage_path)
sources = {s["id"]:s for s in footage["sources"]}
candidates = {c["id"]:c for c in footage["candidateSegments"]}
bindings = []
for selected in CONFIG["bindings"]:
    c = candidates[selected["candidate"]]
    src = sources[c["sourceId"]]
    audio = copy.deepcopy(src.get("audio", {}))
    offset = audio.get("fullOriginalAudioOffsetForLocalVideo", 0)
    bindings.append({
        "beat":segments[selected["index"]]["id"], "sceneId":f'{selected["index"]:03d}',
        "candidate":c["id"], "sourceId":c["sourceId"], "game":src["game"],
        "sourceIn":c["sourceIn"], "sourceOut":c["sourceOut"],
        "sourceFile":src["file"], "sourceSha256":src["sha256"],
        "recordingUrl":src["recordingUrl"], "decodedSize":src["decodedSize"],
        "nativeFps":src["nativeFps"], "playbackRate":1, "hold":0,
        "loop":False, "freezePadding":False,
        "role":selected["role"], "observed":c["observed"],
        "claimLimits":c["claimLimits"], "annotationPlan":c["annotationPlan"],
        "reviewEvidence":c["reviewEvidence"],
        "nativeDecodeEvidence":c.get("nativeDecodeEvidence"),
        "speechTarget":{"prefixKo":selected["speechPrefix"],
                        "timing":"Phrase placement to follow actual PCM; speak target, action and result while visible."},
        "handoffToExplanation":selected["after"],
        "audio":audio, "fullOriginalAudioIn":c["sourceIn"]+offset,
        "fullOriginalAudioOut":c["sourceOut"]+offset,
        "status":"observed-source-bound-to-text; native playback, audio, annotation and exact timing QA pending"
    })
plan_path = PROJECT / "planning/production-plan.json"
plan = load(plan_path)
plan.update({
    "sourceFinal":True, "narrationFinal":False, "sceneBindingsFinal":False,
    "stage":"full-draft-gameplay-integration",
    "learningSteps":[{"id":s["id"],"section":s["section"],
                     "sourceParagraphs":s["sourceParagraphs"],
                     "retainedExplanation":s["text"],"screenIntent":s["screenPlan"]}
                    for s in segments],
    "teachingBeats":[{"id":s["id"],"speech":s["text"],"visual":s["screenPlan"],"hold":0,
                     "timing":"pending actual PCM and realized motion; no automatic observation silence"}
                    for s in segments],
    "nativeGameCueBindings":bindings,
    "gameMix":CONFIG["gameMix"],
    "boundaryLinks":[{"from":segments[i-1]["id"],"to":segments[i]["id"],
                      "carriedResult":re.split(r"(?<=[.!?])\s+", segments[i-1]["text"])[-1],
                      "nextOpening":re.split(r"(?<=[.!?])\s+", segments[i]["text"])[0],
                      "sourceBoundary":segments[i].get("boundaryFromPrevious"),
                      "actualGameBridge":next((b["role"] for b in bindings if b["beat"]==segments[i]["id"]),None)}
                     for i in range(1,len(segments))]
})
save(plan_path, plan)
readthrough = {
    "status":"full bilingual draft and integrated changes text-reviewed; realized audiovisual review pending",
    "source": "planning/source-audit.json",
    "beats":len(segments),"sourceOrderPreserved":True,
    "sourceParagraphMappingPreserved":True,
    "notes":CONFIG["reviewNotes"],
    "audioListeningCompleted":False, "realizedTimingReviewed":False,
    "koSha256":sha(ko_final),"enSha256":sha(en_final)
}
save(PROJECT/"planning/script-integration.json", {
    "updatedAt":datetime.now(timezone.utc).isoformat(),
    "episode":CONFIG["episode"], "sourceAudit":"planning/source-audit.json",
    "sourceAuditSha256":sha(PROJECT/"planning/source-audit.json"),
    "footageAudit":"planning/footage-audit.json","footageAuditSha256":sha(footage_path),
    "changes":changes,"readThrough":readthrough,
    "sourceFinal":True,"narrationFinal":False,"sceneBindingsFinal":False,
    "ttsStarted":False,
    "remaining":[
                 "Unity runtime and all source-beat scene bindings",
                 "Actual voice duration, phrase-to-motion synchronization and native gameplay listening",
                 "Final moving annotations and caption composite at1080p and375px"]
})
for language, rows in [("ko",scenes),("en",scenes_en)]:
    (PROJECT/f"script/integrated-readthrough.{language}.txt").write_text(
        "\n\n".join(" ".join(s["lines"]) for s in rows)+"\n",encoding="utf-8")
print(CONFIG["episode"], "integrated", len(segments), "beats;", len(bindings),
      "verified-source roles; final narration and scene-binding gates remain false.")
