"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M24", "slug": "game-math-velocity-derivatives", "edits": [{"index": 0, "mode": "replace", "ko": "슈퍼 마리오 오디세이에서 마리오가 방을 가로질러 갔다가, 벽을 따라 다시 가운데로 돌아옵니다. 출발점과 도착점만 보면 그 사이에 얼마나, 어떻게 움직였는지 알 수 있을까요? 오늘은 위치와 시간을 같은 기준으로 기록하고, 구간 전체의 평균에서 바로 지금의 변화율로 들어가 보겠습니다. 마지막에는 길의 기울기와 이동 속도를 연결해서, 언덕 위로 얼마나 빠르게 올라가는지도 계산해 볼 거예요. 먼저 방금 움직임에서 무엇을 기록해야 하는지부터 보죠.", "en": "In Super Mario Odyssey, Mario crosses a room, follows the wall, and returns toward its middle. Can the starting and finishing positions alone tell us how far he traveled or how his motion changed? We will record position and time with consistent units, move from an interval average to the rate of change at one instant, then combine path slope and travel speed to calculate the rate of gaining height. First, let us decide what to record from the motion we just saw.", "reason": "Replace unseen forward-stop-reverse placeholder with observed Mario2480–2498. Preserve thesis and full source order; not an exactly closed loop.", "screen": "Native Mario2480–2498 with feet/path and endpoint guides after branding. Continue remaining overview into our matching grid/path model; never stretch footage or freeze to fill speech."}, {"index": 15, "mode": "prepend", "ko": "포르자 호라이즌 파이브에서 차가 출발하면, 도로 위 위치와 함께 계기판의 속력도 계속 바뀝니다. 방금 지나온 구간의 평균과, 계기판이 알려주는 지금의 빠르기는 다른 질문에 답하죠.", "en": "As a car starts in Forza Horizon 5, its position along the road and the speedometer reading keep changing. The average over the section just traveled and the displayed speed right now answer different questions.", "reason": "Observed speed readout supports motivation for instantaneous rate, without claiming internal derivative algorithm or constant acceleration.", "screen": "Native Forza5 local5–22. Brief leader to actual mph readout; do not relabel it as km/h. Transition to shrinking secant interval of the unchanged source hare example."}, {"index": 32, "mode": "prepend", "ko": "왕국의 눈물에서는 링크가 뗏목의 돛대 옆에 서 있는데도 강가의 풍경이 지나갑니다. 뗏목을 기준으로 보면 거의 제자리지만, 강가를 기준으로 보면 함께 이동하는 거죠. 이처럼 무엇을 기준으로 위치를 적는지가 중요합니다.", "en": "In Tears of the Kingdom, Link stands beside the raft’s mast while the riverbank passes by. He is nearly still relative to the raft but moving relative to the shore. The reference used to record position matters.", "reason": "Observed raft-frame relation motivates original straight train/walking example; do not claim Link walks or camera/world axes fixed.", "screen": "Native TOTK1022–1042; mark feet relative to mast and shore landmark only while visible. Transition to our straight nonrotating train/person model for original10+2m/s example."}], "screenOverrides": {"46": "Close on the same independent grid/path and position graph used after the real Mario opening. Use current derivative highlights, no duplicate replay or new unverified game cut."}, "bindings": [{"index": 0, "candidate": "M24-G01-path-displacement", "speechPrefix": "슈퍼 마리오 오디세이에서 마리오가 방을 가로질러 갔다가", "role": "Actual-game abstract: traveled route versus endpoint information", "after": "Our matching grid world introduces particle position and units; remaining overview continues over moving explanation."}, {"index": 15, "candidate": "M24-G02-changing-speed", "speechPrefix": "포르자 호라이즌 파이브에서 차가 출발하면", "role": "Actual speedometer motivates instantaneous rate rather than interval average", "after": "Return to the original hare polynomial, narrowing nonzero time intervals and tangent limit."}, {"index": 32, "candidate": "M24-G03-moving-frame", "speechPrefix": "왕국의 눈물에서는 링크가 뗏목의 돛대 옆에 서 있는데도", "role": "Relative position on moving raft motivates sum-rule train example", "after": "Our train/person scene uses aligned nonrotating axes and exactly the original10+2=12m/s worked example."}], "aliases": {"포르자 호라이즌 파이브": "Forza Horizon 5"}, "corrections": [{"index": 33, "koFrom": "퍼롱", "koTo": "펄롱", "reason": "Consistent Korean furlong spelling with prior definition."}], "reviewNotes": ["All47KO and47EN draft beats read in full. Full instructional order, examples, calculations and source mapping retained.", "Three inspected gameplay roles integrated beside the relevant explanations. No exact in-game metrics or hidden implementation inferred.", "Three bridges and heading-free flow reviewed in text; actual narration listening, native playback and rendered timing remain pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 2, "nintendoGame": "Super Mario Odyssey; The Legend of Zelda: Tears of the Kingdom", "selectionReason": "Three different required observations; lecture smallest sufficient set. Mario room path, Forza speed readout, TOTK moving reference frame; no extra title to pad count."}}')
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
