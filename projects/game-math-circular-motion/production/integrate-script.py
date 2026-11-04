"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M26", "slug": "game-math-circular-motion", "edits": [{"index": 0, "mode": "replace", "ko": "포르자 호라이즌 파이브에서 차가 커브를 돌 때, 속도계의 숫자뿐 아니라 나아가는 방향도 바뀝니다. 그렇다면 빠르기를 그대로 유지하고 방향만 바꾸어도 가속도가 생길까요? 길을 원으로 단순화해 그 이유를 보고, 속력과 반지름의 관계를 구한 뒤, 삼차원 회전축으로 넓혀 보겠습니다. 마지막에는 단위와 미적분을 실제 숫자 문제에 연결하겠습니다. 먼저 원 위를 일정한 빠르기로 움직이는 한 점을 만들어 보죠.", "en": "When a car takes a bend in Forza Horizon 5, both its speedometer reading and its travel direction change. Would changing only direction still produce acceleration if speed stayed constant? We will simplify the path to a circle, relate speed to radius, then extend the picture to a three-dimensional rotation axis. Finally, worked problems connect units and calculus. First, model one point moving around a circle at constant speed.", "reason": "Verified corner changes both speed and direction; isolate constant speed explicitly in our model rather than falsely label gameplay uniform circular motion.", "screen": "Native Forza35–46, show full approach/turn/exit and actual readout. Transition without freeze to matching top-down circular track and constant-speed point for remaining overview."}, {"index": 11, "mode": "prepend", "ko": "왕국의 눈물에서는 울트라핸드로 돛을 집어 들고, 누워 있던 돛대를 세워 뗏목에 붙입니다. 어느 쪽 축으로 돌리는지가 물체의 자세를 바꾸죠.", "en": "In Tears of the Kingdom, Ultrahand lifts a sail, turns its mast upright, and attaches it to a raft. The chosen rotation axis changes the object’s orientation.", "reason": "Hands-on rotation/placement supports axis concept without claiming constant rate.", "screen": "Native TOTK998–1009; sail/mast contour and curved guide match actual turn, clear at attachment flash. Then preserve source right-handed axis explanation in our model."}, {"index": 17, "mode": "prepend", "ko": "비시지의 풍차에서는 중심 가까운 부분과 날개 끝이 함께 돕니다. 중심에서 얼마나 떨어졌는지에 따라 한 바퀴 동안 지나가는 길이는 달라지죠.", "en": "On a windmill in Besiege, the portion near the hub and the blade tip turn together. Their distances from the hub determine how far each travels around a turn.", "reason": "Visible rotating blade motivates point-speed relation, no measured game angular velocity or engine implementation.", "screen": "Native Besiege338–348, keep rotor visible as camera approaches. Brief leaders to hub and tip, no invented physical numbers; switch to same rigid-rotor model for exact r/omega relationship."}, {"index": 39, "mode": "replace", "ko": "처음 커브를 도는 차에서 방향이 바뀌는 것을 보았습니다. 이를 일정한 속력의 원운동으로 단순화하니, 속도 벡터 변화의 극한이 중심을 향하는 가속도가 되었죠. 닮은 삼각형과 미분으로 같은 결과를 얻었고, 각속도와 외적으로 삼차원까지 넓혔습니다. 연습문제에서는 단위를 맞추고, 위치를 구간별로 읽고, 미분과 적분으로 속도와 도착 시간을 연결했습니다. 중요한 것은 공식을 먼저 고르는 것보다 어떤 물체, 어떤 기준점, 어떤 시간과 단위를 계산하는지 분명히 정하는 것입니다. 그 위에서 식과 화면의 움직임이 같은 이야기를 하게 됩니다.", "en": "The opening car changed travel direction. Simplifying this to constant-speed circular motion made the velocity vector’s derivative point inward. Similar triangles and differentiation gave the same acceleration, and angular velocity with cross products extended it to three dimensions. The problems connected units, piecewise position, derivatives, accumulation, and arrival times. Before choosing a formula, identify the object, reference point, time, and units. Then the equations and visible motion can describe the same event.", "reason": "Closing refers to observed car then explicit uniform-circle model; retain source conclusion.", "screen": "Close on same own circular track/rotor and formulas; no duplicate raw footage."}], "screenOverrides": {}, "aliases": {"포르자 호라이즌 파이브": "Forza Horizon 5", "비시지": "Besiege"}, "corrections": [], "bindings": [{"index": 0, "candidate": "M26-G01-corner-direction", "speechPrefix": "포르자 호라이즌 파이브에서 차가 커브를 돌 때", "role": "Actual corner motivates changing velocity direction; exact uniform circular motion in model", "after": "Simplify to circular constant-speed point; preserve full similar-triangle limit."}, {"index": 11, "candidate": "M26-G02-object-axis", "speechPrefix": "왕국의 눈물에서는 울트라핸드로 돛을", "role": "Object manipulation reveals choice of rotation axis", "after": "Same own sail/rotor and canonical right-hand axes carry angular vector and cross product."}, {"index": 17, "candidate": "M26-G03-rigid-points", "speechPrefix": "비시지의 풍차에서는", "role": "Rotor hub versus tip motivates one angular velocity and differing point speeds", "after": "Own rotor gives exact distances and velocities, then all original worked exercises."}], "reviewNotes": ["Read all40KO and40EN full draft beats, including every worked problem. Source order, definitions, derivations and correction mapping preserved.", "Gameplay does not establish uniform speed or internal force/integration algorithms. Same-speed assumptions introduced only in the explicit model.", "KO/EN full text and joins reviewed; actual audio, native playback, timing and composite not approved."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "The Legend of Zelda: Tears of the Kingdom", "selectionReason": "Racing corner, object rotation/placement and construction-sandbox rotor; 1/3 Nintendo."}}')
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
