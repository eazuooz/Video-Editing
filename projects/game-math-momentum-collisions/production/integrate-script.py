"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M29", "slug": "game-math-momentum-collisions", "edits": [{"index": 0, "mode": "replace", "ko": "비이엠엔지 드라이브에서 달리던 차가 바위에 부딪히자, 차체가 찌그러지고 다른 방향으로 구릅니다. 충돌 전후의 움직임은 어떻게 연결할 수 있을까요? 힘이 만든 운동량 변화부터 살펴보고, 질량중심과 두 물체의 충돌 조건을 차례로 더해 보겠습니다. 복잡한 실제 충돌을 이해하기 위해, 먼저 한 방향으로 움직이는 물체의 운동량부터 계산하죠.", "en": "In BeamNG.drive, a car hits rocks, crumples, and tumbles in a different direction. How can we connect the motion before and after contact? We will begin with the momentum change produced by force, then add center of mass and two-object contact conditions. To understand the complex collision, first calculate momentum for one object moving along one direction.", "reason": "Observed impact replaces unsupported generic collision opening while preserving source progression.", "screen": "Native BeamNG24–38, complete approach/impact/tumble. Then own simple object/force graph; show deformation only as observed, no one-point elastic collision label."}, {"index": 14, "mode": "prepend", "ko": "비시지에서는 날아간 포탄이 성벽을 맞히고, 벽의 조각들이 움직이기 시작합니다. 이제 발사체 하나만 볼 것이 아니라, 부딪힌 대상까지 함께 놓고 충돌 뒤 상태를 찾아야 합니다.", "en": "In Besiege, a fired shot hits a wall and its fragments begin moving. We now need to include the struck object as well as the projectile when finding the state after contact.", "reason": "Actual target result motivates momentum accounting; subsequent two-body bullet/block worked example is explicitly own simplified model.", "screen": "Native Besiege297–305, muzzle→impact→moving fragments. Transition to labelled own bullet/block; do not assign fragment masses or equate game destruction with perfect inelastic collision."}, {"index": 18, "mode": "prepend", "ko": "슈퍼 마리오 오디세이에서는 당겨 놓은 멍멍이가 벽에 닿는 순간, 벽이 부서져 길이 열립니다. 어느 곳에 닿았는지 알아내는 일과, 그 뒤 어떤 결과를 낼지 정하는 일을 나누어 보겠습니다.", "en": "In Super Mario Odyssey, a released Chain Chomp reaches the wall, which breaks and opens a path. Separate finding where contact occurs from deciding what should happen afterward.", "reason": "Observable contact/result motivates detection versus response; no hidden algorithm claim.", "screen": "Native Mario1444–1454, aim/pull/release/wall opens. Hide contour during dust; own contact point and normal follow."}], "bindings": [{"index": 0, "candidate": "M29-G01-car-impact", "speechPrefix": "비이엠엔지 드라이브에서 달리던 차가", "role": "Actual impact motivates momentum before/after", "after": "Original impulse, force integration and momentum state follow."}, {"index": 14, "candidate": "M29-G02-cannon-wall", "speechPrefix": "비시지에서는 날아간 포탄이", "role": "Projectile and struck target motivate multi-object accounting", "after": "Original two-unknowns, bullet/block and two-dimensional car calculations remain."}, {"index": 18, "candidate": "M29-G03-chomp-contact", "speechPrefix": "슈퍼 마리오 오디세이에서는 당겨 놓은 멍멍이가", "role": "Actual contact and visible game consequence motivate two collision stages", "after": "Original manifold, contact normal, impulse/restitution and Dirac explanations preserved."}], "screenOverrides": {}, "corrections": [], "aliases": {"비시지": "Besiege", "비이엠엔지 드라이브": "BeamNG.drive", "라이더스 리퍼블릭": "Riders Republic"}, "reviewNotes": ["All 38 bilingual source-faithful draft beats were authored and read during full primary lesson audit; unchanged derivations/examples/corrections remain.", "All integration changes and adjacent bridges read in Korean and English. No unseen game mechanics, exact engine algorithms or measured parameters claimed.", "Native gameplay observations, source hashes and publisher/recorder evidence are in footage-audit. Actual audio listening, continuous playback and final composite timing still pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "Super Mario Odyssey", "selectionReason": "Three inspected meaningful observations selected by source lesson role, 1/3 Nintendo; no ratio-padding or slow/static footage."}}')
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
