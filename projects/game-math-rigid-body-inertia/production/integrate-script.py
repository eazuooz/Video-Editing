"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M30", "slug": "game-math-rigid-body-inertia", "edits": [{"index": 0, "mode": "replace", "ko": "비시지에서 대포를 쏘자, 차체가 뒤로 밀리면서 동시에 들려 넘어갑니다. 물체가 이동하는 것과 돌아가는 것을 함께 계산하려면 무엇이 더 필요할까요? 힘을 가하는 위치와 질량 분포를 살펴보고, 회전 속도와 토크에서 충돌, 물리 엔진의 시간 갱신까지 연결하겠습니다. 먼저 하나의 물체에 이동과 회전이 함께 있다는 사실부터 정리해 보죠.", "en": "When a cannon fires in Besiege, its vehicle moves backward and also rears up and overturns. What else is needed to calculate translation and rotation together? We will examine where forces act and how mass is distributed, then connect angular velocity and torque to collisions and a physics engine’s time update. First, separate translation from rotation on a single object.", "reason": "Observed rotation plus translation motivates torque; no actual same-force/lever-arm values inferred. The source same-force/different-point comparison remains in the following own model.", "screen": "Native Besiege176–188 then same own wheeled cannon model; distinguish measured implementation values from illustrated game overlay."}, {"index": 3, "mode": "prepend", "ko": "왕국의 눈물에서는 통나무와 돛대를 붙인 뗏목을 한 번에 들어 옮깁니다. 붙어 있는 단단한 부분들은 서로의 배치를 유지한 채 같이 움직이죠. 이런 물체의 움직임을 이동과 회전으로 나누어 보겠습니다.", "en": "In Tears of the Kingdom, a raft made from joined logs and a mast is lifted and moved as an assembly. Its connected solid parts retain their relative arrangement. Let us separate that object’s motion into translation and rotation.", "reason": "Visible assembly motivates rigid motion; exclude cloth deformation and no engine-body implementation assertion.", "screen": "Native TOTK1010–1020; mark logs/mast only, preserve water release result. Our rigid assembly then defines actual centre of mass and angular quantities."}, {"index": 27, "mode": "prepend", "ko": "비이엠엔지 드라이브의 바퀴는 차체에 연결된 채 돌고, 요철을 넘으며 위아래로 움직입니다. 연결됐다고 해서 모든 움직임이 사라지는 것은 아니죠. 이 관계를 강체 모형으로 단순화하면, 어떤 움직임을 남기고 어떤 움직임을 막을지 정해야 합니다.", "en": "In BeamNG.drive, wheels rotate while connected to the body and move vertically over bumps. Being connected does not eliminate every motion. In an ideal rigid-body model, we must decide which motions to allow and which to constrain.", "reason": "Observed connected motion motivates ideal constraints without identifying BeamNG soft-body solver as a hinge/prismatic system.", "screen": "Native second buggy55–73; visible wheel-body relation. Transition to independent joint models before assigning canonical joint names and exact freedoms."}], "bindings": [{"index": 0, "candidate": "M30-G01-recoil-rotation", "speechPrefix": "비시지에서 대포를 쏘자", "role": "Observed translation plus rotation motivates angular state and torque", "after": "Same neutral cannon/lever-arm model preserves original force-location question and derivation."}, {"index": 3, "candidate": "M30-G02-linked-assembly", "speechPrefix": "왕국의 눈물에서는 통나무와 돛대를", "role": "Joined solid parts motivate translation/rotation split", "after": "Original centre-of-mass subtraction, angular acceleration and inertia tensors retain source order."}, {"index": 27, "candidate": "M30-G03-connected-wheel-motion", "speechPrefix": "비이엠엔지 드라이브의 바퀴는", "role": "Connected motion motivates permitted degrees of freedom", "after": "Own ideal joint definitions, constraints, integration and all12 worked exercises retained."}], "screenOverrides": {}, "corrections": [{"index": 60, "koFrom": "처음에 같은 힘을 어디에 가하는지가 왜 중요했는지 이제 연결됩니다.", "koTo": "처음에 차체가 밀려가면서 동시에 돌아갔던 모습을 이제 연결할 수 있습니다. 힘을 어디에 가하는지도 중요했죠.", "enFrom": "The opening question now connects:", "enTo": "The opening vehicle’s translation and rotation now connect:", "reason": "Match observed opening while retaining source force-location conclusion."}], "aliases": {"비시지": "Besiege", "비이엠엔지 드라이브": "BeamNG.drive", "라이더스 리퍼블릭": "Riders Republic"}, "reviewNotes": ["All 61 bilingual source-faithful draft beats were authored and read during full primary lesson audit; unchanged derivations/examples/corrections remain.", "All integration changes and adjacent bridges read in Korean and English. No unseen game mechanics, exact engine algorithms or measured parameters claimed.", "Native gameplay observations, source hashes and publisher/recorder evidence are in footage-audit. Actual audio listening, continuous playback and final composite timing still pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "The Legend of Zelda: Tears of the Kingdom", "selectionReason": "Three inspected meaningful observations selected by source lesson role, 1/3 Nintendo; no ratio-padding or slow/static footage."}}')
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
