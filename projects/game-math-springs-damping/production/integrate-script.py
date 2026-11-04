"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M28", "slug": "game-math-springs-damping", "edits": [{"index": 0, "mode": "replace", "ko": "비이엠엔지 드라이브에서 울퉁불퉁한 길을 지날 때, 바퀴와 차체가 서로 다른 높이로 움직입니다. 흔들리는 물체를 제자리로 되돌리면서, 흔들림도 줄이려면 무엇이 필요할까요? 용수철의 복원력에서 시작해 감쇠를 더하고, 마지막에는 카메라나 메뉴 값을 부드럽게 따라가게 만드는 코드로 연결하겠습니다. 먼저 늘어났다가 돌아오는 움직임부터 보죠.", "en": "On a bumpy road in BeamNG.drive, the wheels and body move to different heights. What lets a displaced object return while also reducing its oscillation? We will start with a spring’s restoring force, add damping, then connect those ideas to code that smoothly tracks a camera or menu value. First, look at displacement followed by return.", "reason": "Observed suspension motivates spring/damping without claiming free-decay or exact coefficients.", "screen": "Native BeamNG5–27. Show wheel-versus-body relative travel, preserving road input; then own spring/mass model removes external forcing for exact derivation."}, {"index": 1, "mode": "prepend", "ko": "슈퍼 마리오 오디세이에서는 멍멍이를 붙잡아 뒤로 당겼다가 놓으면, 반대쪽 벽으로 튀어나갑니다. 당긴 뒤 되돌아가는 이 모습을 발판 삼아, 힘을 계산하는 용수철 모형을 만들어 보겠습니다.", "en": "In Super Mario Odyssey, a captured Chain Chomp can be pulled back and released toward a wall. Use that pull-and-return motion as a starting point for a spring model whose force we can calculate.", "reason": "Observed capture/pull/release, not a claim Nintendo uses Hooke law.", "screen": "Native Mario1228–1239 with tether/target labels; clear on cinematic. Transition to independent spring model, display rest length before formula."}, {"index": 16, "mode": "prepend", "ko": "라이더스 리퍼블릭에서는 자전거가 길을 돌아도 카메라가 뒤에서 따라오며 선수를 화면에 붙잡아 둡니다. 이런 따라가기 동작을 우리 모형에서 만든다면, 어디까지 따라갈지를 먼저 정해야겠죠.", "en": "In Riders Republic, the camera follows behind the cyclist through turns and keeps the rider in view. To build this kind of tracking in our own model, we first need to specify where it should follow.", "reason": "Actual follow behavior motivates setpoint; do not identify game controller as PD or spring.", "screen": "Native Riders770–783; contour rider, hide around780 occlusion. Own observer-camera view then shows target/setpoint/output with known values."}], "bindings": [{"index": 0, "candidate": "M28-G01-suspension", "speechPrefix": "비이엠엔지 드라이브에서 울퉁불퉁한 길을", "role": "Wheel/body motion gives the spring and damping question", "after": "Continue same independent body/spring example with rest length and free oscillation."}, {"index": 1, "candidate": "M28-G02-chomp-pull-release", "speechPrefix": "슈퍼 마리오 오디세이에서는 멍멍이를", "role": "Pull-and-release action motivates restoring force", "after": "Original Hooke law, ODE, frequency and phase preserved; no game parameter inference."}, {"index": 16, "candidate": "M28-G03-camera-setpoint", "speechPrefix": "라이더스 리퍼블릭에서는 자전거가", "role": "Tracking camera motivates a moving setpoint", "after": "Return to original setpoint, PD, state/code, semi-implicit integration and first-order filter."}], "screenOverrides": {}, "corrections": [], "aliases": {"비시지": "Besiege", "비이엠엔지 드라이브": "BeamNG.drive", "라이더스 리퍼블릭": "Riders Republic"}, "reviewNotes": ["All 25 bilingual source-faithful draft beats were authored and read during full primary lesson audit; unchanged derivations/examples/corrections remain.", "All integration changes and adjacent bridges read in Korean and English. No unseen game mechanics, exact engine algorithms or measured parameters claimed.", "Native gameplay observations, source hashes and publisher/recorder evidence are in footage-audit. Actual audio listening, continuous playback and final composite timing still pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "Super Mario Odyssey", "selectionReason": "Three inspected meaningful observations selected by source lesson role, 1/3 Nintendo; no ratio-padding or slow/static footage."}}')
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
