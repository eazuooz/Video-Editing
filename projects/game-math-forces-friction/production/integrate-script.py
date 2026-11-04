"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads('{"episode": "M27", "slug": "game-math-forces-friction", "edits": [{"index": 0, "mode": "replace", "ko": "비이엠엔지 드라이브에서 차가 바위를 넘으면, 바퀴가 올라가고 차체도 기울어집니다. 이런 움직임은 무엇이 만들까요? 지금 어떤 물체가 어떤 방향으로 밀고 당기는지부터 살펴봐야 합니다. 먼저 뉴턴의 법칙으로 힘을 모아 계산하고, 그 방법을 중력과 마찰에 차례로 적용하겠습니다. 마지막에는 같은 계산을 게임의 점프와 미끄러짐을 설계하는 도구로 연결해 보죠.", "en": "In BeamNG.drive, a vehicle crosses rocks: its wheels rise and its body tilts. What produces this motion? Start by identifying which objects push or pull, and in which directions. We will combine forces through Newton’s laws, apply the method to gravity and friction, then use the same calculations to design jumping and sliding in a game.", "reason": "Observed tire/contact motion replaces unseen push-and-release opening. Preserve Newton→gravity→friction order.", "screen": "Native BeamNG local35–51, wheel-ground contours with body tilt. After full crossing use same neutral vehicle/contact model; show only labelled illustrative force arrows, not measured game data."}, {"index": 12, "mode": "prepend", "ko": "비시지에서는 대포를 쏘자 포탄은 앞으로 나가고, 발사한 차체는 뒤로 들려 넘어갑니다. 서로 영향을 주는 대포와 포탄을 먼저 나누어 보면, 힘의 짝을 이해하기 쉬워집니다.", "en": "In Besiege, firing sends the shot forward while the firing vehicle rears backward and overturns. Separating the cannon and projectile helps us identify the pair of interacting forces.", "reason": "Observed recoil motivates simultaneous interaction; equal force proof and ground forces explained in own model.", "screen": "Native Besiege176–187; barrel/shot direction and body turn marks. Hand off to separate cannon/projectile free-body drawings, with gravity/ground forces shown separately."}, {"index": 18, "mode": "prepend", "ko": "왕국의 눈물에서 링크가 절벽 아래 물로 뛰어내립니다. 발밑의 지지가 사라진 뒤 아래로 내려가는 모습을 보면서, 이제 중력을 단순한 게임 월드의 식으로 옮겨 보죠.", "en": "In Tears of the Kingdom, Link dives from a ledge into the water below. As he descends after leaving ground support, let us translate gravity into a simple game-world equation.", "reason": "Concrete fall motivates gravity; dive animation and water are not treated as exact free-fall measurements.", "screen": "Native TOTK943–953, ledge→descent→splash/resurface. Guide only visible descending body, hide in splash. Continue unchanged gravity equation in fixed-axis particle model."}], "bindings": [{"index": 0, "candidate": "M27-G01-contact-traction", "speechPrefix": "비이엠엔지 드라이브에서 차가 바위를 넘으면", "role": "Contact motion motivates summing forces", "after": "Same own force-diagram stage introduces Newton laws and all original examples."}, {"index": 12, "candidate": "M27-G02-cannon-reaction", "speechPrefix": "비시지에서는 대포를 쏘자", "role": "Separate interacting objects rather than canceling forces on one object", "after": "Original action/reaction/book-table demonstration retains independent force sets."}, {"index": 18, "candidate": "M27-G03-fall-support", "speechPrefix": "왕국의 눈물에서 링크가 절벽 아래 물로", "role": "Leaving support and falling before gravity simplification", "after": "Original constant-g mass cancellation, gravity values and jump design follow without omissions."}], "screenOverrides": {}, "corrections": [], "aliases": {"비시지": "Besiege", "비이엠엔지 드라이브": "BeamNG.drive", "라이더스 리퍼블릭": "Riders Republic"}, "reviewNotes": ["All 32 bilingual source-faithful draft beats were authored and read during full primary lesson audit; unchanged derivations/examples/corrections remain.", "All integration changes and adjacent bridges read in Korean and English. No unseen game mechanics, exact engine algorithms or measured parameters claimed.", "Native gameplay observations, source hashes and publisher/recorder evidence are in footage-audit. Actual audio listening, continuous playback and final composite timing still pending."], "gameMix": {"adoptedGames": 3, "nintendoGames": 1, "nintendoGame": "The Legend of Zelda: Tears of the Kingdom", "selectionReason": "Three inspected meaningful observations selected by source lesson role, 1/3 Nintendo; no ratio-padding or slow/static footage."}}')
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
